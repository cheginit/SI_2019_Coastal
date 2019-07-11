#!/usr/bin/env python
import xarray as xr
import pandas as pd
import numpy as np
import multiprocessing
from pathlib import Path
import utils
from sys import argv


fname = argv[1:]

label = [Path(f).parent.name.replace('_', ' ') for f in fname]
res = [xr.open_dataset(f) for f in fname]

nx, ny = res[0].variables['mesh2d_face_x'], res[0].variables['mesh2d_face_y']*1e-3
time = pd.to_datetime(res[0].variables['time'].values)
wd = [r.variables['mesh2d_s1'] for r in res]

center = np.where((nx > 25000 - 200) & (nx < 25000))

wd_center = [w.values[:,center] for w in wd]
ny_center = ny[center]

xmin = np.array([w.min() for w in wd_center]).min()
xmax = np.array([w.max() for w in wd_center]).max()

def plot(t):
    import matplotlib.colors as mcolors

    output = Path('images', f'compare_{t:03d}.png')
    if output.exists():
        return

    fig, gs, canvas = utils.make_canvas(8, 5)
    ax = fig.add_subplot(gs[0])

    color = list(mcolors.TABLEAU_COLORS.keys())[:len(label)]
    for w, l, c in zip(wd_center, label, color):
        ax.plot(ny_center,
                w[t][0],
                label=f'{l}',
                c=c)

    ax.set_title('Cross-section across the middle of the domain')
    ax.set_xlim(ny_center.min(), ny_center.max())
    ax.set_ylim(xmin - 0.5, xmax + 0.5)
    ax.set_xlabel('Distance (km)')
    ax.set_ylabel('Water Level (m)')
    ax.legend(loc='upper right')
    canvas.print_figure(output, format="png", dpi=300);


if __name__ == '__main__':
    import time as dt
    import subprocess

    print('Plotting in parallel ...')
    starttime = dt.time()
    pool = multiprocessing.Pool()
    pool.map(plot, range(0, time.shape[0], 1))
    pool.close()
    print(f'Plotting finished after {dt.time() - starttime:.1f} seconds')

    print('Making animation from the plots ...')
    output_loc = Path('images', 'compare_%03d.png')
    clip_loc = Path('waterlevel.mp4')

    p = subprocess.Popen(['ffmpeg',
                          '-hide_banner',
                          '-loglevel', 'panic',
                          '-y',
                          '-i', output_loc,
                          clip_loc])
    p.communicate()
    print('Completed successfully')
