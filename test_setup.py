from setup import find_circuit_name, find_num_qubits

class TestFindCircuitName:
    def test_finds_ghz(self):
        filename = "circuits/ghz_5qubits.qasm"
        circuit_name = find_circuit_name(filename)
        assert circuit_name == "ghz"

class TestFindNumQubits:
    def test_finds_ghz_11(self):
        filename = "circuits/ghz_11qubits.qasm"
        num_qubits = find_num_qubits(filename)
        assert num_qubits == 11