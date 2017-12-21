#!/usr/bin/env python

#author: Justin Clifford Smith
#date: December 1, 2017

#Written in python 3.x

#This script sorts a geometry.in file by z position in a 
#FHI-aims input file. It has very basic error checking. 

import sys
import operator


if len(sys.argv) != 2:
    print('Usage: fhiatoms.py GEOMETRYFILE')
    sys.exit()

latvec=0
number_atoms=0

def printcurrent(line, outfile):
  outfile.write(" ".join(str(x) for x in line))
  outfile.write("\n")


allatoms = []

with open(sys.argv[1]) as f: 
  with open('sorted.in', 'w') as out:
    for line in f:
      linelist = line.split() #split the lines (str) into lists
      if linelist: #checks if the line is entirely empty
        if linelist[0] == 'lattice_vector':
          latvec += 1  
          printcurrent(linelist, out)
        elif (linelist[0] == 'atom' or linelist[0] == 'atom_frac') :
           number_atoms += 1
           allatoms.append(linelist)
    allatoms.sort(key=operator.itemgetter(3))
    for item in allatoms:
      printcurrent(item, out)


if not latvec == 3:
    print('{} lattice vectors. Is this an FHI-aims file? (Ignore if molecule)'\
        .format(latvec))
if number_atoms ==0:
    print('ERROR: 0 atoms. Is this an FHI-aims files?')

