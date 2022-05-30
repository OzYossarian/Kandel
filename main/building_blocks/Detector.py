from collections import defaultdict
from functools import reduce
from typing import List, Tuple

from main.building_blocks.Check import Check
from main.building_blocks.PauliWord import PauliWord
from main.utils.DebugFriendly import DebugFriendly


class Detector(DebugFriendly):
    def __init__(
            self, floor: List[Tuple[int, Check]],
            lid: List[Tuple[int, Check]]):
        """If we learn the value of the same stabilizer at two different
        timesteps, and the stabilizer remained stabilized in this interval,
        then we can multiply together the two values to detect whether an
        error occurred in this interval. This is what a Detector represents:
        its floor is the set of checks multiplied together to tell us the
        value of the stabilizer the first time around, then the lid is the
        set of checks multiplied together to tell us the value of the
        stabilizer the second time around.
        """
        self.floor = floor
        self.lid = lid
        # Note down which checks 'trigger' this detector (i.e. are the last
        # things measured before this detector can be learned)
        self.triggers = set()
        # When compiling, note which triggers have actually been measured -
        # when they've all been measured, we can build the detector.
        self.triggers_measured = set()

        def get_stabilizer(face: List[Tuple[int, Check]]):
            # Pauli multiplication is not commutative so order matters.
            face = sorted(face, key=lambda check: check[0])
            checks = [check for (_, check) in face]
            paulis = [pauli for check in checks for pauli in check.paulis]
            # Sort these paulis into qubit order so that comparison between
            # lid and floor in a minute is valid.
            paulis = sorted(paulis, key=lambda pauli: pauli.qubit.coords)
            # Group by the qubit that the Paulis are applied to
            pauli_letters = defaultdict(list)
            for pauli in paulis:
                pauli_letters[pauli.qubit].append(pauli.letter)
            # Multiply together the Paulis on each qubit.
            products = [
                reduce(lambda x, y: x.times(y), letters)
                for letters in pauli_letters.values()]
            word = PauliWord.from_letters(products)
            return word

        self.floor_word = get_stabilizer(self.floor)
        self.lid_word = get_stabilizer(self.lid)
        # Allow sign difference - e.g. can measure XXXX and -XXXX and still
        # build a detector from this.
        assert self.floor_word.word == self.lid_word.word

        for (t, check) in self.lid:
            if t == 0:
                self.triggers.add(check)
                check.detectors_triggered.append(self)

        super().__init__(['floor', 'lid'])

    def get_targets(self, current_round: int, measurements: int):
        assert self.triggers == self.triggers_measured

        def get_face_targets(face):
            # Find the actual rounds in which the checks that constitute the
            # detector face were measured
            face = [
                (current_round + rounds_ago, check)
                for rounds_ago, check in face]
            # Only if every check in this face has been measured can we build
            # the detector face.
            if all([round >= 0 for round, check in face]):
                # Find the measurement number stim will have assigned each check
                face_targets = [
                    check.measurements[round] - measurements
                    for round, check in face]
                return face_targets
            else:
                return []

        targets = []
        targets.extend(get_face_targets(self.lid))
        targets.extend(get_face_targets(self.floor))
        # Set triggers measured back to the empty set ready for future
        # measurement layers.
        self.triggers_measured = set()
        return targets






