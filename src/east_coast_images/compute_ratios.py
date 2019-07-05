import pandas as pd
import numpy as np
import geopandas as gpd
import shapely.geometry as sgeom
from pathlib import Path


la = 0.03 * 110.574
lo = 0.06 * 111.32 * np.cos(0.03)
di = np.sqrt(la**2 + lo**2)

data = []

def add_ratio(df, sh, lon, lat, wb, wr, lb, wt):
    return df.append([sh, lon, lat, wb, wr, lb, wt,
                     float(wb)/float(wr), float(lb)/float(wb),
                     float(wb)/float(wt)])

add_ratio(data, 'triangle', -66.46, 45.06, 2*di, 0.2*di, 1.5*di, np.nan)
add_ratio(data, 'trapezoid', -66.74, 45.07, di, 0.1*di, 1.5*di, di)
add_ratio(data, 'trapezoid', -67.27, 44.63, 2*di, 0.1*di, 3*la, 1.5*di)
add_ratio(data, 'triangle', -67.80, 44.52, 0.8*di, 0.05*di, 4*la, np.nan)
add_ratio(data, 'trapezoid', -67.80, 44.52, 1.2*di, 0.05*di, di, 1.1*di)
add_ratio(data, 'triangle', -70.64, 41.99, 4*la, 0.1*di, 1.5*di, np.nan)
add_ratio(data, 'trapezoid', -70.66, 41.60, 1.2*di, 0.05*di, di, 1.1*di)
add_ratio(data, 'triangle', -40.5, 73.9, 17, 2, 24, np.nan)
add_ratio(data, 'triangle', -41.0, 72.0, 28, 3, 158, np.nan)
add_ratio(data, 'trapezoid', -71.01, 42.31, 3*la, 0.3*la, 2*di, 2*la)
add_ratio(data, 'triangle', -71.38, 41.73, 1.5*di, 0.1*di, 4*la, np.nan)
add_ratio(data, 'triangle', -72.81, 41.26, 0.8*di, 0.1*di, di, np.nan)
add_ratio(data, 'triangle', -74.27, 40.49, 3*la, 0.3*la, 2*lo, np.nan)
add_ratio(data, 'trapezoid', -75.09, 38.62, 4*la, 0.3*la, 2*lo, 4*la)
add_ratio(data, 'triangle', -75.48, 39.34, 49, 4, 98, np.nan)
add_ratio(data, 'triangle', -75.74, 37.92, 35, 4, 241, np.nan)
add_ratio(data, 'triangle', -75.85, 38.02, 1.1*di, 0.1*la, 3*di, np.nan)
add_ratio(data, 'triangle', -66.46, 45.06, 2*di, 0.05*la, 2*di, np.nan)
add_ratio(data, 'trapezoid', -67.15, 44.83, 28, 1, 35, 15)


data = pd.DataFrame(data)
data.columns=['Shape', 'Lon', 'Lat',
              'Wb', 'Wr', 'Lb','Wt',
              'Rbr', 'Rlb', 'Rbt']

for f in ['john.csv', 'gustavo.csv']:
    df = pd.read_csv(f)
    df['Rbr'] = df.Wb / df.Wr
    df['Rlb'] = df.Lb / df.Wb
    df['Rbt'] = df.Wb / df.Wt
    data = pd.concat([data, df]).reset_index(drop=True)

data = data.sort_values('Shape').reset_index(drop=True)

ratio_min = data[['Shape', 'Rbr', 'Rlb', 'Rbt']].groupby('Shape').min()
ratio_max = data[['Shape', 'Rbr', 'Rlb', 'Rbt']].groupby('Shape').max()
ratio_range = pd.concat([ratio_min, ratio_max], keys=['R_min', 'R_max'])

points = gpd.GeoDataFrame(sgeom.MultiPoint([sgeom.Point(lon, lat) for lon, lat in zip(data.Lon, data.Lat)]))
points.columns = ['geometry']

data.to_csv('shape_data.csv', index=None)
points.to_file(Path('gis_data', 'classification', 'classification.shp'))
plot_coords(Path('gis_data', 'east_coast', 'east_coast.shp'))
