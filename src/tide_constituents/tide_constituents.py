import pandas as pd
from shapely.ops import nearest_points
from shapely.geometry import Point, MultiPoint
from py_noaa import coops
from tappy import tappy


def get_tides(start, end, lon, lat):
    """
    date format: YYYYDDMM
    Returns: phase, amplitude
    """
    stations = pd.read_csv('noaa_stations.csv', parse_dates=[1])
    coords = [Point(ln, lt) for ln, lt in zip(stations.Longitude, stations.Latitude)]
    nearest_station_loc = nearest_points(Point(lon, lat), MultiPoint(coords))[1]
    idx = coords.index(nearest_station_loc)

    df_water_levels = coops.get_data(
        begin_date=start,
        end_date=end,
        stationid=stations.iloc[idx].ID,
        product="water_level",
        datum="MSL",
        units="metric",
        time_zone="gmt")
    
    dates = pd.to_datetime(df_water_levels.index) # a datetime.datetime list of dates
    elevation = df_water_levels.water_level.values # a list of surface elevation values

    # Set up the bits needed for TAPPY. This is mostly lifted from
    # tappy.py in the baker function "analysis" (around line 1721).
    quiet = True
    debug = False
    outputts = True
    outputxml = 'mobile.xml'
    ephemeris = False
    rayleigh = 1.0
    print_vau_table = False
    missing_data = 'ignore'
    linear_trend = False
    remove_extreme = False
    zero_ts = None
    filter = None
    pad_filters = None
    include_inferred = True

    if rayleigh:
        ray = float(rayleigh)

    x = tappy.tappy(
        outputts = outputts,
        outputxml = outputxml,
        quiet=quiet,
        debug=debug,
        ephemeris=ephemeris,
        rayleigh=rayleigh,
        print_vau_table=print_vau_table,
        missing_data=missing_data,
        linear_trend=linear_trend,
        remove_extreme=remove_extreme,
        zero_ts=zero_ts,
        filter=filter,
        pad_filters=pad_filters,
        include_inferred=include_inferred,
        )

    x.dates = dates
    x.elevation = elevation
    package = x.astronomic(x.dates)
    (x.zeta, x.nu, x.nup, x.nupp, x.kap_p, x.ii, x.R, x.Q, x.T, x.jd, x.s, x.h, x.N, x.p, x.p1) = package
    (x.speed_dict, x.key_list) = x.which_constituents(len(x.dates),
            package, rayleigh_comp=ray)

    # the analysis
    x.constituents()
    
    return df_water_levels, x