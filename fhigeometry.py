#!/usr/bin/env python

#author: Justin Clifford Smith
#date: January 2, 2018

#Written in python 3.x

#This script reads an FHI-aims output file from  relaxation calculation 
#and creates a last_geometry.in with the final relaxation step.

#This script outputs the total number of atoms, and number per species in a 
#FHI-aims input file. It has very basic error checking. 

import sys


def printcurrent(line, outfile):
  outfile.write(" ".join(str(x) for x in line))
  outfile.write("\n")


if len(sys.argv) != 2:
    print('Usage: fhigeometry.py OUTPUTFILE')
    sys.exit()

record = False #flag to start recording geometry info to an output

with open(sys.argv[1]) as f: #this method automatically closes the file
  with open('last_geometry.in', 'w') as out:
    for line in f:
        linelist = line.split() #split the lines (str) into lists
        if linelist: #checks if the line is entirely empty
            if linelist[0] == 'Final' and linelist[1] == 'atomic':
              record = True  
            elif record == True and (linelist[0] == 'atom' or linelist[0] == 'lattice_vector'):
              printcurrent(linelist, out)


if record == True:
  print('Final geometry step outputed to last_geometry.in')

#TODO generalize code for non-final output as the last output in the final (aborted run) 
