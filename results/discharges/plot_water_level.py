#!/usr/bin/env python
import pandas as pd
from pathlib import Path
from geopy import distance
import utils


data = pd.read_csv('Graph-1_WL_D0_4obspoints.csv', parse_dates=[0])
data.set_index('DateTime', drop=True, inplace=True)
hourly = data.groupby(pd.Grouper(freq='2H')).mean()

fig, gs, canvas = utils.make_canvas(8, 5)
ax = fig.add_subplot(gs[0])
hourly.plot(ax=ax)
ax.set_ylabel('Water Level (m)')
ax.set_xlabel('')
canvas.print_figure("water_level_loc.png", format="png", dpi=300);

data = pd.read_csv('Graph-2_WL_Mannings.csv', parse_dates=[0])
data.set_index('DateTime', drop=True, inplace=True)
hourly = data.groupby(pd.Grouper(freq='2H')).mean()

fig, gs, canvas = utils.make_canvas(8, 5)
ax = fig.add_subplot(gs[0])
hourly.plot(ax=ax)
ax.set_ylabel('Water Level (m)')
ax.set_xlabel('')
canvas.print_figure("water_level_man.png", format="png", dpi=300);

data = pd.read_csv('Velocity.csv', parse_dates=[0])
data.set_index('DateTime', drop=True, inplace=True)
hourly = data.groupby(pd.Grouper(freq='2H')).mean()

fig, gs, canvas = utils.make_canvas(8, 5)
ax = fig.add_subplot(gs[0])
hourly.plot(ax=ax)
ax.set_ylabel('Velocity (m/s)')
ax.set_xlabel('')
canvas.print_figure("velocity.png", format="png", dpi=300);

