"""Tests for :mod:`pythmpg.pg_elements` -- rotation matrices and group tables.

These lock in the geometric foundation of the package.  A future edit that
mistypes a rotation axis, an angle, or a matrix entry would break
crystallographic group closure; it is caught here rather than surfacing as a
silently wrong tensor count far downstream.
"""

import numpy as np
import pytest

from pythmpg.pg_elements import (
    get_cub_rot_dict,
    get_cub_table,
    get_hex_rot_dict,
    get_hex_table,
    get_mult_table,
    rot_mat,
)


def is_proper_rotation(matrix):
    """Return True if ``matrix`` is a 3x3 orthogonal matrix with det +1."""
    matrix = np.asarray(matrix, dtype=float)
    return (
        matrix.shape == (3, 3)
        and np.allclose(matrix @ matrix.T, np.eye(3))
        and np.isclose(np.linalg.det(matrix), 1.0)
    )


class TestRotMat:
    def test_zero_angle_is_identity(self):
        assert np.allclose(rot_mat([0, 0, 1], 0, 1), np.eye(3))

    def test_full_turn_is_identity(self):
        # angle = 2*pi*m/n; m == n is one full revolution
        assert np.allclose(rot_mat([0, 0, 1], 3, 3), np.eye(3))

    def test_quarter_turn_about_z(self):
        # +90 deg about +z sends x -> y and y -> -x
        rot = rot_mat([0, 0, 1], 1, 4)
        assert np.allclose(rot @ [1, 0, 0], [0, 1, 0], atol=1e-12)
        assert np.allclose(rot @ [0, 1, 0], [-1, 0, 0], atol=1e-12)

    def test_axis_need_not_be_normalized(self):
        assert np.allclose(rot_mat([0, 0, 5], 1, 6), rot_mat([0, 0, 1], 1, 6))

    @pytest.mark.parametrize(
        "axis,m,n",
        [([0, 0, 1], 1, 6), ([1, 1, 1], 1, 3), ([1, -1, 0], 1, 2)],
    )
    def test_always_proper_rotation(self, axis, m, n):
        assert is_proper_rotation(rot_mat(axis, m, n))


class TestRotationDicts:
    def test_hex_has_twelve_operations(self):
        assert len(get_hex_rot_dict()) == 12

    def test_cub_has_twentyfour_operations(self):
        assert len(get_cub_rot_dict()) == 24

    @pytest.mark.parametrize("getter", [get_hex_rot_dict, get_cub_rot_dict])
    def test_all_entries_are_proper_rotations(self, getter):
        assert all(is_proper_rotation(m) for m in getter().values())

    @pytest.mark.parametrize("getter", [get_hex_rot_dict, get_cub_rot_dict])
    def test_identity_present_and_correct(self, getter):
        assert np.allclose(getter()["1"], np.eye(3))

    @pytest.mark.parametrize("getter", [get_hex_rot_dict, get_cub_rot_dict])
    def test_matrices_are_distinct(self, getter):
        # Two named operations must never collapse to the same matrix.
        mats = list(getter().values())
        for i in range(len(mats)):
            for j in range(i + 1, len(mats)):
                assert not np.allclose(mats[i], mats[j])


class TestMultiplicationTable:
    @pytest.mark.parametrize(
        "table_getter,order", [(get_hex_table, 12), (get_cub_table, 24)]
    )
    def test_table_is_complete(self, table_getter, order):
        _rot_dict, table = table_getter()
        assert len(table) == order * order

    @pytest.mark.parametrize("table_getter", [get_hex_table, get_cub_table])
    def test_closure_results_are_valid_names(self, table_getter):
        rot_dict, table = table_getter()
        names = set(rot_dict)
        assert all(value in names for value in table.values())

    @pytest.mark.parametrize("table_getter", [get_hex_table, get_cub_table])
    def test_identity_acts_trivially(self, table_getter):
        rot_dict, table = table_getter()
        for name in rot_dict:
            assert table[("1", name)] == name
            assert table[(name, "1")] == name

    @pytest.mark.parametrize("table_getter", [get_hex_table, get_cub_table])
    def test_rows_and_columns_are_latin_squares(self, table_getter):
        # Group axiom: each element appears exactly once in every row and column.
        rot_dict, table = table_getter()
        names = list(rot_dict)
        for a in names:
            row = [table[(a, b)] for b in names]
            col = [table[(b, a)] for b in names]
            assert sorted(row) == sorted(names)
            assert sorted(col) == sorted(names)

    @pytest.mark.parametrize("table_getter", [get_hex_table, get_cub_table])
    def test_every_element_has_inverse(self, table_getter):
        rot_dict, table = table_getter()
        names = list(rot_dict)
        for a in names:
            assert any(table[(a, b)] == "1" for b in names)

    def test_non_closed_set_raises(self):
        # {identity, 4z} is not closed: 4z * 4z = 2z is absent -> ValueError.
        full = get_cub_rot_dict()
        subset = {"1": full["1"], "4z": full["4z"]}
        with pytest.raises(ValueError):
            get_mult_table(subset)
