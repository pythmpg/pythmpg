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


.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Contents

   self
   introduction
   user_guide
   api
