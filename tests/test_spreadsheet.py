"""Tests for :class:`pythmpg.spreadsheet.Spreadsheet` -- the user interface.

Covers section management, output formats, error handling, and a full-output
regression against the committed golden file ``tests/test_ref.csv``.  The
regression is the original ``test_mpg.py`` rewritten to be path-independent so
it passes from any working directory -- including VS Code's Test Explorer,
which runs pytest from the repository root.
"""

import csv
from pathlib import Path

import pytest

from pythmpg.spreadsheet import Spreadsheet

DATA_DIR = Path(__file__).parent


class TestSectionManagement:
    def test_default_sections_present(self):
        sheet = Spreadsheet()
        assert list(sheet.section_dict) == ["groups", "symm", "scalar", "vector"]

    def test_add_new_section(self):
        sheet = Spreadsheet()
        sheet.add("tensor", [("Piezoel", "V[V2]")])
        assert sheet.section_dict["tensor"] == [("Piezoel", "V[V2]")]

    def test_add_existing_section_raises(self):
        sheet = Spreadsheet()
        with pytest.raises(ValueError):
            sheet.add("scalar", [])

    def test_delete_section(self):
        sheet = Spreadsheet()
        sheet.delete("scalar")
        assert "scalar" not in sheet.section_dict

    def test_delete_missing_section_raises(self):
        sheet = Spreadsheet()
        with pytest.raises(ValueError):
            sheet.delete("nope")

    def test_modify_section(self):
        sheet = Spreadsheet()
        sheet.modify("vector", [("Polar", "V")])
        assert sheet.section_dict["vector"] == [("Polar", "V")]

    def test_modify_missing_section_raises(self):
        sheet = Spreadsheet()
        with pytest.raises(ValueError):
            sheet.modify("nope", [])

    def test_instances_are_isolated_from_defaults(self):
        # section_dict is a deepcopy of the class-level defaults; mutating one
        # instance must not leak into another instance or into the class.
        first = Spreadsheet()
        first.delete("scalar")
        second = Spreadsheet()
        assert "scalar" in second.section_dict
        assert "scalar" in Spreadsheet.defaults


class TestBuildCsv:
    def test_row_count(self, default_sheet):
        # 4 header rows + one data row per MPG.
        assert len(default_sheet.spreadsheet_data) == 4 + 122

    def test_rows_have_uniform_width(self, default_sheet):
        widths = {len(row) for row in default_sheet.spreadsheet_data}
        assert len(widths) == 1

    def test_header_labels(self, default_sheet):
        row3 = default_sheet.spreadsheet_data[3]
        assert row3[:4] == ["Number", "Name", "Order", "Type"]


class TestWriteCsvErrors:
    def test_write_before_build_raises(self, tmp_path):
        sheet = Spreadsheet()
        with pytest.raises(RuntimeError):
            sheet.write_csv(tmp_path / "out.csv")

    def test_bad_kind_raises(self, default_sheet, tmp_path):
        with pytest.raises(ValueError):
            default_sheet.write_csv(tmp_path / "out.csv", kind="xml")


class TestCsvOutput:
    def test_num_and_bool_files_written(self, default_sheet, tmp_path):
        num = tmp_path / "num.csv"
        boolean = tmp_path / "bool.csv"
        default_sheet.write_csv(num, kind="num")
        default_sheet.write_csv(boolean, kind="bool")
        assert num.exists()
        assert boolean.exists()

    def test_bool_cells_are_blank_zero_or_one(self, default_sheet, tmp_path):
        out = tmp_path / "bool.csv"
        default_sheet.write_csv(out, kind="bool")
        rows = list(csv.reader(out.open(newline="")))
        for row in rows[4:]:  # data rows only
            for cell in row[4:]:  # beyond the four group-identification columns
                assert cell in ("", "0", "1")


class TestRegression:
    def test_matches_golden_csv(self, tmp_path):
        # Reproduce the documented mpg_min workflow and compare the full
        # 122-group numeric output to the committed golden file.
        sheet = Spreadsheet()
        sheet.add("tensor", [("Piezoel", "V[V2]"), ("Piezomag", "ae[V2]V")])
        sheet.build_csv()
        out = tmp_path / "test.csv"
        sheet.write_csv(out, kind="num")
        assert out.read_text() == (DATA_DIR / "test_ref.csv").read_text()


class TestReports:
    def test_header_report_runs(self, capsys):
        Spreadsheet().header_report()
        assert "Header Report" in capsys.readouterr().out

    def test_jahn_report_runs(self, capsys):
        Spreadsheet().jahn_report()
        assert "Jahn Symbol Report" in capsys.readouterr().out
