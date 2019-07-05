
"""
Module to create topo and qinit data files for this example.
"""

from __future__ import absolute_import
import numpy as np


class MakeTopo():
    def __init__(self, nxpoints, nypoints,
                 xlower, ylower, xupper, yupper,
                 outfile, topo_type=2):
        self.nxpoints = nxpoints
        self.nypoints = nypoints
        self.xlower = xlower
        self.ylower = ylower
        self.xupper = xupper
        self.yupper = yupper
        self.outfile= outfile
        self.topo_type = topo_type

    def generate(self, topo_func):
        from clawpack.geoclaw.topotools import Topography

        topography = Topography(topo_func=topo_func)
        topography.x = np.linspace(self.xlower, self.xupper, self.nxpoints)
        topography.y = np.linspace(self.ylower, self.yupper, self.nypoints)
        topography.write(self.outfile,
                         topo_type=self.topo_type,
                         Z_format="%22.15e")


def topo(x, y):
    z = np.zeros_like(x) + 10
    for i in range(x.shape[0]):
        for j in range(x.shape[1]):
            if x[i, j] >= 0.0 and x[i, j] <= 50.0e3 and y[i, j] >= 0.0 and y[i, j] <= 40.0e3:
                p, q, r = np.array([0, 0, -35]), np.array([50e3, 0, -35]), np.array([0, 40e3, -10])
            elif x[i, j] >= 10.0e3 and x[i, j] <= 40.0e3 and y[i, j] >= 40.0e3 and y[i, j] <= 80.0e3:
                p, q, r = np.array([10e3, 40e3, -10]), np.array([40e3, 40e3, -10]), np.array([20e3, 80e3, -2])
            elif x[i, j] >= 20.0e3 and x[i, j] <= 30.0e3 and y[i, j] >= 80.0e3 and y[i, j] <= 130.0e3:
                p, q, r = np.array([20e3, 80e3, -2]), np.array([30e3, 80e3, -2]), np.array([20e3, 130e3, -1])
            else:
                continue
                
            pq = q - p
            pr = r - p

            a, b, c = np.cross(pq, pr)
            z[i, j] = p[2] - a / c * (x[i, j] - p[0]) - b / c * (y[i, j] - p[1])
    return z


if __name__=='__main__':
    tp = MakeTopo(201, 521, 0e0, 0e0, 50e3, 130e3, 'mobile_bay.topotype2')
    tp.topo_type = 2
    tp.generate(topo)
