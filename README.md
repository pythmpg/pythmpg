# Magnetic point group (MPG) tensor analysis toolkit

[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.18672613-blue.svg)](https://doi.org/10.5281/zenodo.18672613)
[![readthedocs status](https://app.readthedocs.org/projects/pythmpg/badge/?version=latest)](https://pythmpg.readthedocs.io/en/latest/) 

The ``pythmpg`` package provides tools for enumerating symmetry
properties of all 122 magnetic point groups (MPGs), and for counting
the number of independent components of arbitrary-rank tensors
under those symmetries as classified by their Jahn symbol.

A major feature of the package is its ability to export data in the
form of a ``.csv`` file that can be used to build a spreadsheet
capable of screening for MPGs based on whether they have
certain symmetries or support specified tensor properties. A broader
community of users can then use standard spreadsheet tools, such
as sorting on columns and hiding columns and rows, to achieve similar ends,
without the need to access the Python codes themselves.

## Resources
- **Source**: https://github.com/pythmpg/pythmpg
- **Documentation**: https://pythmpg.readthedocs.io/en/latest/
- **Zenodo Repository**: https://zenodo.org/records/18672613

## Installation

PythMPG is available through PyPI.

```bash
pip install pythmpg
```
To install from source in editable mode:

```bash
git clone https://github.com/pythmpg/pythmpg.git
cd pythmpg
pip install -e .
```

PythMPG ≥ 1.0.0 requires Python ≥ 3.12 and the core dependency:
- numpy ≥ 2.0

## Citation

If you use the code in your paper, please cite us

```bibtex
@software{Urru_Python_Magnetic_Point_2026,
author = {Urru, Andrea and Birol, Turan and Cole, Trey and Vanderbilt, David},
doi = {10.5281/zenodo.18672613},
license = {GPL-3.0-or-later},
month = jun,
title = {{Python Magnetic Point Group (PythMPG)}},
url = {https://zenodo.org/records/18672613},
version = {1.0.0},
year = {2026}
}
```
