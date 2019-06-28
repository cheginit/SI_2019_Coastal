import pandas as pd
import numpy as np
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

    noaa_predict = coops.get_data(
        begin_date=start,
        end_date=end,
        stationid=stations.iloc[idx].ID,
        product="predictions",
        datum="MSL",
        interval="h",
        units="metric",
        time_zone="gmt")
    noaa_predict['predicted_wl'] =  noaa_predict.predicted_wl.astype('float')

    return noaa_predict


def get_water_levels(start, end, lon, lat):
    """
    date format: YYYYDDMM
    Returns: phase, amplitude
    """
    stations = pd.read_csv('noaa_stations.csv', parse_dates=[1])
    coords = [Point(ln, lt) for ln, lt in zip(stations.Longitude, stations.Latitude)]
    nearest_station_loc = nearest_points(Point(lon, lat), MultiPoint(coords))[1]
    idx = coords.index(nearest_station_loc)

    water_levels = coops.get_data(
        begin_date=start,
        end_date=end,
        stationid=stations.iloc[idx].ID,
        product="water_level",
        datum="MSL",
        interval="h",
        units="metric",
        time_zone="gmt")
    
    return water_levels

def tide_constituents(water_levels):
    
    dates = pd.to_datetime(water_levels.index) # a datetime.datetime list of dates
    elevation = water_levels.water_level.astype('float') # a list of surface elevation values

    # Set up the bits needed for TAPPY. This is mostly lifted from
    # tappy.py in the baker function "analysis" (around line 1721).
    quiet = True
    debug = False
    outputts = False
    outputxml = False
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
    
    return x


def sum_signals(constituents, hours, speed_dict, amp, phase):
    import astronomia.calendar as cal


    jd = [cal.cal_to_jd(i.year, i.month, i.day) + cal.hms_to_fday(i.hour, i.minute, i.second) for i in hours]
    hours = np.array(jd).flatten()
    hours = (hours - hours[0]) * 24.0
    total = np.zeros(len(hours), dtype=np.float64)

    deg2rad = np.pi/180.0
    for i in constituents:
        total = total + amp[i] * speed_dict[i]['FF'] * np.cos(speed_dict[i]['speed'] * hours - (phase[i] - speed_dict[i]['VAU']) * deg2rad)
    return total


def wl_prediction(data, start, end, interval=1):
    d = start
    p =  []
    
    while d < end:
        start_ = d
        end_ = start_ + pd.DateOffset(interval)
        end_ = end_ if end_ < end else end
        tide = tide_constituents(data.loc[start_:end_])
        prediction = 0.0 if 'Z0' not in list(tide.speed_dict.keys()) else tide.speed_dict['Z0']
        prediction += sum_signals(tide.key_list, tide.dates, tide.speed_dict, tide.r, tide.phase)
        p.append(prediction[:-1])
        d = end_

    return pd.DataFrame({'prediction': np.hstack(p)}, index=data.loc[start:end].index[:-1])