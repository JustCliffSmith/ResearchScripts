#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  4 11:21:00 2018

@author: Justin Clifford Smith
"""

import numpy as np
from scipy.interpolate import griddata
import sys
import matplotlib.pyplot as plt
import os

if len(sys.argv) != 3:
  print("Usage: fhiPES.py outputPrefix adatomSymbol")
  sys.exit()

#initialize adatom arrays
x = np.array([])
y = np.array([])
z = np.array([]) #energy

final = False

#Get data for PES
for files in os.listdir('.'):
#get data for PES
  if files.startswith(sys.argv[1]):
    with open(files) as outputfile:
        print("Extracting PES data from {}".format(files))
        for line in outputfile:
            linelist = line.split()
            if linelist:
                if (linelist[0] == 'Final' and linelist[1] == 'atomic'):
                    final = True
                if (linelist[0] == 'atom' and linelist[-1] == sys.argv[2] \
                    and final == True):
                    x = np.append(x,linelist[1]).astype(np.float)
                    y = np.append(y,linelist[2]).astype(np.float)
                    final = False
                if (len(linelist) > 10  and linelist[1] == 'Total' \
                     and linelist[2] == 'energy' and linelist[3] == 'of'):
                    z = np.append(z,linelist[-2]).astype(np.float)
#get atomic positions for scatter plot
  if files.endswith(".in"): 
    print('Extracting atomic positions from {}'.format(files))
    xscIn = np.array([])
    yscIn = np.array([])
    zscIn = np.array([])
    xscAs = np.array([])
    yscAs = np.array([])
    zscAs = np.array([])
    latvec = np.array([])
    latcount = 0
    with open(files) as geometryfile:
      for line in geometryfile:
        linelist = line.split()
        if linelist:
          if linelist[0] == 'lattice_vector' and latcount < 2:
            latvec = np.append(latvec,linelist[1]).astype(np.float) #x
            latvec = np.append(latvec,linelist[2]).astype(np.float) #y
            latcount += 1 #only want first two lattice vectors
          if (linelist[0] == 'atom' and linelist[-1] == 'In' ):
            xscIn = np.append(xscIn,linelist[1]).astype(np.float)
            yscIn = np.append(yscIn,linelist[2]).astype(np.float)
            zscIn = np.append(zscIn,linelist[3]).astype(np.float)
          if (linelist[0] == 'atom' and linelist[-1] == 'As'):
            xscAs = np.append(xscAs,linelist[1]).astype(np.float)
            yscAs = np.append(yscAs,linelist[2]).astype(np.float)
            zscAs = np.append(zscAs,linelist[3]).astype(np.float)

#subtract off the largest negative value
z = np.subtract(z, np.amin(z))

[print("x: {: 02.4f}, y: {: 02.4f}, z: {: 02.4f}".format(xi,yi,zi)) \
      for (xi, yi, zi) in zip(x, y, z)]

#define the grid dimensions
xi = np.linspace(0, latvec[0] + latvec[2], 1000)
yi = np.linspace(0, latvec[3], 1000)
#grid the data
zi = griddata((x, y), z, (xi[None,:], yi[:,None]), method='cubic')
#draw the edges of the surface cell 
ax = plt.axes()
ax.arrow(0, 0, latvec[2], latvec[3], head_width=None, lw=1, color='k') # left
ax.arrow(0, 0, latvec[0], 0, head_width=None, lw=1, color='k') #bottom
ax.arrow(latvec[0], 0, latvec[2], latvec[3], head_width=None, lw=1, color='k') #right
ax.arrow(latvec[2], latvec[3], latvec[0], 0, head_width=None, lw=1, color='k') #top
#contour the gridded data, plotting dots
plt.contour(xi, yi, zi, 20, linewidths=0.5, colors='k')
plt.contourf(xi, yi, zi*2, 20, cmap=plt.cm.jet)
plt.colorbar() # draw colorbar
#plt.scatter(xscIn[-11:], yscIn[-11:], zscIn[-11:]**3/15, c='c', zorder=1)
#plt.scatter(xscAs[-8:], yscAs[-8:], zscAs[-8:]**3/15, c='k', zorder=1)
plt.scatter(xscIn[-7:], yscIn[-7:], 100*(zscIn[-7:]/zscIn[-1])**4, c='c', zorder=1)
plt.scatter(xscAs[-8:], yscAs[-8:], 100*(zscAs[-8:]/zscAs[-1])**4, c='k', zorder=1)
plt.scatter(x, y, 1000, c='r', zorder=1)
plt.xlim(0,latvec[0] + latvec[2])
plt.ylim(0,latvec[3] + .1)
#plt.savefig('PES_output.png', bbox_inches='tight')
plt.show()


