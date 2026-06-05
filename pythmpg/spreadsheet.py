"""
User-level interface for generating Magnetic Point Group (MPG) spreadsheets.

This module defines the ``Spreadsheet`` class, which is designed to be
invoked at the user level, i.e., called from outside the ``pythmpg``
package.

Notes
-----
External functions called from this module are defined in module
``mpg_tools``, which in turn makes use of other lower-level modules
in this package.

Example
-------
Here is a minimal example of a calling script:
>>> from pythmpg import Spreadsheet     # Import this module
>>> my_sheet = Spreadsheet()            # Instantiate spreadsheet
>>> my_sheet.header_report()            # Print header info (optional)
>>> my_sheet.build_csv()                # Analyze tensors
>>> my_sheet.write_csv('my_sheet.csv')  # Write the .csv file
"""

from copy import deepcopy
import csv

# ----------------------------------------------------
# Class definition for class 'Spreadsheet'
# ----------------------------------------------------


class Spreadsheet:
    """
    Generate and output data for a Magnetic Point Group (MPG) spreadsheet.

    The spreadsheet is organized into named sections of column headers.
    Default sections cover group identification (``groups``), symmetry
    indicators (``symm``), and scalar and vector property columns
    (``scalar``, ``vector``).  Sections can be added, removed, or
    replaced before calling :meth:`build_csv`.

    Attributes
    ----------
    defaults : dict
        Class-level dictionary of default header sections, each mapping
        a section name to a list of column-header tuples.
    section_dict : dict
        Instance copy of ``defaults``, modified by :meth:`add`,
        :meth:`delete`, and :meth:`modify`.
    spreadsheet_data : list of list
        Populated by :meth:`build_csv`; contains header rows followed
        by one data row per MPG.
    """

    # Specify default sections of column headers
    defaults = {}
    defaults["groups"] = [
        ("", "", "Number"),
        ("", "", "Name"),
        ("", "", "Order"),
        ("", "Jahn symbol", "Type"),
    ]
    defaults["symm"] = [
        ("Has P", ""),
        ("Has T", ""),
        ("Has PT", ""),
        ("Has P*R", "", "R = simple proper rot"),
        ("Has T*R", ""),
        ("Has PT*R", ""),
    ]
    defaults["scalar"] = [
        ("Struct chiral", "e", "Has no P*R or PT*R"),
        ("Colorless", "a", "Has no T*R or PT*R"),
        ("Axionic", "ae", "Has no P*R or T*R"),
    ]
    defaults["vector"] = [
        ("Polar", "V"),
        ("Ferro- magnetic", "aeV"),
        ("Ferro- rotational", "eV"),
        ("Ferro- toroidal", "aV"),
    ]

    # Instantiation of class object
    def __init__(self):
        self.section_dict = deepcopy(self.defaults)

    def delete(self, section):
        """
        Remove a section from the spreadsheet headers.

        Parameters
        ----------
        section : str
            Key of the section to remove from ``section_dict``.

        Raises
        ------
        ValueError
            If ``section`` is not a key in ``section_dict``.
        """
        if section not in self.section_dict:
            raise ValueError(f"Section {section} is not in dictionary")
        del self.section_dict[section]

    def add(self, section, section_entry):
        """
        Add a new section to the spreadsheet headers.

        Parameters
        ----------
        section : str
            Key for the new section to add to ``section_dict``.
        section_entry : list of tuple
            List of column-header tuples defining the new section.

        Raises
        ------
        ValueError
            If ``section`` is already a key in ``section_dict``;
            use :meth:`modify` to update an existing section.
        """
        if section in self.section_dict:
            raise ValueError(f"Section {section} is already present; use 'modify'")
        self.section_dict[section] = section_entry

    def modify(self, section, section_entry):
        """
        Replace an existing section of the spreadsheet headers.

        Parameters
        ----------
        section : str
            Key of the section to update in ``section_dict``.
        section_entry : list of tuple
            New list of column-header tuples for the section.

        Raises
        ------
        ValueError
            If ``section`` is not a key in ``section_dict``;
            use :meth:`add` to introduce a new section.
        """
        if section not in self.section_dict:
            raise ValueError(f"Section {section} is not in dictionary")
        self.section_dict[section] = section_entry

    def header_report(self):
        """
        Print a formatted report of the current spreadsheet headers.

        Iterates over all sections in ``section_dict`` and prints each
        column-header tuple, along with any associated annotation stored
        in the third element of the tuple.
        """

        print("\n=============")
        print("Header Report")
        print("=============\n")

        print("Header Sections:", list(self.section_dict.keys()))
        for section in self.section_dict:
            print(60 * "-" + f"\n{section}:\n" + 60 * "-")
            for header in self.section_dict[section]:
                line = "  " + f"{header[0]:22}{header[1]:14}"
                if len(header) == 3:
                    line += f"{header[2]:22}"
                print(line)
        print(60 * "-" + "\n")

    def jahn_report(self):
        """
        Print the details of the parsing of Jahn symbols.

        Iterates over all sections in ``section_dict``, pulls
        the Jahn symbol names, parses each one, and prints
        explanatory information.
        """

        print("==================")
        print("Jahn Symbol Report")
        print("==================\n")

        from pythmpg.parse_jahn import parse_jahn_symbol, jahn_dict

        # Construct list of Jahn symbols
        sections = list(self.section_dict.keys())
        jahn_list = []
        for sec in sections[2:]:
            for entry in self.section_dict[sec]:
                jahn_list.append(entry[1])

        for jahn in jahn_list:
            space_parity = jahn.count("e") % 2
            time_parity = jahn.count("a") % 2
            jahn_bare = jahn.replace("a", "").replace("e", "")

            print(f"Parsing Jahn symbol {jahn}")
            pty = f"({space_parity},{time_parity})"
            if jahn_bare == "":
                print(f"Parities = {pty}, Scalar")
            elif jahn_bare in jahn_dict:
                print(f"Parities = {pty}, bare Jahn {jahn_bare} already parsed")
            else:
                print(f"Parities = {pty}, bare Jahn = {jahn_bare}")
                # Parse rest of Jahn symbol to get instruction set
                instructions = parse_jahn_symbol(jahn_bare, if_print=True)

                # In case an exception was raised:
                if instructions is None:
                    print("  Correct the syntax of this Jahn symbol and try again.\n")
                    exit(1)

            print("")

    def write_csv(self, filename, kind="bool"):
        """
        Write ``spreadsheet_data`` to a CSV file.

        Parameters
        ----------
        filename : str
            Path of the output CSV file.
        kind : {'bool', 'num'}, optional
            Output format.  ``'bool'`` (default) replaces all non-zero,
            non-blank data cells with ``'1'``; ``'num'`` writes the raw
            numerical values.

        Raises
        ------
        ValueError
            If ``kind`` is not ``'bool'`` or ``'num'``.
        """

        if kind not in ("bool", "num"):
            raise ValueError(
                f"Argument kind='{kind}' not recognized" + " in Spreadsheet.write_csv"
            )

        # Check that build_csv() has been called
        if not hasattr(self, "spreadsheet_data"):
            raise RuntimeError("Must call build_csv first")

        print("================")
        print("Writing CSV File")
        print("================\n")

        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            if kind == "num":
                writer.writerows(self.spreadsheet_data)
                print(f"Numerical CSV file {filename} has been written\n")
            elif kind == "bool":
                data = deepcopy(self.spreadsheet_data)
                for row in data[4:]:
                    for j, cell in enumerate(row):
                        if j > 3 and cell not in ["", "0"]:
                            row[j] = "1"
                writer.writerows(data)
                print(f"Boolean CSV file {filename} has been written\n")

    def build_csv(self):
        """
        Populate ``spreadsheet_data`` with header and MPG data rows.

        Constructs the full spreadsheet contents by first building four
        header rows from ``section_dict``, then calling external helpers
        to obtain per-MPG symmetry information and independent-tensor
        counts for each Jahn symbol.  Results are stored in
        ``self.spreadsheet_data`` as a list of rows ready for writing
        with :meth:`write_csv`.

        Notes
        -----
        This method imports ``mpg_dict`` from ``pythmpg.mpg_dicts`` and
        ``get_mpg_info``, ``get_num_indep`` from ``pythmpg.mpg_tools``.
        Both function calls use their defaults, which implies all MPGs.
        """

        print("====================")
        print("Building Spreadsheet")
        print("====================\n")

        from pythmpg.mpg_dicts import mpg_dict
        from pythmpg.mpg_tools import get_mpg_info, get_num_indep

        # set up spreadsheet column structure and fill header rows
        # build Jahn symbol ('js') list and column map

        js_list = []
        js_column = []
        col = 0
        row_zero = []
        row_one = []
        row_two = []
        row_three = []

        sections = self.section_dict.keys()
        for k, sec in enumerate(sections):
            # add empty columns between groups
            if k != 0:
                row_zero.append("")
                row_one.append("")
                row_two.append("")
                row_three.append("")
                col += 1
            for entry in self.section_dict[sec]:
                row_zero.append(sec)
                row_one.append(entry[0])
                row_two.append(entry[1])
                if len(entry) == 3:
                    row_three.append(entry[2])
                else:
                    row_three.append("")
                # Sections beyond the first two ('groups' and 'symm')
                # are assumed to contain Jahn symbols in entry[1]
                if k > 1:
                    js_list.append(entry[1])
                    js_column.append(col)
                col += 1
        num_cols = len(row_one)

        # Fill header rows
        self.spreadsheet_data = [row_zero, row_one, row_two, row_three]

        # Now call functions from module 'mpg_tools.py' to get the
        # information needed to fill the spreadsheet cells, to be
        # returned in the form of two dictionaries

        # mpg_info_dict  (all lists run over MPGs)
        #   Key: 'bns'
        #     Value: List of strings giving BNS serial number of MPG
        #   Key: 'order'
        #     Value: List of integers giving order of group
        #   Key: 'group_type'
        #     Value: List of strings giving type of MPG (colorless, ...)
        #   Key: 'symm_info'
        #     Value: List of tuples of 6 Booleans specifying
        #            presence or absence of a symmetry

        # This function call uses default that implies all MPGs
        mpg_info_dict = get_mpg_info()

        # num_indep_dict
        #   Key: Jahn symbol (string)
        #     Value: List (over MPGs) of number of indep tensors (int)

        # This function call uses default that implies all MPGs
        num_indep_dict = get_num_indep(js_list)

        # Unpack information (each is a list over MPGs)
        bns = mpg_info_dict["bns"]
        order = mpg_info_dict["order"]
        group_type = mpg_info_dict["group_type"]
        symm_info = mpg_info_dict["symm_info"]

        # Loop over MPG's and fill rows of the spreadsheet
        for j, mpg in enumerate(mpg_dict):
            # Get information not involving Jahn symbols
            group_info = [bns[j], mpg, order[j], group_type[j]]
            presence_info = [str(int(x)) for x in symm_info[j]]

            # Start filling row
            row = group_info + [""] + presence_info
            # Fill with blanks for a total of num_cols columns
            row += [""] * (num_cols - len(row))

            # Get number of independent elements by Jahn symbol
            num_indep = [num_indep_dict[js][j] for js in js_list]
            for i, val in enumerate(num_indep):
                row[js_column[i]] = str(val)

            self.spreadsheet_data.append(row)

        print("")
