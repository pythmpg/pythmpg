
Introduction
============

MENTION THE USER GUIDE.  CLARIFY WHAT TO DO IF YOU ONLY WANT
THE SPREADSHEETS.
ADD LINKS TO THE GIT REPOSITORY AND THE ZENODO RECORD.

The top-level entry point for most users is the :class:`~pythmpg.Spreadsheet`
class, which drives construction and export of a ``.csv`` spreadsheet
whose rows and columns correspond to magnetic point groups (MPGs) and
symmetry-allowed properties respectively.
The two functions :func:`~pythmpg.get_mpg_info` and :func:`~pythmpg.get_num_indep` from
the :mod:`~pythmpg.mpg_tools` module are also exported for direct use.

Example Scripts
---------------

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

Installation
------------

PythMPG is available through PyPI::

   pip install pythmpg

To install from source in editable mode::

   git clone https://github.com/pythmpg/pythmpg.git
   cd pythmpg
   pip install -e .

PythMPG ≥ 1.0.0 requires Python ≥ 3.12 and numpy ≥ 2.0

License
-------

If you use the code in your paper, please cite us.  Here is the
``bibtex`` entry::

   @software{Urru_Python_Magnetic_Point_2026,
   author = {Urru, Andrea and Birol, Turan and Cole, Trey and Vanderbilt, David},
   doi = {10.5281/zenodo.18672614},
   license = {GPL-3.0-or-later},
   month = jun,
   title = {{Python Magnetic Point Group (PythMPG)}},
   url = {https://zenodo.org/records/18672614},
   version = {1.0.0},
   year = {2026}
   }
