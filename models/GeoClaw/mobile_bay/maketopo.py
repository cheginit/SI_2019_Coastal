"""
Module to create topo and qinit data files for this example.
"""

from __future__ import absolute_import
import numpy as np


class MakeTopo():
    def __init__(self, bay, outfile, topo_type=2):
        self.nxpoints = np.int64(4.0 *
                                 (bay.x_o2 - bay.x_o1) / bay.cell_size) + 1
        self.nypoints = np.int64(4.0 * (bay.y_r - bay.y0) / bay.cell_size) + 1
        self.xlower = bay.x_o1
        self.ylower = bay.y0
        self.xupper = bay.x_o2
        self.yupper = bay.y_r
        self.outfile = outfile
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
    from bay import Bay
    z = np.zeros_like(x) + 10

    mobile = Bay('bay.info')

    for i in range(x.shape[0]):
        for j in range(x.shape[1]):
            if x[i, j] >= mobile.x_o1 and \
               x[i, j] <= mobile.x_o2 and \
               y[i, j] >= mobile.y0 and \
               y[i, j] <= mobile.y_o:

                p = np.array([mobile.x_o1, mobile.y0, mobile.z0])
                q = np.array([mobile.x_o2, mobile.y0, mobile.z0])
                r = np.array([mobile.x_o1, mobile.y_o, mobile.z_o])
            elif x[i, j] >= mobile.x_b1 and \
                    x[i, j] <= mobile.x_b2 and \
                    y[i, j] >= mobile.y_o and \
                    y[i, j] <= mobile.y_b:

                p = np.array([mobile.x_b1, mobile.y_o, mobile.z_o])
                q = np.array([mobile.x_b2, mobile.y_o, mobile.z_o])
                r = np.array([mobile.x_b3, mobile.y_b, mobile.z_b])
            elif x[i, j] >= mobile.x_r1 and \
                    x[i, j] <= mobile.x_r2 and \
                    y[i, j] >= mobile.y_b and \
                    y[i, j] <= mobile.y_r:

                p = np.array([mobile.x_r1, mobile.y_b, mobile.z_b])
                q = np.array([mobile.x_r2, mobile.y_b, mobile.z_b])
                r = np.array([mobile.x_r1, mobile.y_r, mobile.z_r])
            else:
                continue

            pq = q - p
            pr = r - p

            a, b, c = np.cross(pq, pr)
            z[i, j] = p[2] - a / c * (x[i, j] - p[0]) - b / c * (y[i, j] -
                                                                 p[1])
    return z


if __name__ == '__main__':
    from bay import Bay
    import reader as io

    mobile = Bay('bay.info')

    tp = MakeTopo(mobile, 'mobile_bay.topotype2')
    tp.topo_type = 2
    tp.generate(topo)

    io.tide_data('data', 'low')
    io.discharge_data('data/discharge.bc', 'low', mobile)
