import geopandas as gpd
import shapely.geometry as sgeom
from pathlib import Path


def get_us_east_coast(gis_data):    
    import numpy as np


    gobal_coast = gpd.read_file(Path(gis_data, 'global_coast', 'GSHHS_h_L1.shp'))
    conus = gobal_coast.geometry[3]

    coordsList = [sgeom.Point(-98.65, 25.82),
                  sgeom.Point(-75.95, 24.12),
                  sgeom.Point(-78.91, 30.84),
                  sgeom.Point(-66.18, 44.87),
                  sgeom.Point(-66.63, 45.19),
                  sgeom.Point(-102.01, 25.25)]
    poly = sgeom.Polygon([[p.x, p.y] for p in coordsList])
    conus_points = sgeom.MultiPoint(list(conus.exterior.coords))
    inside_idx = np.where([p.within(poly) for p in conus_points])[0]
    east = sgeom.MultiPoint([conus_points[i] for i in in_idx])
    east = gpd.GeoDataFrame(east)
    east.columns = ['geometry']
    east.to_file(gis_data + 'east_coast.shp')


def get_image(lon, lat):
    import matplotlib
    matplotlib.use('Agg')

    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    from cartopy.io.img_tiles import Stamen
    from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER


    img = Path('images', f'coast_{lon:.2f}_{lat:.2f}.png')
    if Path(img).exists():
        return

    tiler = Stamen('toner')
    mercator = tiler.crs

    from matplotlib.figure import Figure
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    import matplotlib.gridspec as gridspec

    fig = Figure(figsize=(7, 7), frameon=False, dpi=300)
    canvas = FigureCanvas(fig)
    gs = gridspec.GridSpec(1, 1,
                           left=0.15, right=0.95, bottom=0.15, top=0.95,
                           wspace=None, hspace=None,
                           width_ratios=None, height_ratios=None)
    ax = fig.add_subplot(gs[0], projection=mercator)

    x_width = 0.3
    y_width = 0.2
    ax.set_extent([lon - x_width*0.5,
                   lon + x_width*0.5,
                   lat - y_width*0.3,
                   lat + y_width*0.7], crs=ccrs.PlateCarree())

    ax.add_image(tiler, 14)
    #ax.coastlines('10m')

    gl = ax.gridlines(draw_labels=True)
    gl.xlabels_top = gl.ylabels_right = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    canvas.print_figure(img, format="png", dpi=300)
    plt.close('all')


def get_coords(gis_data='gis_data', skip_step=50):
    from joblib import Parallel, delayed
    
    
    if gis_data == None:
        gis_data = 'gis_data'

    if skip_step == None:
        skip_step = 50

    east_coast = gpd.read_file(Path(gis_data, 'east_coast', 'east_coast.shp'))
    east_coast_coords = sgeom.MultiPoint(east_coast.geometry.values)
    Parallel(n_jobs=2, prefer="threads")(delayed(get_image)(i.x, i.y) for i in east_coast_coords[::skip_step])
    #[get_image(i.x, i.y) for i in east_coast_coords[::skip_step]]


if __name__ == '__main__':
    from sys import argv

    if len(argv) > 1:
        skip_step, gis_data = int(argv[1]), argv[2]
    else:
        skip_step, gis_data = None, None

    get_coords(gis_data, skip_step)