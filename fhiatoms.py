#!/usr/bin/env python

#author: Justin Clifford Smith
#date: November 8, 2017

#Written in python 3.x

#This script outputs the total number of atoms, and number per species in a 
#FHI-aims input file. It has very basic error checking. 

import sys


if len(sys.argv) != 2:
    print('Usage: fhiatoms.py GEOMETRYFILE')
    sys.exit()

species ={}
latvec=0
number_atoms=0

with open(sys.argv[1]) as f: #this method automatically closes the file
    for line in f:
        linelist = line.split() #split the lines (str) into lists
        if linelist: #checks if the line is entirely empty
            if linelist[0] == 'lattice_vector':
                latvec +=1
            elif (linelist[0] == 'atom' or linelist[0] == 'atom_frac') :
                number_atoms += 1
                elem = linelist[4]
                species.setdefault(elem, 0)
                species[elem] += 1

print('Total: {}'.format(number_atoms))
for atoms in species:
    print('{}: {}'.format(atoms, species[atoms]))

if not latvec == 3:
    print('{} lattice vectors. Is this an FHI-aims file? (Ignore if molecule)'\
          .format(latvec))
if number_atoms ==0:
    print('ERROR: 0 atoms. Is this an FHI-aims files?')

