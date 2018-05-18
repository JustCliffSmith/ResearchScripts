#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plots the potential energy surface from a collection of FHI-aims calculations.

Given a collection off FHI-aims calculations of adatoms on a surface

This script takes a collection of FHI-aims surface calculations
(surface perpendicular to the z-direction) with a single adatom adsorbed
and plots three potential energy surface (PES):
* The data as is
* The data with user specified symmetry operations
* Same as 2 but repeated in the x and y direction.

Transition state paths can be plotted on top of the surface using path.xyz
files generated by the aimsChain code. In principle other codes can be used 
too as long as they have the same file format.


Author: Justin Clifford Smith

TODO: implement symmetry operations
"""

import sys
import os
import argparse
import numpy as np
from scipy.interpolate import griddata
import matplotlib.pyplot as plt


def extract_PES_data(file_name, adatom, x, y, z):
    """ Return PES data as three arrays."""
    final = False
    with open(file_name) as outputfile:
        print("Extracting PES data from {}".format(file_name))
        for line in outputfile:
            linelist = line.split()
            if linelist:
                if (linelist[0] == 'Final' and linelist[1] == 'atomic'):
                    final = True
                if (linelist[0] == 'atom' and linelist[-1] == args.adatom \
                    and final == True):
                    x = np.append(x,linelist[1]).astype(np.float)
                    y = np.append(y,linelist[2]).astype(np.float)
                    final = False
                if (len(linelist) > 10  and linelist[1] == 'Total' \
                     and linelist[2] == 'energy' and linelist[3] == 'of'):
                    z = np.append(z,linelist[-2]).astype(np.float)
    return x, y, z

def extract_latvec(file_name):
    """ Return lattice vectors from an output file as a flat array. """
    latvec = np.array([])
    with open(file_name) as outputfile:
        for line in outputfile:
            linelist = line.split()
            if linelist:
                if linelist[0] == 'lattice_vector':
                    latvec = np.append(latvec, linelist[1]).astype(np.float) #x
                    latvec = np.append(latvec, linelist[2]).astype(np.float) #y
                    latvec = np.append(latvec, linelist[3]).astype(np.float) #z
    return latvec

def make_grid(latvec, x, y, z):
    """ Makes grid for plotting.
    
    xi and yi are evenly spaced based off the lattive vector.
    zi is a cubic interpolation of the z data and xi and yi.
    """
    
    xi = np.linspace(0, (latvec[0] + latvec[3])*2, 1000)
    yi = np.linspace(0, latvec[4]*2, 1000)
    zi = griddata((x, y), z, (xi[None,:], yi[:,None]), method='cubic')    
    return xi, yi, zi

def draw_cell(ax, amt=1):
    """ Draw the unit cell on the PES. If amt=2 then draws a 2x2 cell."""
    ax.arrow(latvec[0], 0, amt*latvec[3], amt*latvec[4], head_width=None, lw=1, color='k') # middle vertical
    ax.arrow(latvec[3], latvec[4], amt*latvec[0], 0, head_width=None, lw=1, color='k') #middle horizontal
    ax.arrow(0, 0, amt*latvec[3], amt*latvec[4], head_width=None, lw=1, color='k') # left
    ax.arrow(0, 0, amt*latvec[0], 0, head_width=None, lw=1, color='k') #bottom
    ax.arrow(amt*latvec[0], 0, amt*latvec[3], amt*latvec[4], head_width=None, lw=1, color='k') #right
    ax.arrow(amt*latvec[3], amt*latvec[4], amt*latvec[0], 0, head_width=None, lw=1, color='k') #top
    ax.set_aspect('equal', 'box')

def plot_PES(args, amt, outname):
    """ Plot the PES where amt is if plotting 1 cell or a 2x2. """
    plt.figure(figsize=(amt*6.4, amt*4.8))
    xi, yi, zi = make_grid(latvec, x, y, z)
    ax = plt.axes()
    draw_cell(ax, amt)
    #contour the gridded data, plotting dots
    plt.contour(xi, yi, zi, 30, linewidths=0.5, colors='k')
    plt.contourf(xi, yi, zi, 30, cmap=plt.cm.jet)
    if amt == 1:
        plt.colorbar()
    if amt == 2:
        plt.colorbar(orientation='horizontal', pad=0.05)
    if args.debug:
        plt.scatter(x, y, 600, c='r', zorder=1, alpha=.5)
    for path in args.path:
        plot_path(plt, args.adatom, path)
    plt.xlim(0, amt*(latvec[0] + latvec[3]))
    plt.ylim(0, amt*latvec[4] + .1)
    plt.savefig(outname, bbox_inches='tight')
    plt.show()

def translate_x(x, y, z, latvec, amt):
  """Translate the data by lattice vectors in the x-direction by integer amt."""
  x = np.append(x, np.add(x, amt*latvec[0])) 
  y = np.append(y, y)
  z = np.append(z, z)                    
  return x, y, z

def translate_y(x, y, z, latvec, amt):
  """Translate the data by lattice vectors in the y-direction by integer amt."""
  x = np.append(x, np.add(x, amt*latvec[3])) 
  y = np.append(y, np.add(y, amt*latvec[4]))
  z = np.append(z, z)                    
  return x, y, z

def translate_xy(x, y, z, latvec, amt):
  """Translate the data by lattice vectors in the xy-direction by integer amt."""
  x = np.append(x, np.add(x, amt*(latvec[0] + latvec[3]))) 
  y = np.append(y, np.add(y, amt*latvec[4]))
  z = np.append(z, z)                    
  return x, y, z

def get_path(adatom, path_file):
    """ Extracts the NEB path from the given path file in xyz format."""
    NEB_path = []
    with open(path_file, 'r') as file:
        for line in file:
            linelist = line.split()
            if linelist[0] == adatom:
                x = linelist[1]
                y = linelist[2]
                z = linelist[3]
                NEB_path.append((x, y, z))
    return np.array(NEB_path).astype(np.float)

def plot_path(plot, path):
    """ Add an NEB path to the plot. """
    plot.scatter(path[0], path[1], 120, c='k', alpha=0.75)

def plot_path(plot, adatom, path_file):
    path = get_path(adatom, path_file)
    path_xyz = []
    for i in [0,1,2]:
        path_xyz.append(list(zip(*path))[i])
    plot.scatter(path_xyz[0], path_xyz[1], 120, c='k', alpha=0.75)


parser = argparse.ArgumentParser()
parser.add_argument("file_prefix", help="File prefix of fhiAIMS calculations"
                    ", e.g. \"output.\".")
parser.add_argument("adatom", help="Adatom on surface")
parser.add_argument("-path", nargs='*', help="Specify all path files.")
parser.add_argument("--debug", action="store_true", 
                    help="Plots the adatom positions.")
args = parser.parse_args()

#TODO arg for symmetry

#initialize adatom arrays
x = np.array([])
y = np.array([])
z = np.array([]) #energy

for f in os.listdir('.'):
  if f.startswith(args.file_prefix):
    x, y, z = extract_PES_data(f, args.adatom, x, y, z)    
    # Only need to extract latvec once.
    try:
        latvec
    except NameError:
        latvec = extract_latvec(f)

# Subtract off the largest negative value.
z = np.subtract(z, np.amin(z))

# Print out adsorption sites and adjusted energies.
print('Extracted adsorption sites and adjusted energies:')
[print("x: {: 02.4f}, y: {: 02.4f}, z: {: 02.4f}".format(xi,yi,zi)) \
      for (xi, yi, zi) in zip(x, y, z)]

### No transformation
plot_PES(args, 1, 'PES_notransform.png')

### Transformation and then plot

# Symmetry operations to get full surface

# Mirror symmetry along x-y direction
m = latvec[4]/(latvec[0]+latvec[3])
pref = 1/ (1 + m**2)
refmat = np.array([[pref*(1-m**2), pref*2*m, 0], [pref*2*m, pref*(m**2 -1), 0] , [0, 0, 1]])
xyz = np.array([x, y, z])
xyzref = np.dot(refmat, xyz)
x = np.append(x, xyzref[0])
y = np.append(y, xyzref[1])
z = np.append(z, xyzref[2])


rotarg = 2*np.pi/3
rotmat = np.array([[np.cos(rotarg), np.sin(rotarg), 0], [-np.sin(rotarg), np.cos(rotarg), 0] , [0, 0, 1]])

# shift the origin to the center of the cell
x = np.add(x, -(latvec[0]+latvec[3])/2)
y = np.add(y, -latvec[4]/2)

xyz = np.array([x, y, z])

xyzrot = np.dot(rotmat,xyz)
xyzrotrot = np.dot(rotmat,xyzrot)
x = np.append(x, xyzrot[0])
y = np.append(y, xyzrot[1])
z = np.append(z, xyzrot[2])
x = np.append(x, xyzrotrot[0])
y = np.append(y, xyzrotrot[1])
z = np.append(z, xyzrotrot[2])

# shift the origin back to 0, 0
x = np.add(x, (latvec[0]+latvec[3])/2)
y = np.add(y, latvec[4]/2)

plot_PES(args, 1, 'PES.png')

### Plot a 2x2 grid of unit cells ###
# Translate the data into x, y, and x-y directions
for i in [1, 2, -1]:
  x, y, z = translate_x(x, y, z, latvec, i)
  x, y, z = translate_y(x, y, z, latvec, i)
  x, y, z = translate_xy(x, y, z, latvec, i)

plot_PES(args, 2, 'PES_big.png')

