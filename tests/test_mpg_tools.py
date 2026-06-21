"""Tests for :mod:`pythmpg.mpg_tools` -- classification and tensor counts.

These are the scientific outputs of the package.  Anchor values are textbook
results: e.g. the piezoelectric tensor ``V[V2]`` has 18 independent components
in triclinic group ``1`` and exactly 0 in any centrosymmetric group.  The
helper-function tests guard the linear-algebra primitives those counts rest on.
"""

import math

import numpy as np
import pytest

from pythmpg.mpg_dicts import mpg_dict
from pythmpg.mpg_tools import (
    get_mpg_info,
    get_num_indep,
    init_orth_list,
    is_zero,
    norm,
    permutation_sign,
    symmetrize_indices,
    t_prod,
    transform_tensors,
)


class TestGetMpgInfo:
    def test_default_covers_all_groups(self):
        info = get_mpg_info()
        assert set(info) == {"bns", "order", "group_type", "symm_info"}
        for key in info:
            assert len(info[key]) == 122

    def test_order_matches_mpg_dict(self):
        info = get_mpg_info()
        for i, name in enumerate(mpg_dict):
            assert info["order"][i] == math.prod(mpg_dict[name][2])

    def test_group_types_are_valid(self):
        info = get_mpg_info()
        assert set(info["group_type"]) <= {"Grey", "Black-White", "Colorless"}

    @pytest.mark.parametrize(
        "name,order,gtype,symm",
        [
            # symm = [P, T, PT, P*R, T*R, PT*R]
            ("1", 1, "Colorless", [0, 0, 0, 0, 0, 0]),
            ("1'", 2, "Grey", [0, 1, 0, 0, 1, 0]),
            ("-1", 2, "Colorless", [1, 0, 0, 1, 0, 0]),
            ("m-3m1'", 96, "Grey", [1, 1, 1, 1, 1, 1]),
        ],
    )
    def test_known_groups(self, name, order, gtype, symm):
        info = get_mpg_info([name])
        assert info["order"][0] == order
        assert info["group_type"][0] == gtype
        assert [int(b) for b in info["symm_info"][0]] == symm


# (Jahn symbol, MPG): number of independent components.  Verified against the
# package and consistent with standard crystallographic tensor tables.
NUM_INDEP = {
    ("", "1"): 1,
    ("", "m-3m"): 1,
    ("e", "1"): 1,
    ("e", "-1"): 0,
    ("e", "m-3m"): 0,
    ("a", "1"): 1,
    ("a", "1'"): 0,
    ("ae", "1"): 1,
    ("ae", "-1"): 0,
    ("V", "1"): 3,
    ("V", "-1"): 0,
    ("V", "m-3m"): 0,
    ("V2", "1"): 9,
    ("V2", "m-3m"): 1,
    ("V2", "4/mmm"): 2,
    ("[V2]", "1"): 6,
    ("[V2]", "m-3m"): 1,
    ("[V2]", "4/mmm"): 2,
    ("{V2}", "1"): 3,
    ("{V2}", "m-3m"): 0,
    ("V[V2]", "1"): 18,  # piezoelectric tensor in triclinic
    ("V[V2]", "-1"): 0,  # forbidden by inversion
    ("ae[V2]V", "1"): 18,
    ("ae[V2]V", "m-3m"): 0,
    ("ae[V2]V", "4/mmm"): 1,
}


class TestGetNumIndep:
    @pytest.mark.parametrize(
        "symbol,group,expected",
        [(s, g, n) for (s, g), n in NUM_INDEP.items()],
    )
    def test_anchor_values(self, symbol, group, expected):
        result = get_num_indep([symbol], mpg_list=[group])
        assert result[symbol][0] == expected

    def test_default_covers_all_groups(self):
        result = get_num_indep(["[V2]"])
        assert len(result["[V2]"]) == 122

    def test_scalar_is_one_for_every_group(self):
        result = get_num_indep([""])
        assert all(n == 1 for n in result[""])

    @pytest.mark.parametrize("symbol,rank", [("V", 1), ("[V2]", 2), ("V[V2]", 3)])
    def test_count_bounded_by_full_basis(self, symbol, rank):
        # Independent components can never be negative nor exceed 3**rank.
        result = get_num_indep([symbol])
        assert all(0 <= n <= 3**rank for n in result[symbol])

    @pytest.mark.parametrize("group", ["-1", "2/m", "mmm", "4/mmm", "m-3m"])
    def test_centrosymmetric_kills_polar_vector(self, group):
        # Any group containing spatial inversion forbids a polar vector.
        assert get_num_indep(["V"], mpg_list=[group])["V"][0] == 0

    def test_invalid_symbol_raises(self):
        with pytest.raises(RuntimeError):
            get_num_indep(["Q7"], mpg_list=["1"])


class TestLinearAlgebraHelpers:
    @pytest.mark.parametrize(
        "perm,sign",
        [
            ((0, 1, 2), 1),
            ((1, 0, 2), -1),
            ((1, 0), -1),
            ((2, 1, 0), -1),
            ((0, 1), 1),
            ((2, 0, 1), 1),
        ],
    )
    def test_permutation_sign(self, perm, sign):
        assert permutation_sign(perm) == sign

    def test_symmetrize_produces_symmetric_tensor(self):
        tensor = np.arange(9, dtype=float).reshape(3, 3)
        sym = symmetrize_indices(tensor, [0, 1])
        assert np.allclose(sym, sym.T)

    def test_symmetrize_is_idempotent(self):
        tensor = np.arange(9, dtype=float).reshape(3, 3)
        sym = symmetrize_indices(tensor, [0, 1])
        assert np.allclose(symmetrize_indices(sym, [0, 1]), sym)

    def test_antisymmetrize_of_symmetric_is_zero(self):
        tensor = np.arange(9, dtype=float).reshape(3, 3)
        sym = symmetrize_indices(tensor, [0, 1])
        assert is_zero(symmetrize_indices(sym, [0, 1], antisym=True))

    def test_inner_product_norm_and_is_zero(self):
        tensor = np.arange(9, dtype=float).reshape(3, 3)
        assert np.isclose(t_prod(tensor, tensor), norm(tensor) ** 2)
        assert is_zero(np.zeros((3, 3)))
        assert not is_zero(tensor)

    def test_init_orth_list_is_orthonormal_basis(self):
        basis = init_orth_list(2)
        assert len(basis) == 9
        assert all(b.shape == (3, 3) for b in basis)
        assert all(np.isclose(norm(b), 1.0) for b in basis)
        for i in range(len(basis)):
            for j in range(i + 1, len(basis)):
                assert np.isclose(t_prod(basis[i], basis[j]), 0.0)

    def test_transform_tensors_identity_and_parity(self):
        stack = np.stack(init_orth_list(2), axis=-1)
        assert np.allclose(transform_tensors(stack.copy(), np.eye(3), 0), stack)
        assert np.allclose(transform_tensors(stack.copy(), np.eye(3), 1), -stack)
