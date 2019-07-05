import pandas as pd
from pathlib import Path
from geopy import distance
import utils


data = pd.read_csv('shape_data.csv')
left = data.loc[data.Lon.idxmin(), ['Lat', 'Lon']]
data['Distance'] = data.apply(lambda x: distance.geodesic(left, (x['Lat'], x['Lon'])).km, axis=1)

trap = data.loc[data.Shape == 'trapezoid', ['Lon', 'Lat', 'Rlb', 'Rbt', 'Distance']]
tri = data.loc[data.Shape == 'triangle', ['Lon', 'Lat', 'Rlb', 'Rbr', 'Distance']]

fig, gs, canvas = utils.make_canvas(5, 5)
ax = fig.add_subplot(gs[0])
tri.plot(kind='scatter', x='Distance', y='Rlb', marker='^', color='g', ax=ax)
trap.plot(kind='scatter', x='Distance', y='Rlb', marker='s', color='#FFA500', ax=ax)
ax.set_xlabel('Distance from Corpus Christi (km)')
ax.set_ylabel('$R_{lb} = \\dfrac{L_b}{W_b}$')
ax.legend(['Triangle', 'Trapezoid'])
canvas.print_figure("ratio.png", format="png", dpi=300);
