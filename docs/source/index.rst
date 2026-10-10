.. MPG documentation master file, created by
   sphinx-quickstart on Wed May 13 16:21:56 2026.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

PythMPG
=======

**PythMPG** is a Magnetic Point Group (MPG) tensor analysis toolkit.

This python package provides tools to enumerate symmetry properties of all
122 magnetic point groups and to count the number of independent
components of arbitrary-rank tensors under those symmetries, as
classified by their Jahn symbol.

A major feature of the package is its ability to export data in the
form of a ``.csv`` file that can be used to build a spreadsheet
capable of screening for MPGs based on whether they have
certain symmetries or support specied tensor properties. A broader
community of users can then use standard spreadsheet tools, such
as sorting on columns and hiding columns and rows, to achieve similar ends,
without the need to access the python codes themselves.

Modules in the Package
----------------------

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

Citation
--------

The principal reference describing the code is
Andrea Urru, Turan Birol, Trey Cole, and David Vanderbilt,
*Screening of tensor properties by magnetic point group symmetries:
The pythmpg code package*,
`https://arxiv.org/abs/2610.10024 <https://arxiv.org/abs/2610.10024>`_,
2026.

The spreadsheets and code are also available at
`this Zenodo repository <https://zenodo.org/records/18672613>`_,
which can be cited in Bibtex and other formats using
the *Export* tab on the landing page.

License
-------

This software is released under the
`GNU General Public License v3.0 <https://www.gnu.org/licenses/gpl-3.0.html>`_.


.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Contents

   self
   introduction
   user_guide
   api
   release
