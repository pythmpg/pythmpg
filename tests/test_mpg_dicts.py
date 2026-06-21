"""Tests for :mod:`pythmpg.mpg_dicts` -- construction of all 122 MPGs.

``mpg_dict`` and ``bns_dict`` are built once at import.  These tests verify the
count, structure, and internal consistency of every group (its order equals the
product of its polycyclic generator orders) so a future change to ``parse_mpg``
cannot quietly produce a malformed or wrong-order group.
"""

import math

import pytest

import pythmpg.mpg_dicts as md
from pythmpg.mpg_dicts import bns_dict, mpg_dict, parse_mpg


class TestMpgDict:
    def test_has_122_groups(self):
        assert len(mpg_dict) == 122

    def test_entry_structure(self):
        for _name, value in mpg_dict.items():
            frame, generators, gen_orders = value
            assert frame in ("hex", "cub")
            assert len(generators) == len(gen_orders)
            for rot, p_space, p_time in generators:
                assert isinstance(rot, str)
                assert p_space in (0, 1)
                assert p_time in (0, 1)
            assert all(isinstance(o, int) and o > 0 for o in gen_orders)

    @pytest.mark.parametrize(
        "name,order",
        [
            ("1", 1),
            ("-1", 2),
            ("2", 2),
            ("23", 12),
            ("432", 24),
            ("4/mmm", 16),
            ("6/mmm", 24),
            ("m-3m", 48),
            ("m-3m1'", 96),
        ],
    )
    def test_known_group_orders(self, name, order):
        _frame, _generators, gen_orders = mpg_dict[name]
        assert math.prod(gen_orders) == order

    def test_parse_mpg_is_self_consistent_for_all_groups(self):
        # parse_mpg internally validates the group order and rejects duplicate
        # elements (raising RuntimeError); re-running it on every group guards
        # the constructor end-to-end and confirms it reproduces mpg_dict.
        for name in mpg_dict:
            _frame, _generators, gen_orders = parse_mpg(name)
            assert math.prod(gen_orders) == math.prod(mpg_dict[name][2])


class TestBnsDict:
    def test_has_122_entries(self):
        assert len(bns_dict) == 122

    def test_first_is_111(self):
        assert bns_dict["1"] == "1.1.1"

    def test_serial_third_field_runs_1_to_122(self):
        thirds = [int(v.split(".")[2]) for v in bns_dict.values()]
        assert thirds == list(range(1, 123))

    def test_format_is_three_dotted_integers(self):
        for value in bns_dict.values():
            parts = value.split(".")
            assert len(parts) == 3
            assert all(p.isdigit() for p in parts)


class TestGroupHelpers:
    @pytest.fixture(autouse=True)
    def _use_cubic_table(self):
        # product()/get_cycle()/get_closure() read the module-level table_dict;
        # set it explicitly so these helpers are testable in isolation, then
        # restore whatever was there to avoid leaking state to other tests.
        saved = md.table_dict
        md.table_dict = md.cub_table_dict
        yield
        md.table_dict = saved

    def test_product_combines_parities_mod_2(self):
        assert md.product(("4z", 1, 0), ("4z", 1, 1)) == ("2z", 0, 1)

    def test_get_cycle_order(self):
        assert len(md.get_cycle(("4z", 0, 0))) == 4
        assert len(md.get_cycle(("2z", 0, 0))) == 2
        assert md.get_cycle(("1", 0, 0)) == [("1", 0, 0)]

    def test_get_closure_is_closed(self):
        ops = md.get_closure([("1", 0, 0), ("2z", 0, 0)])
        assert ("2z", 0, 0) in ops
        assert len(ops) == 2
