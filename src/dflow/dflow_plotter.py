#!/usr/bin/env python

import xarray as xr
import utils
from pathlib import Path
from sys import argv
import itertools
import vis


dirname = argv[1:]
res_list, inp_list = [], []
for d in dirname:
    fname = [Path(d, n) for n in ['FlowFM_map.nc', 'inputs.txt']]
    for f in fname:
        if not Path(f).exists():
            raise FileNotFoundError(f'{f} not found')

    res_list.append(xr.open_dataset(fname[0]))
    inp_list.append(utils.read_data(fname[1]))

plot_id = [inp['plot'] for inp in inp_list]

wl_idx = [i for i, f in enumerate(plot_id) if f[0] == 'T']
cs_idx = [i for i, f in enumerate(plot_id) if f[1] == 'T']
tc_idx = [i for i, f in enumerate(plot_id) if f[2] == 'T']

res, inp = list(itertools.compress(res_list, wl_idx)), list(itertools.compress(inp_list, wl_idx))
if len(res) > 0 and len(inp) > 0:
    water_level = vis.WaterSurface(res, inp)
    water_level.animate()

res, inp = list(itertools.compress(res_list, cs_idx)), list(itertools.compress(inp_list, cs_idx))
#if len(res) > 0 and len(inp) > 0:
#    cross_section = vis.CrossSection(res, inp)
#    cross_section.animate()

res, inp = list(itertools.compress(res_list, tc_idx)), list(itertools.compress(inp_list, tc_idx))
if len(res) > 0 and len(inp) > 0:
    tidal_constituents = vis.TidalConstituents(res, inp)
    tidal_constituents.plot_constituents()
    tidal_constituents.plot_mouth()
