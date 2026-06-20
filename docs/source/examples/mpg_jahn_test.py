#!/usr/bin/env python3

# ------------------------------------------------------
# Example user program to create a spreadsheet
# ------------------------------------------------------

# import Spreadsheet class
from pythmpg.spreadsheet import Spreadsheet

# Initialize spreadsheet and delete 'scalar' and 'vector' sections
my_sheet = Spreadsheet()
my_sheet.delete('scalar')
my_sheet.delete('vector')

# Add 'test' entries (without physical labels)
test_section = [
      ('','V'),
      ('','V2'),
      ('','[V2]'),
      ('','V[V2]'),
      ('','{V3}'),
      ('','[[V2][V2]]'),
      ('','[{V2}{V2}]'),
      ('','[{V2}{V2}{V2}]') ]
my_sheet.add('test',test_section)

# Print the modified sections and their headers
my_sheet.header_report()

# Print the details of the parsing of Jahn symbols
my_sheet.jahn_report()

# Analyze tensors and write csv file to disk
my_sheet.build_csv()
my_sheet.write_csv('mpg_jahn_test.csv',kind='num')
