#!/usr/bin/env python
"""e2dfm.py: A python script to convert exodus II file to netCDF(ugrid-0.9) for Delft3D-FM use.

To use, edit the path in ni_file
The output is in the same folder with the same file name but a .nc extension

"""
__author__ = "Ruo-Qian Wang"
__copyright__ = "Copyright 2016"
__license__ = "GPL"
__version__ = "0.11"
__maintainer__ = "Ruo-Qian Wang"
__email__ = "wangruoqian@gmail.com"
__status__ = "Production"

import os
import netCDF4
import numpy as np

#matplotlib inline
#from matplotlib.patches import Polygon
#from matplotlib.collections import PatchCollection
#import matplotlib.pyplot as plt
#import matplotlib.tri as tri
#from matplotlib.tri import Triangulation, UniformTriRefiner, CubicTriInterpolator
#import matplotlib.cm as cm
#import matplotlib

# Open exodus data for reading
print(" ===============================================\n")
print(" Script converting exodus to CF-ugrid-0.9 netCDF  \n")
print(" ===============================================\n")

ni_file='./mesh.e'     # change to your own file path
file_len=len(ni_file)

ni = netCDF4.Dataset(ni_file,'r',format='NETCDF3_64BIT')    # open file for reading

nNetNode = ni.dimensions['num_nodes']       # reading dimensions data
nNetLink = ni.dimensions['num_elem']
nNetLinkPts = ni.dimensions['num_nodes']

X = ni.variables['coord'][0]              # reading variable data
Y = ni.variables['coord'][1]
connect = ni.variables['connect1']

# Analyzing grid
ghash=dict()
links_data=[]
bnd_nodes=[]
for elm in connect:                 # counting edges
    for i in range(0,3):
        node0=elm[i]
        node1=elm[(i+1)%3]
        if node1<node0:
            node=node1
            node1=node0
            node0=node
        link=str(node0)+'-'+str(node1)
        if (link in ghash):
            ghash[link]=ghash[link]+1
        else:
            ghash[link]=1
            links_data.append([node0,node1])
#            if (not node0 in bnd_nodes):
#                bnd_nodes.append(node0)
#            if (not node1 in bnd_nodes):
#                bnd_nodes.append(node1)
        
nNetLink=len(ghash)
#nBndLink=len(bnd_nodes)

# Opening nc data for writing
no_file=ni_file[0:file_len-1]+'nc'
print("Converting from ", ni_file, "to ", no_file, "\n")
try:
    os.remove(no_file)
except OSError:
    pass

no = netCDF4.Dataset(no_file,'w',format='NETCDF3_CLASSIC') 

# Creating ugrid-0.9 framework
#	dimensions
no.createDimension('nNetNode',nNetNode.size)
no.createDimension('nNetLink',nNetLink)
no.createDimension('nNetLinkPts',2)
#no.createDimension('nBndLink',nBndLink)

#	varialbles
Mesh2D=no.createVariable('Mesh2D','i4')
Mesh2D.setncattr('cf-type',"mesh_topology")
Mesh2D.setncattr('topology_dimension',2)
Mesh2D.setncattr('node_coordinates',"NetNode_x NetNode_y")
Mesh2D.setncattr('face_node_connectivity',"NetElemNode")
Mesh2D.setncattr('edge_node_connectivity',"NetLink")

NetNode_x=no.createVariable('NetNode_x','f8','nNetNode')
NetNode_x.setncattr('units',"m")
NetNode_x.setncattr('standard_name',"projection_x_coordinate")
NetNode_x.setncattr('long_name',"x-coordinate of net nodes")

NetNode_y=no.createVariable('NetNode_y','f8','nNetNode')
NetNode_y.setncattr('units',"m")
NetNode_y.setncattr('standard_name',"projection_y_coordinate")
NetNode_y.setncattr('long_name',"y-coordinate of net nodes")

#projected_coordinate_system=no.createVariable('projected_coordinate_system','i4')
#projected_coordinate_system.setncattr('name',"Unknown projected")
#projected_coordinate_system.setncattr('epsg',28992)
#projected_coordinate_system.setncattr('grid_mapping_name',"Unknown projected")
#projected_coordinate_system.setncattr('longitude_of_prime_medidian',0.)
#projected_coordinate_system.setncattr('semi_major_axis',6378137.)
#projected_coordinate_system.setncattr('semi_minor_axis',6356752.314245)
#projected_coordinate_system.setncattr('inverse_flattening',298.257333563)
#projected_coordinate_system.setncattr('epsg_code',"EPGS:28992")
#projected_coordinate_system.setncattr('value',"value is equal to EPSG code")

#NetNode_lon=no.createVariable('NetNode_lon','f8','nNetNode')
#NetNode_lon.setncattr('units',"degrees_east")
#NetNode_lon.setncattr('standard_name',"longitude")
#NetNode_lon.setncattr('long_name',"longitude")

#NetNode_lat=no.createVariable('NetNode_lat','f8','nNetNode')
#NetNode_lat.setncattr('units',"degrees_north")
#NetNode_lat.setncattr('standard_name',"latitude")
#NetNode_lat.setncattr('long_name',"latitude")

NetNode_z=no.createVariable('NetNode_z','f8','nNetNode')
NetNode_z.setncattr('units',"m")
NetNode_z.setncattr('positive',"up")
NetNode_z.setncattr('standard_name',"sea_floor_depth")
NetNode_z.setncattr('long_name',"Bottom level at net nodes (flow element\'s corners)")
NetNode_z.setncattr('coordinates',"NetNode_x NetNode_y")
NetNode_z.setncattr('mesh',"Mesh2D")
NetNode_z.setncattr('location',"node")

NetLink=no.createVariable('NetLink','i4',['nNetLink','nNetLinkPts'])
NetLink.setncattr('standard_name',"netlink")
NetLink.setncattr('long_name',"link between two netnodes")

NetLinkType=no.createVariable('NetLinkType','i4','nNetLink')
NetLinkType.setncattr('long_name',"Type of netlink")
NetLinkType.setncattr('flag_values',[0,1,2])
NetLinkType.setncattr('flag_meanings',"closed_link_between_2D_nodes link_between_1D_nodes link_between_2D_nodes")

#BndLink=no.createVariable('BndLink','i4','nBndLink')
#BndLink.setncattr('long_name',"Netlinks that compose the net boundary.")

no.setncattr('Conventions',"UGRID-0.9")

NetNode_x[:] = X[:]
NetNode_y[:] = Y[:]
NetNode_z[:] = np.zeros(nNetNode.size)

NetLink[:] = links_data
NetLinkType[:] = np.ones(nNetLink)*2

#bnd_nodes.sort()
#BndLink[:] = bnd_nodes

# plotting grid
#fig, ax = plt.subplots()
#print X
#triang = tri.Triangulation(X, Y)
#plt.triplot(triang)

#plt.plot(X[:],Y[:],'ro')
#plt.show()

# close files
ni.close()
no.close()
