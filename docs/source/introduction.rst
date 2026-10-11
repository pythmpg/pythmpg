
Introduction
============

This documentation describes the ``pythmpg`` software that can be used
to create user-customized spreadsheets as part of the
``Python MPG`` project.  See the :doc:`user_guide`
for an overview of the project.  Note that some
pre-constructed spreadsheets are provided at the
`Zenodo Pyth-MPG site <https://zenodo.org/records/18672613>`_;
these can be used without the need to reference the software
described here.

The source for this documentation and the ``pythmpg`` software package
is the `pythmpg GitHub repository <https://github.com/pythmpg/pythmpg/>`_.

Example Script for Spreadsheet Creation
---------------------------------------

The top-level entry point for most users is the :class:`~pythmpg.Spreadsheet`
class, which drives construction and export of a ``.csv`` spreadsheet
whose rows and columns correspond to magnetic point groups (MPGs) and
symmetry-allowed properties respectively.  Here is a
minimal workflow using all defaults::

   from pythmpg import Spreadsheet
   sheet = Spreadsheet()
   sheet.header_report()          # optional: inspect column layout
   sheet.build_csv()              # compute tensor counts for every MPG
   sheet.write_csv('mpg.csv')

Example Scripts for Direct Access
---------------------------------

Direct access to the symmetry information, without reference to
any spreadsheet structure, is also provided by
two functions :func:`~pythmpg.get_mpg_info` and
:func:`~pythmpg.get_num_indep` from the :mod:`~pythmpg.mpg_tools`
module.

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

