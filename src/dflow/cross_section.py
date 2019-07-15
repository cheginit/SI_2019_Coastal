#!/usr/bin/env python

import xarray as xr
import numpy as np
from pathlib import Path
import utils
from sys import argv


def plot(t):
    import matplotlib.colors as mcolors

    output = Path('images', f'frame_{t:03d}.png')
    if output.exists():
        return

    fig, gs, canvas = utils.make_canvas(8, 5)
    ax = fig.add_subplot(gs[0])

    colors = list(mcolors.TABLEAU_COLORS.keys())[:len(wd_center)]
    for w, l, c in zip(wd_center, labels, colors):
        ax.plot(ny_center, w[t][0], label=f'{l}', c=c)

    ax.set_title('Cross-section across the middle of the domain (y-direction)')
    ax.set_xlim(ny_center.min(), ny_center.max())
    ax.set_ylim(ymin, ymax)
    ax.set_xlabel('Distance (m)')
    ax.set_ylabel('Water Level (m)')
    ax.legend(loc='upper right')
    ax.ticklabel_format(style='sci', axis='x', scilimits=(3, 3))
    canvas.print_figure(output, format="png", dpi=300)


dirname = argv[1:]
res_list, inp_list = [], []
for d in dirname:
    fname = [Path(d, n) for n in ['FlowFM_map.nc', 'inputs.txt']]
    for f in fname:
        if not Path(f).exists():
            raise FileNotFoundError(f'{f} not found')

    res_list.append(xr.open_dataset(fname[0]))
    inp_list.append(utils.read_data(fname[1]))

nx, ny = res_list[0].mesh2d_face_x.values, res_list[0].mesh2d_face_y.values
center = np.where((nx > inp_list[0]['x_center'] - 200)
                  & (nx < inp_list[0]['x_center']))
ny_center = ny[center]
wd_center = [res.mesh2d_s1.values[:, center] for res in res_list]

ymax = np.array([np.ceil(abs(res.mesh2d_s1.values.max()))
                 for res in res_list]).max()
ymin = -ymax

labels = [inp['label'] for inp in inp_list]

utils.animation(plot, range(0, res_list[0].time.shape[0], 1),
                inp_list[-1]['label'].replace(' ', ''))
