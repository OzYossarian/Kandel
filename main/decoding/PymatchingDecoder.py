from typing import Callable, List
import stim
import networkx as nx
import pymatching
import numpy as np
import math


class PymatchingDecoder():
    def __init__(self, detector_error_model: stim.DetectorErrorModel):
        """most of this code is taken from
        https: // github.com/Strilanc/honeycomb-boundaries/blob/main/src/hcb/tools/analysis/decoding.py

        Doesn't work for codes where an error leads to more than 2 symptoms"""

        self.detector_error_model = detector_error_model
        matching_graph = self.detector_error_model_to_nx_graph()
#        print(matching_graph, 'm graph')
        self.matcher = self.nx_graph_to_pymatching_graph(matching_graph)
#        print(self.matcher, 'matcher')

    def eval_model(
            self,
            handle_error: Callable[[float, List[int], List[int]], None],
            handle_detector_coords: Callable[[int, np.ndarray], None]):
        """Interprets the error model instructions, taking care of loops and shifts.

        Makes callbacks as error mechanisms are declared, and also when detector
        coordinate data is declared.
        """
        det_offset = 0
        coords_offset = np.zeros(100, dtype=np.float64)

        def _helper(m: stim.DetectorErrorModel, reps: int):
            nonlocal det_offset
            nonlocal coords_offset
            for _ in range(reps):
                for instruction in m:
                    if isinstance(instruction, stim.DemRepeatBlock):
                        _helper(instruction.body_copy(),
                                instruction.repeat_count)
                    elif isinstance(instruction, stim.DemInstruction):
                        if instruction.type == "error":
                            dets: List[int] = []
                            frames: List[int] = []
                            t: stim.DemTarget
                            p = instruction.args_copy()[0]
                            for t in instruction.targets_copy():
                                if t.is_relative_detector_id():
                                    dets.append(t.val + det_offset)
                                elif t.is_logical_observable_id():
                                    frames.append(t.val)
                                elif t.is_separator():
                                    # Treat each component of a decomposed error as an independent error.
                                    # (Ideally we could configure some sort of correlated analysis; oh well.)
                                    handle_error(p, dets, frames)
                                    frames = []
                                    dets = []
                            # Handle last component.
                            handle_error(p, dets, frames)
                        elif instruction.type == "shift_detectors":
                            det_offset += instruction.targets_copy()[0]
                            a = np.array(instruction.args_copy())
                            coords_offset[:len(a)] += a
                        elif instruction.type == "detector":
                            a = np.array(instruction.args_copy())
                            for t in instruction.targets_copy():
                                handle_detector_coords(
                                    t.val + det_offset, a + coords_offset[:len(a)])
                        elif instruction.type == "logical_observable":
                            pass
                        else:
                            raise NotImplementedError()
                    else:
                        raise NotImplementedError()
        _helper(self.detector_error_model, 1)

    def detector_error_model_to_nx_graph(self) -> nx.Graph:
        """Convert a stim error model into a NetworkX graph."""

        g = nx.Graph()
        boundary_node = self.detector_error_model.num_detectors
        g.add_node(boundary_node, is_boundary=True, coords=[-1, -1, -1])

        def handle_error(p: float, dets: List[int], frame_changes: List[int]):
            if p == 0:
                return
            if len(dets) == 0:
                print('here?')
                # No symptoms for this error.
                # Code probably has distance 1.
                # Accept it and keep going, though of course decoding will probably perform terribly.
                return
            if len(dets) == 1:
                dets = [dets[0], boundary_node]
            if len(dets) > 2:
                raise NotImplementedError(
                    f"Error with more than 2 symptoms can't become an edge or boundary edge: {dets!r}.")
            if g.has_edge(*dets):
                edge_data = g.get_edge_data(*dets)
                old_p = edge_data["error_probability"]
                old_frame_changes = edge_data["qubit_id"]
                # If frame changes differ, the code has distance 2; just keep whichever was first.
                if set(old_frame_changes) == set(frame_changes):
                    p = p * (1 - old_p) + old_p * (1 - p)
                    g.remove_edge(*dets)
            g.add_edge(*dets, weight=math.log((1 - p) / p),
                       qubit_id=frame_changes, error_probability=p)

        def handle_detector_coords(detector: int, coords: np.ndarray):
            g.add_node(detector, coords=coords)

        self.eval_model(handle_error, handle_detector_coords)
        return g

    def nx_graph_to_pymatching_graph(self, graph: nx.Graph) -> pymatching.Matching:
        """Convert an nx graph into a pymatching graph."""
        num_detectors = self.detector_error_model.num_detectors
        num_observables = 1
        # Add spandrels to the graph to ensure pymatching will accept it.
        # - Make sure there's only one connected component.
        # - Make sure no detector nodes are skipped.
        # - Make sure no observable nodes are skipped.
        for k in range(num_detectors):
            graph.add_node(k)
        graph.add_node(num_detectors + 1)
        for k in range(num_detectors + 1):
            graph.add_edge(k, num_detectors + 1, weight=9999999999)
        graph.add_edge(num_detectors, num_detectors + 1, weight=9999999999,
                       qubit_id=list(range(num_observables)))
        return pymatching.Matching(graph)

    def decode_samples(self, samples):
        num_shots = samples.shape[0]
        num_dets = self.detector_error_model.num_detectors
        num_obs = self.detector_error_model.num_observables
        predictions = np.zeros(shape=(num_shots, num_obs), dtype=np.bool8)
        for k in range(num_shots):
            expanded_det = np.resize(samples[k], num_dets + 1)
            expanded_det[-1] = 0
            predictions[k] = self.matcher.decode(
                expanded_det, num_neighbours=20, )

        return predictions
