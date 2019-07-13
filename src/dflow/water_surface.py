#!/usr/bin/env python

import xarray as xr
import numpy as np
from pathlib import Path
import utils
from sys import argv
from scipy.interpolate import griddata
from matplotlib import tri, cm


def plot(t):
    output = Path('images', f'frame_{t:03d}.png')
    if output.exists():
        return

    fig, gs, canvas = utils.make_canvas(5, 7)
    ax = fig.add_subplot(gs[0])

    wdt = griddata((nx, ny),
                   wd.isel(time=t).values,
                   (triang.x, triang.y),
                   method='linear')

    tcf = ax.tricontourf(triang, wdt, levels,
                         cmap=cm.get_cmap(cmap, len(levels) - 1),
                         norm=norm)
    ax.tricontour(triang, wdt, tcf.levels, colors='k')

    #ax.set_aspect('equal')
    ax.set_title(inp['label'].strip())
    ax.set_xlim(nx.min(), nx.max())
    ax.set_ylim(ny.min(), ny.max())
    ax.ticklabel_format(style='sci', scilimits=(3,3))
    fig.colorbar(tcf, norm=norm, ax=ax, use_gridspec=True, extend=[vmin, vmax])
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

vmax = np.array([np.ceil(abs(res.mesh2d_s1.values.max())) for res in res_list]).max()
vmin = -vmax
itr = 0

for res, inp in zip(res_list, inp_list):
    nx, ny = res.mesh2d_face_x.values, res.mesh2d_face_y.values
    wd = res.mesh2d_s1

    norm = cm.colors.Normalize(vmax=vmax, vmin=vmin)
    cmap = cm.PRGn
    levels = np.arange(vmin, vmax, 0.05)

    triang = tri.Triangulation(nx, ny)
    x = nx[triang.triangles].mean(axis=1)
    y = ny[triang.triangles].mean(axis=1)

    m = []
    if inp['class'] == 1:
        m.append(np.where((x > inp['x_o1']) &
                          (x < inp['x_r1']) &
                          (y > inp['y_o']),
                          1, 0))
        m.append(np.where((x > inp['x_r2']) &
                          (x < inp['x_o2']) &
                          (y > inp['y_o']),
                          1, 0))
    else:
        if (inp['x_b3'] - inp['x_b1']) < 1e-2:
            s_w, s_e = 0e0, 0e0
        else:
            s_w = (inp['y_r'] - inp['y_b']) / (inp['x_b3'] - inp['x_b1'])
            s_e = (inp['y_r'] - inp['y_b']) / (inp['x_b4'] - inp['x_b2'])

        m.append(np.where((x > inp['x_o1']) &
                          (x < inp['x_b1']) &
                          (y > inp['y_o']),
                          1, 0))
        m.append(np.where((x > inp['x_b2']) &
                          (x < inp['x_o2']) &
                          (y > inp['y_o']),
                          1, 0))
        m.append(np.where((x > inp['x_b1']) &
                          (x < inp['x_b3']) &
                          (y > inp['y_b']),
                          1, 0))
        m.append(np.where((x > inp['x_b4']) &
                          (x < inp['x_b2']) &
                          (y > inp['y_b']),
                          1, 0))
        m.append(np.where((x > inp['x_b3']) &
                          (x < inp['x_r1']) &
                          (y > inp['y_b']),
                          1, 0))
        m.append(np.where((x > inp['x_r2']) &
                          (x < inp['x_b4']) &
                          (y > inp['y_b']),
                          1, 0))
        m.append(np.where((x > inp['x_b1']) &
                          (x < inp['x_b3']) &
                          (y > inp['y_b'] + s_w * (x - inp['x_b1'])),
                          1, 0))
        m.append(np.where((x > inp['x_b4']) &
                          (x < inp['x_b2']) &
                          (y > inp['y_b'] + s_e * (x - inp['x_b2'])),
                          1, 0))

    mask = m[0]
    for i in m[1:]:
        mask = mask + i
    mask[mask > 1] = 1

    triang.set_mask(mask)

    utils.animation(plot,
                    range(0, wd.time.shape[0], 1),
                    inp['label'].replace(' ', ''))
    if itr > 0:
        wd = res_list[0].mesh2d_s1 - wd
        inp['label'] = 'RDiff ' + inp['label']
        utils.animation(plot,
                        range(0, wd.time.shape[0], 1),
                        inp['label'].replace(' ', ''))
    itr =+ 1
