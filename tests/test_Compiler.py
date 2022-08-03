import stim
from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliZ
from main.compiling.compilers.AncillaPerCheckCompiler import AncillaPerCheckCompiler
from main.compiling.compilers.Compiler import Compiler
from main.QPUs.SquareLatticeQPU import SquareLatticeQPU
from main.codes.RepetitionCode import RepetitionCode
from main.codes.RotatedSurfaceCode import RotatedSurfaceCode
from main.compiling.Circuit import Circuit
from main.compiling.noise.models import CircuitLevelNoise
from main.codes.hexagonal.tic_tac_toe.HoneycombCode import HoneycombCode
from main.compiling.syndrome_extraction.controlled_gate_orderers.TrivialOrderer import (
    TrivialOrderer,
)
from main.compiling.syndrome_extraction.controlled_gate_orderers.RotatedSurfaceCodeOrderer import (
    RotatedSurfaceCodeOrderer,
)
from main.compiling.syndrome_extraction.extractors.PurePauliWordExtractor import (
    PurePauliWordExtractor,
)
from main.enums import State
import stimcirq

test_qpu = SquareLatticeQPU((3, 1))
rep_code = RepetitionCode(2)
test_qpu.embed(rep_code, (0, 0), 0)
trivial_orderer = TrivialOrderer()
extractor = PurePauliWordExtractor(trivial_orderer)
noise_model = CircuitLevelNoise(0.1, 0.15, 0.05, 0.03, 0.03)
test_compiler = AncillaPerCheckCompiler(noise_model, extractor)
rep_qubits = list(rep_code.data_qubits.values())
rep_initials_zero = {qubit: State.Zero for qubit in rep_qubits}
rep_initials_plus = {qubit: State.Plus for qubit in rep_qubits}
rep_finals = [Pauli(qubit, PauliZ) for qubit in rep_qubits]
rep_logicals = [rep_code.logical_qubits[0].z]


def test_compile_initialisation():
    _, _, circuit = test_compiler.compile_initialisation(
        rep_code, rep_initials_zero, None
    )
    assert circuit.instructions[0][rep_code.data_qubits[0]][0].name == "RZ"
    assert circuit.instructions[1][rep_code.data_qubits[2]][0].name == "PAULI_CHANNEL_1"

    _, _, circuit = test_compiler.compile_initialisation(
        rep_code, rep_initials_plus, None
    )
    assert circuit.instructions[0][rep_code.data_qubits[0]][0].name == "RX"
    assert circuit.instructions[1][rep_code.data_qubits[0]][0].name == "PAULI_CHANNEL_1"

    try:
        _, _, circuit = test_compiler.compile_initialisation(rep_code, {}, None)
        raise ValueError("Shouldn't be able to initialise if no states given.")
    except ValueError as error:
        expected_message = (
            "Some data qubits' initial states either aren't given or "
            "aren't determined by the given initial stabilizers! Please "
            "give a complete set of desired initial states or desired "
            "stabilizers for the first round of measurements."
        )
        assert str(error) == expected_message


def test_compile_code():
    code = RotatedSurfaceCode(3)

    syndrome_extractor = PurePauliWordExtractor(RotatedSurfaceCodeOrderer())
    p = 0.1
    noise_model = CircuitLevelNoise(
        initialisation=0.3, idling=p, one_qubit_gate=p, two_qubit_gate=p, measurement=p
    )

    compiler = AncillaPerCheckCompiler(noise_model, syndrome_extractor)

    rsc_qubits = list(code.data_qubits.values())
    rsc_initials = {qubit: State.Zero for qubit in rsc_qubits}
    rsc_finals = [Pauli(qubit, PauliZ) for qubit in rsc_qubits]
    rsc_logicals = [code.logical_qubits[0].z]

    rsc_circuit: stim.Circuit = compiler.compile_code(
        code,
        code.distance,
        initial_states=rsc_initials,
        final_measurements=rsc_finals,
        logical_observables=rsc_logicals,
    )

    """
    print(
        stimcirq.stim_circuit_to_cirq_circuit(rsc_circuit.without_noise()),
        file=open("output2.txt", "a"),
    )
    """

    # 4 + 8 + 8+4
    assert rsc_circuit.num_detectors == 24

    # 8 + 8 + 17 = 3
    assert rsc_circuit.num_measurements == 33
    error: stim.ExplainedError = rsc_circuit.shortest_graphlike_error()[0]
    print(error, "\n \n \n")
    error: stim.ExplainedError = rsc_circuit.shortest_graphlike_error()[1]
    print(error)
    #    print(rsc_circuit.shortest_graphlike_error())
    assert len(rsc_circuit.shortest_graphlike_error()) == 3


"""
def test_compile_code_circuit_level_noise():
    
    # phenom_rep_circuit = phenom_pure_trivial_compiler.compile_code(
    #     rep_code, 2, rep_initials, rep_finals, rep_logicals)

    test_compiler.compile_code(rep_code, 2, rep_initials, rep_finals, rep_logicals)
    d_0 = rep_code.data_qubits[0]
    d_1 = rep_code.data_qubits[2]
#    anc = rep_code.ancilla_qubits[1]

    noise_timestep_0 = {
        d_0: [["X_Error", 0.15]],
        d_1: [["X_Error", 0.15]],
        anc: [["X_Error", 0.15]],
    }
    noise_timestep_1 = {
        (d_0, anc): [["DEPOLARIZE2", 0.05]],
        d_1: [["DEPOLARIZE1", 0.1]],
    }
    noise_timestep_2 = {
        (d_1, anc): [["DEPOLARIZE2", 0.05]],
        d_0: [["DEPOLARIZE1", 0.1]],
        anc: [["X_Error", 0.03]],
    }
    noise_timestep_3 = {d_0: [["DEPOLARIZE1", 0.1]], d_1: [["DEPOLARIZE1", 0.1]]}

    assert test_compiler.gates_at_timesteps[0]["noise"] == noise_timestep_0
    assert test_compiler.gates_at_timesteps[1]["noise"] == noise_timestep_1
    assert test_compiler.gates_at_timesteps[2]["noise"] == noise_timestep_2
    assert test_compiler.gates_at_timesteps[3]["noise"] == noise_timestep_3

    test_compiler = Compiler(noise_model)
    test_compiler.compile_code(
        rep_code, repeat_block=False, final_block=False, measure_data_qubits=True
    )
    noise_timestep_2 = {
        (d_1, anc): ["DEPOLARIZE2", 0.05],
        d_0: [["DEPOLARIZE1", 0.1], ["X_Error", 0.3]],
        anc: [["X_Error", 0.03]],
    }
    test_compiler.gates_at_timesteps[2]["noise"] == noise_timestep_2



def test_compile_code():
    test_qpu = SquareLatticeQPU((3, 1))
    rep_code = RepetitionCode(2)
    test_qpu.embed(rep_code, (0, 0), 0)
    test_compiler = Compiler()

    test_compiler.compile_code(rep_code, repeat_block=False, final_block=False)
    gate_dict = {}
    for qubit in rep_code.data_qubits.values():
        gate_dict[qubit] = "RZ"
    for qubit in rep_code.ancilla_qubits.values():
        gate_dict[qubit] = "RZ"
    assert test_compiler.gates_at_timesteps[0]["gates"] == gate_dict

    test_qpu = SquareLatticeQPU((3, 1))
    rep_code = RepetitionCode(2)
    test_qpu.embed(rep_code, (0, 0), 0)
    test_compiler = Compiler()

    test_compiler.compile_code(
        rep_code, repeat_block=False, final_block=False, measure_data_qubits=True
    )

    gate_dict = {}
    gate_measure_dict = {}
    data_qubits = tuple()
    for qubit in rep_code.data_qubits.values():
        gate_dict[qubit] = "RZ"
        data_qubits += (qubit,)

    for qubit in rep_code.ancilla_qubits.values():
        gate_dict[qubit] = "RZ"

        gate_measure_dict[((data_qubits), (), qubit)] = "MRZ"
        gate_measure_dict[qubit] = "MRZ"

    gate_measure_dict[(rep_code.data_qubits[0],)] = "Observable"

    assert test_compiler.gates_at_timesteps[0]["gates"] == gate_dict
    assert test_compiler.gates_at_timesteps[3]["gates"] == gate_measure_dict

    test_qpu = SquareLatticeQPU((7, 1))
    rep_code = RepetitionCode(4)
    test_qpu.embed(rep_code, (0, 0), 0)
    test_compiler = Compiler()

    test_compiler.compile_code(rep_code, repeat_block=False, final_block=False)
    gate_dict = {}
    measurement_dict = {}
    for qubit in rep_code.data_qubits.values():
        gate_dict[qubit] = "RZ"
    for qubit in rep_code.ancilla_qubits.values():
        gate_dict[qubit] = "RZ"
        measurement_dict[qubit] = "MRZ"

    assert test_compiler.gates_at_timesteps[0]["gates"] == gate_dict
    assert test_compiler.gates_at_timesteps[3]["gates"] == measurement_dict

    test_compiler_2_rounds = Compiler()

    test_compiler_2_rounds.compile_code(rep_code, repeat_block=False, final_block=True)
    gate_dict = {}

    for i in range(3):
        assert (
            test_compiler_2_rounds.gates_at_timesteps[i]["gates"]
            == test_compiler.gates_at_timesteps[i]["gates"]
        )

    for i in range(5, 8):
        assert (
            test_compiler_2_rounds.gates_at_timesteps[i]["gates"]
            == test_compiler.gates_at_timesteps[i - 4]["gates"]
        )

    test_compiler_3_rounds = Compiler()

    test_compiler_3_rounds.compile_code(rep_code, repeat_block=True, final_block=True)

    for i in range(3):
        assert (
            test_compiler_3_rounds.gates_at_timesteps[i]["gates"]
            == test_compiler.gates_at_timesteps[i]["gates"]
        )

    for i in range(5, 8):
        assert (
            test_compiler_3_rounds.gates_at_timesteps[i]["gates"]
            == test_compiler.gates_at_timesteps[i - 4]["gates"]
        )


def test_initialize_qubits():
    test_qpu = SquareLatticeQPU((3, 1))
    rep_code = RepetitionCode(2)

    test_qpu.embed(rep_code, (0, 0), 0)
    test_compiler = Compiler()
    test_compiler.initialize_qubits(rep_code.data_qubits.values(), 0)
    assert test_compiler.gates_at_timesteps[0]["gates"] == {
        rep_code.data_qubits[0]: "RZ",
        rep_code.data_qubits[2]: "RZ",
    }

    honeycomb_code = HoneycombCode(5)
    print(honeycomb_code.data_qubits)
    print(honeycomb_code.ancilla_qubits)


#    print(honeycomb_code.)


test_initialize_qubits()


def test_compile_one_round():
    test_qpu = SquareLatticeQPU((3, 1))
    rep_code = RepetitionCode(2)

    test_qpu.embed(rep_code, (0, 0), 0)
    test_compiler = Compiler()
    test_compiler.compile_one_round(test_qpu.codes[1].schedule[0], 0)
    gate_dict = {}
    for qubit in rep_code.data_qubits.values():
        gate_dict[qubit] = "RZ"
    for qubit in rep_code.ancilla_qubits.values():
        gate_dict[qubit] = "RZ"
    test_compiler.initialize_qubits(rep_code.data_qubits.values(), 0)
    assert test_compiler.gates_at_timesteps[0]["gates"] == gate_dict

    test_qpu = SquareLatticeQPU((7, 1))
    rep_code = RepetitionCode(4)

    test_qpu.embed(rep_code, (0, 0), 0)
    test_compiler = Compiler()
    test_circuit = Circuit()
    test_compiler.initialize_qubits(rep_code.data_qubits.values(), 0)
    test_compiler.compile_one_round(test_qpu.codes[1].schedule[0], 0)

    gate_dict = {}
    for qubit in rep_code.data_qubits.values():
        gate_dict[qubit] = "RZ"
    for qubit in rep_code.ancilla_qubits.values():
        gate_dict[qubit] = "RZ"
    assert test_compiler.gates_at_timesteps[0]["gates"] == gate_dict

    gate_dict_t1 = {}
    gate_dict_t2 = {}
    gate_dict_t3 = {}
    for check in rep_code.checks:

        gate_dict_t1[check.paulis[0].qubit, check.ancilla] = "CNOT"
        gate_dict_t2[check.paulis[1].qubit, check.ancilla] = "CNOT"
        gate_dict_t3[check.ancilla] = "MRZ"

    assert test_compiler.gates_at_timesteps[1]["gates"] == gate_dict_t1
    assert test_compiler.gates_at_timesteps[2]["gates"] == gate_dict_t2
    assert test_compiler.gates_at_timesteps[3]["gates"] == gate_dict_t3

    assert test_compiler.gates_at_timesteps[3]["initialized_qubits"] == set(
        rep_code.data_qubits.values()
    )


def test_compile_rotated_surface_code_three_rounds():
    test_qpu = SquareLatticeQPU((10, 10))
    sc = RotatedSurfaceCode(3)
    test_qpu.embed(sc, (0, 0), (0, 1))
    test_compiler = Compiler()
    test_compiler.initialize_qubits(sc.data_qubits.values(), 0)
    test_compiler.compile_code(test_qpu.codes[1], measure_data_qubits=True)

    gate_dict_0 = {}
    gate_dict_1 = {}
    for data_q in sc.data_qubits.values():
        gate_dict_0[data_q] = "RZ"
    for check in sc.schedule[0]:
        if check.initialization_timestep == 0:
            gate_dict_0[check.ancilla] = "RZ"
            gate_dict_1[check.ancilla] = "H"
        elif check.initialization_timestep == 1:
            gate_dict_1[check.ancilla] = "RZ"

    gate_dict_2 = {
        sc.ancilla_qubits[(4, 1)]: "RZ",
        ((sc.data_qubits[(4, 2)]), (sc.ancilla_qubits[(3, 2)])): "CNOT",
        ((sc.data_qubits[(2, 2)]), (sc.ancilla_qubits[(1, 2)])): "CNOT",
        ((sc.data_qubits[(2, 0)]), (sc.ancilla_qubits[(1, 0)])): "CNOT",
        ((sc.ancilla_qubits[(2, 1)]), (sc.data_qubits[(3, 1)])): "CNOT",
        ((sc.ancilla_qubits[(2, 3)]), (sc.data_qubits[(3, 3)])): "CNOT",
        ((sc.ancilla_qubits[(0, 3)]), (sc.data_qubits[(1, 3)])): "CNOT",
    }

    assert test_compiler.gates_at_timesteps[0]["gates"] == gate_dict_0
    assert test_compiler.gates_at_timesteps[1]["gates"] == gate_dict_1
    assert len(test_compiler.gates_at_timesteps[2]["initialized_qubits"]) == 16
    assert test_compiler.gates_at_timesteps[2]["gates"] == gate_dict_2


def test_compile_rotated_surface_code_one_round():
    test_qpu = SquareLatticeQPU((10, 10))
    sc = RotatedSurfaceCode(3)
    test_qpu.embed(sc, (0, 0), (0, 1))
    test_compiler = Compiler()
    test_compiler.initialize_qubits(sc.data_qubits.values(), 0)
    test_compiler.compile_one_round(test_qpu.codes[1].schedule[0], 0)

    gate_dict_0 = {}
    gate_dict_1 = {}
    for data_q in sc.data_qubits.values():
        gate_dict_0[data_q] = "RZ"
    for check in sc.schedule[0]:
        if check.initialization_timestep == 0:
            gate_dict_0[check.ancilla] = "RZ"
            gate_dict_1[check.ancilla] = "H"
        elif check.initialization_timestep == 1:
            gate_dict_1[check.ancilla] = "RZ"

    gate_dict_2 = {
        sc.ancilla_qubits[(4, 1)]: "RZ",
        ((sc.data_qubits[(4, 2)]), (sc.ancilla_qubits[(3, 2)])): "CNOT",
        ((sc.data_qubits[(2, 2)]), (sc.ancilla_qubits[(1, 2)])): "CNOT",
        ((sc.data_qubits[(2, 0)]), (sc.ancilla_qubits[(1, 0)])): "CNOT",
        ((sc.ancilla_qubits[(2, 1)]), (sc.data_qubits[(3, 1)])): "CNOT",
        ((sc.ancilla_qubits[(2, 3)]), (sc.data_qubits[(3, 3)])): "CNOT",
        ((sc.ancilla_qubits[(0, 3)]), (sc.data_qubits[(1, 3)])): "CNOT",
    }

    assert test_compiler.gates_at_timesteps[0]["gates"] == gate_dict_0
    assert test_compiler.gates_at_timesteps[1]["gates"] == gate_dict_1
    assert len(test_compiler.gates_at_timesteps[2]["initialized_qubits"]) == 16
    assert test_compiler.gates_at_timesteps[2]["gates"] == gate_dict_2
    assert len(test_compiler.gates_at_timesteps[7]["gates"]) == 3
"""
