"""Shared fixtures for the pythmpg test suite."""

import pytest

from pythmpg.spreadsheet import Spreadsheet


@pytest.fixture(scope="session")
def default_sheet():
    """A Spreadsheet built with all default sections (groups/symm/scalar/vector).

    Session-scoped because :meth:`Spreadsheet.build_csv` runs the full
    122-MPG analysis and is comparatively expensive.  Tests must treat the
    returned object as read-only.
    """
    sheet = Spreadsheet()
    sheet.build_csv()
    return sheet
