from typing import List, Dict, Iterable, Any

from main.utils.Colour import Colour
from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.pauli.PauliProduct import PauliProduct
from main.utils.NiceRepr import NiceRepr
from main.utils.types import Coordinates
from main.utils.utils import coords_mid, coords_length, coords_minus, xor


class Check(NiceRepr):
    def __init__(
            self, paulis: List[Pauli] | Dict[Coordinates, Pauli],
            anchor: Coordinates = None, colour: Colour = None):
        """A Pauli operator to measure.
        
        A check is a Pauli operator that is actually measured as part of
        the code. In some codes the checks are just the stabilizers (e.g.
        surface code, colour code), but this need not be the case (e.g.
        subsystem code, Floquet codes).

        Args:
            paulis:
                The Paulis that make up this check. One can either pass in a
                list of Paulis, or a dictionary with items (k, v), where v is
                a Pauli and the key k is the coordinates of the Pauli relative
                to the anchor. This is useful when printing codes with
                non-planar geometries.
            anchor:
                In some sense its center, but need not actually be the
                midpoint of all the data qubits involved. Useful for
                distinguishing otherwise identical checks - e.g. on a rotated
                surface code, the weight-2 checks along the top and bottom -
                and for placing ancillas. Defaults to the midpoint of all
                Paulis in the check.
            colour:
                If it exists, the colour assigned to this check - e.g. in the
                colour code, each plaquette (i.e. check) gets a colour.
        """
        self._assert_check_non_empty(paulis)
        if isinstance(paulis, dict):
            self._assert_anchor_is_given(anchor, paulis)
            self._assert_pauli_coords_valid(paulis.values())
            self._assert_anchor_dim_matches_pauli_dims(
                anchor, list(paulis.values()))
            self._assert_offset_coords_valid(paulis)
            self._assert_anchor_dim_matches_offset_dims(
                anchor, paulis)
            self._assert_qubits_unique(paulis.values())
        else:
            self._assert_qubits_unique(paulis)
            self._assert_pauli_coords_valid(paulis)
            # Auto-create dictionary for paulis
            if anchor is None:
                anchor = coords_mid(*[pauli.qubit.coords for pauli in paulis])
            else:
                self._assert_anchor_dim_matches_pauli_dims(anchor, paulis)
            paulis = {
                coords_minus(pauli.qubit.coords, anchor): pauli
                for pauli in paulis}

        self.product = PauliProduct(list(paulis.values()))
        self._assert_is_hermitian(self.product, paulis)
        self._assert_is_not_identity_up_to_sign(self.product, paulis)

        self.paulis = paulis
        self.anchor = anchor
        self.colour = colour
        self.weight = len(paulis)

        # The following properties are set by a compiler.
        self.ancilla = None

        super().__init__(['product.word', 'anchor', 'colour', 'paulis'])

    @property
    def dimension(self):
        return coords_length(self.anchor)

    @property
    def has_tuple_coords(self):
        return isinstance(self.anchor, tuple)

    @staticmethod
    def _assert_check_non_empty(
            paulis: List[Pauli] | Dict[Coordinates, Pauli]):
        if len(paulis) == 0:
            raise ValueError(
                "Can't create a check from an empty list or dict of Paulis.")

    @staticmethod
    def _assert_anchor_is_given(
            anchor: Coordinates, paulis: Dict[Coordinates, Pauli]):
        # Anchor shouldn't be None in this case, because the keys of
        # `paulis` are the offsets of the paulis from the anchor.
        if anchor is None:
            raise ValueError(
                "If dictionary of Paulis is supplied, `anchor` mustn't be "
                "None, since the keys of the dictionary are the "
                "coordinates of the Paulis relative to the anchor. (And "
                "a sensible anchor can't be automatically inferred). "
                f"Given Paulis are: {paulis}")

    @staticmethod
    def _assert_offset_coords_valid(paulis: Dict[Coordinates, Pauli]):
        offset_dimensions = {coords_length(offset) for offset in paulis.keys()}
        if len(offset_dimensions) > 1:
            raise ValueError(
                "The given distances from the check's anchor to the Paulis "
                "must all have the same dimensions. The given dictionary of "
                f"Paulis is {paulis}.")
        all_tuples = all([
            isinstance(offset, tuple) for offset in paulis.keys()])
        all_non_tuples = not any([
            isinstance(offset, tuple) for offset in paulis.keys()])
        if not (all_tuples or all_non_tuples):
            raise ValueError(
                f"Can't mix tuple and non-tuple offsets! "
                f"The given dictionary of Paulis is {paulis}.")

    @staticmethod
    def _assert_qubits_unique(paulis: Iterable[Pauli]):
        qubits = [pauli.qubit for pauli in paulis]
        if len(set(qubits)) != len(qubits):
            raise ValueError(
                f"Can't include the same qubit more than once in a check! "
                f"Paulis that make up the check are: {list(paulis)}")

    @staticmethod
    def _assert_pauli_coords_valid(paulis: Iterable[Pauli]):
        dimensions = {pauli.dimension for pauli in paulis}
        if len(dimensions) > 1:
            raise ValueError(
                f"Paulis within a check must all have the same dimension. "
                f"Instead, found dimensions {dimensions}. "
                f"Paulis that make up the check are: {list(paulis)}")
        all_tuples = all([pauli.has_tuple_coords for pauli in paulis])
        all_non_tuples = all([not pauli.has_tuple_coords for pauli in paulis])
        if not (all_tuples or all_non_tuples):
            raise ValueError(
                f"Can't mix tuple and non-tuple coordinates! "
                f"Paulis that make up the check are: {list(paulis)}")

    @staticmethod
    def _assert_anchor_dim_matches_pauli_dims(
            anchor: Coordinates, paulis: List[Pauli]):
        # Assumes we've already checked that paulis are non-empty and has all
        # same dimensions.
        if coords_length(anchor) != paulis[0].dimension:
            raise ValueError(
                f"Anchor must have same dimensions as Paulis. "
                f"Instead, anchor is {anchor} and Paulis are {paulis}.")
        types_wrong = xor(
            isinstance(anchor, tuple), paulis[0].has_tuple_coords)
        if types_wrong:
            raise ValueError(
                f"Anchor and Pauli coordinates must all be tuples or all "
                f"be non-tuples - can't mix! Instead, anchor is {anchor} and "
                f"Paulis are {paulis}.")

    @staticmethod
    def _assert_anchor_dim_matches_offset_dims(
            anchor: Coordinates, paulis: Dict[Coordinates, Pauli]):
        # Assumes we've already checked that paulis are non-empty and all
        # offsets have same dimensions.
        offset = list(paulis.keys())[0]
        if coords_length(anchor) != coords_length(offset):
            raise ValueError(
                f"Anchor must have same dimensions as offsets. "
                f"Instead, anchor is {anchor} and dict of Paulis is {paulis}.")
        types_wrong = xor(
            isinstance(anchor, tuple),
            isinstance(offset, tuple))
        if types_wrong:
            raise ValueError(
                f"Anchor and offsets must all be tuples or all be non-tuples "
                f"- can't mix! Instead, anchor is {anchor} and dict of Paulis "
                f"is {paulis}.")

    @staticmethod
    def _assert_is_hermitian(
            product: PauliProduct, paulis: Dict[Coordinates, Pauli]):
        if not product.is_hermitian:
            raise ValueError(
                f"The product of all Paulis in a Check must be Hermitian! "
                f"Given Paulis are {paulis}.")

    @staticmethod
    def _assert_is_not_identity_up_to_sign(
            product: PauliProduct, paulis: Dict[Coordinates, Pauli]):
        # Stim's Pauli product measurement command 'MPP' has no syntax for
        # such measurements. Since they're pointless, we may as well outlaw
        # them from the outset.
        if all(letter == 'I' for letter in product.word.word):
            raise ValueError(f"""
                Can't have a check in which every Pauli is either I or -I. 
                Given Paulis are {paulis}.""")

    def __eq__(self, other: Any):
        return \
            type(self) == type(other) and \
            self.paulis == other.paulis and \
            self.anchor == other.anchor and \
            self.colour == other.colour

    def __hash__(self):
        paulis = frozenset(self.paulis.items())
        return hash((paulis, self.anchor, self.colour))

