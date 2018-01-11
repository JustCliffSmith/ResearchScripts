#!/usr/bin/env python

#author: Justin Clifford Smith
#date: January 2, 2018

#Written in python 3.x

#This script reads an FHI-aims output file from  relaxation calculation 
#and creates a last_geometry.in with the final relaxation step.

import sys

def printcurrent(line, outfile):
  outfile.write(" ".join(str(x) for x in line))
  outfile.write("\n")

def printconstraint(cons, outfile):
  outfile.write("".join(str(x) for x in cons))
  outfile.write("\n")
  
if len(sys.argv) != 2:
    print('Usage: fhigeometry.py OUTPUTFILE')
    sys.exit()

    record = False #flag to start recording geometry info to an output
wrote = False #flag for if we wrote a complete output
constraintRecord = False #flag for recording constraints

constraints = {} #dictionary for constraints. Keys = atoms, items = constraints
atomCount = 0 #current atom being read in

with open(sys.argv[1]) as f:
  for line in f:
      linelist = line.split()
      if linelist: #checks if the line is entirely empty
          #extract constraint information
          if linelist[0] == 'Parsing' and linelist[1] == 'geometry.in':
            constraintRecord = True
          if constraintRecord == True and linelist[0] == 'atom':
            atomCount += 1
          if linelist[0] == 'constrain_relaxation':
            constraints.setdefault(atomCount, [])
            constraints[atomCount].append(linelist[0] + ' ' + linelist[1])
          if linelist[0] == 'Completed':
            constraintRecord = False
            atomCount = 0

          #extract geometry
          if (linelist[0] == 'Final' and linelist[1] == 'atomic') or \
              (linelist[0] == 'Updated' and linelist[1] == 'atomic'):
            out = open('last_geometry.in', 'w')
            record = True
          elif record == True and linelist[0] == 'lattice_vector':
            printcurrent(linelist, out)
          elif record == True and linelist[0] == 'atom':
            printcurrent(linelist, out)
            atomCount += 1
            if atomCount in constraints:
              for cons in constraints[atomCount]:
                printconstraint(cons, out)
          elif linelist[0] == 'Fractional':
            atomCount = 0
            record = False
            wrote = True
            out.close()

if wrote == True:
  print('Final geometry step outputed to last_geometry.in')

