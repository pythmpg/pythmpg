#!/usr/bin/env python3

# ------------------------------------------------------
# Test program, similar to mpg_min.py
# ------------------------------------------------------

import pytest
from pythmpg.spreadsheet import Spreadsheet
from pathlib import Path

def test_package_functionality():
    my_sheet = Spreadsheet()
    tensor_section = [ ('Piezoel','V[V2]'), ('Piezomag','ae[V2]V') ]
    my_sheet.add('tensor',tensor_section)
    my_sheet.build_csv()
    my_sheet.write_csv('test.csv',kind='num')
    
    actual_file = Path("test.csv")
    expected_file = Path("test_ref.csv")
    assert actual_file.read_text() == expected_file.read_text()
