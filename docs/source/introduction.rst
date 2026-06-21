
Introduction
============

The top-level entry point for most users is the :class:`~pythmpg.Spreadsheet`
class, which drives construction and export of a ``.csv`` spreadsheet
whose rows and columns correspond to magnetic point groups (MPGs) and
symmetry-allowed properties respectively.
The two functions :func:`~pythmpg.get_mpg_info` and :func:`~pythmpg.get_num_indep` from
the :mod:`~pythmpg.mpg_tools` module are also exported for direct use.

To Do (For Developers)
======================

Add sections for

- Installation?
- License?
- Links to Zenodo and ReadTheDocs?

What belongs here vs. on landing page?

Examples
--------

Minimal workflow using all defaults::

   from pythmpg import Spreadsheet
   sheet = Spreadsheet()
   sheet.header_report()          # optional: inspect column layout
   sheet.build_csv()              # compute tensor counts for every MPG
   sheet.write_csv('mpg.csv')

Query symmetry info for a subset of groups::

   from pythmpg import get_mpg_info
   info = get_mpg_info(['4/mmm', 'm-3m'])
   info['order']
   # [16, 48]

Count independent components of a rank-2 symmetric tensor::

   from pythmpg import get_num_indep
   count_dict = get_num_indep(['[V2]'], mpg_list=['1', 'm', '4/mmm'])
   count_dict
   # {'[V2]': [6, 4, 2]}

Available Modules
-----------------

:mod:`~pythmpg.spreadsheet`
   Defines :class:`~pythmpg.Spreadsheet`, the primary user-facing class.

:mod:`~pythmpg.mpg_tools`
   Functions :func:`~pythmpg.get_mpg_info` and :func:`~pythmpg.get_num_indep` for
   querying MPG symmetry properties and tensor independence counts.

:mod:`~pythmpg.mpg_dicts`
   Module-level dictionaries describing all 122 MPGs, their
   generators, and BNS serial numbers. Built on first import.

:mod:`~pythmpg.pg_elements`
   Constructs rotation matrices and multiplication tables for the
   hexagonal and cubic crystallographic point groups.

:mod:`~pythmpg.parse_jahn`
   Parser for Jahn symbols that encodes index-symmetrization
   instructions for arbitrary-rank tensors.
