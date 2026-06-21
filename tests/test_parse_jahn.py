"""Tests for :mod:`pythmpg.parse_jahn` -- parsing of Jahn symbols.

The parser decides which tensor-index symmetrizations get applied, so a
regression here silently changes physics.  These tests pin known parses, rank
extraction, the bracket matcher, result caching, and rejection of malformed
symbols.  They also guard the module-level ``axis`` counter, which must reset
between calls.
"""

import pytest

from pythmpg.parse_jahn import (
    ParsingError,
    find_match,
    jahn_dict,
    jahn_rank,
    parse_jahn_symbol,
    parse_string,
)


class TestValidSymbols:
    @pytest.mark.parametrize(
        "symbol,expected",
        [
            ("", ("nosymm", [])),
            ("V", ("nosymm", [0])),
            ("V2", ("nosymm", [0, 1])),
            ("[V2]", ("symm", [0, 1])),
            ("{V2}", ("asymm", [0, 1])),
            ("V[V2]", ("nosymm", [0, ("symm", [1, 2])])),
            ("[V2V2]", ("symm", [("nosymm", [0, 1]), ("nosymm", [2, 3])])),
            ("[[V2][V2]]", ("symm", [("symm", [0, 1]), ("symm", [2, 3])])),
        ],
    )
    def test_known_parses(self, symbol, expected):
        assert parse_jahn_symbol(symbol) == expected

    @pytest.mark.parametrize(
        "symbol,rank",
        [
            ("", 0),
            ("V", 1),
            ("V2", 2),
            ("[V2]", 2),
            ("{V2}", 2),
            ("V[V2]", 3),
            ("[V2V2]", 4),
        ],
    )
    def test_rank(self, symbol, rank):
        assert jahn_rank(parse_jahn_symbol(symbol)) == rank


class TestRank:
    def test_scalar_rank_is_zero(self):
        assert jahn_rank(("nosymm", [])) == 0

    def test_rank_is_one_plus_max_axis(self):
        assert jahn_rank(("nosymm", [0, 1, 2])) == 3


class TestInvalidSymbols:
    @pytest.mark.parametrize(
        "bad",
        [
            "X9",  # illegal characters
            "[V2",  # unbalanced bracket (no close)
            "V2]",  # unbalanced bracket (no open)
            "[V2V3]",  # symmetrized elements of differing size
            "{V2V3}",
        ],
    )
    def test_returns_none(self, bad):
        assert parse_jahn_symbol(bad) is None

    def test_deeply_nested_is_rejected(self):
        # Pathological nesting must be rejected, not crash the parser.
        assert parse_jahn_symbol("[" * 9 + "V2" + "]" * 9) is None


class TestCaching:
    def test_result_is_cached_and_identical(self):
        first = parse_jahn_symbol("[V2]")
        assert "[V2]" in jahn_dict
        # A second parse must return the very same cached object, not a recompute.
        assert parse_jahn_symbol("[V2]") is first


class TestParserHelpers:
    @pytest.mark.parametrize(
        "text,length",
        [("[V2]", 4), ("{V2}", 4), ("[V2V2]", 6), ("[V2]extra", 4)],
    )
    def test_find_match(self, text, length):
        assert find_match(text) == length

    def test_find_match_unbalanced_raises(self):
        with pytest.raises(ParsingError):
            find_match("[V2")

    def test_parse_string_tokenizes(self):
        assert parse_string("1[22]2") == [1, "[22]", 2]

    def test_parse_string_bad_char_raises(self):
        with pytest.raises(ParsingError):
            parse_string("1@2")


class TestGlobalState:
    def test_axis_counter_resets_between_calls(self):
        # The parser uses a module-level ``axis`` counter; it must reset each
        # call so an earlier parse cannot inflate a later symbol's rank.
        parse_jahn_symbol("V2V2")  # rank 4
        assert jahn_rank(parse_jahn_symbol("V")) == 1
