#!/usr/bin/env python3

# ------------------------------------------------------
# Example user program to create a spreadsheet
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

# Delete 'scalar' section
my_sheet.delete('scalar')

# Add 'tensor' entries
tensor_section = [
      ('Piezomag','ae[V2]V','+ Lin mag- resistance'),
      ('Nat Optical Activ','{V2}V'),
      ('Gyro birefring','a[V2]V'),
      ('Ordinary Hall','e{V2}V','+ Ordinary Faraday'),
      ('Spont Hall','a{V2}','+ Spont Faraday'),
      ('Spont Ettings- hausen','aV2')]
my_sheet.add('tensor',tensor_section)

# Print the modified sections and their headers
my_sheet.header_report()

# Analyze tensors for each MPG
my_sheet.build_csv()

# Write csv files to disk
my_sheet.write_csv('mpg_exten.csv',kind='num')
