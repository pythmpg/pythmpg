"""
pythmpg — Magnetic Point Group (MPG) tensor analysis toolkit.

This package provides tools to enumerate symmetry properties of all
122 magnetic point groups and to count the number of independent
components of arbitrary-rank tensors under those symmetries, as
classified by their Jahn symbol.

The top-level entry point for most users is the :class:`Spreadsheet`
class, which drives construction and export of a full MPG spreadsheet.
The two functions :func:`get_mpg_info` and :func:`get_num_indep` from
the ``mpg_tools`` module are also exported here for direct use.

Examples
--------
Minimal workflow using all defaults:

>>> from pythmpg import Spreadsheet
>>> sheet = Spreadsheet()
>>> sheet.header_report()          # optional: inspect column layout
>>> sheet.build_csv()              # compute tensor counts for every MPG
>>> sheet.write_csv(file='mpg.csv')

Query symmetry info for a subset of groups:

>>> from pythmpg import get_mpg_info
>>> info = get_mpg_info(['4/mmm', 'm-3m'])
>>> info['order']
[16, 48]

Count independent components of a rank-2 symmetric tensor:

>>> from pythmpg import get_num_indep
>>> counts = get_num_indep(['[V2]'], mpg_list=['1', 'm', '4/mmm'])

Available Modules
-----------------
spreadsheet
    Defines :class:`Spreadsheet`, the primary user-facing class.
mpg_tools
    Functions :func:`get_mpg_info` and :func:`get_num_indep` for
    querying MPG symmetry properties and tensor independence counts.
mpg_dicts
    Module-level dictionaries describing all 122 MPGs, their
    generators, and BNS serial numbers.  Built on first import.
pg_elements
    Constructs rotation matrices and multiplication tables for the
    hexagonal and cubic crystallographic point groups.
parse_jahn
    Parser for Jahn symbols that encodes index-symmetrization
    instructions for arbitrary-rank tensors.
"""

from pythmpg.spreadsheet import Spreadsheet
from pythmpg.mpg_tools import get_mpg_info, get_num_indep

__all__ = [
    "Spreadsheet",
    "get_mpg_info",
    "get_num_indep",
]
