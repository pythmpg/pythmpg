#!/usr/bin/env python3

# ------------------------------------------------------
# Example user program to create a minimal spreadsheet
# ------------------------------------------------------

# import Spreadsheet class
from pythmpg.spreadsheet import Spreadsheet

# Initialize my spreadsheet
my_sheet = Spreadsheet()

# Default sections are
#   'groups'
#     Identification info on MPGs
#   'symm'
#     Presence or absence of six types of symmetry
#   'scalar'
#     Chiral                e             
#     Colorless             a
#     Axionic               ae
#   'vector'
#     Polar                 V
#     Ferro- magnetic       aeV    
#     Ferro- rotational     eV            
#     Ferro- toroidal       aV

# Print the default sections and their headers
# my_sheet.header_report()

# Add a new section of tensor orders
tensor_section = [
      ('Piezoel','V[V2]'),
      ('Piezomag','ae[V2]V') ]

my_sheet.add('tensor',tensor_section)

# Print the modified sections and their headers
my_sheet.header_report()

# Print the details of the parsing of Jahn symbols
# my_sheet.jahn_report()

# Analyze tensors for each MPG
my_sheet.build_csv()

# Write csv files to disk
my_sheet.write_csv('mpg_min_bool.csv')
my_sheet.write_csv('mpg_min_num.csv',kind='num')
