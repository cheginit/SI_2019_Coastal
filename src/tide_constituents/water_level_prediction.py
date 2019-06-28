import tide_constituents as tc
from py_noaa import coops
import pandas as pd
import numpy as np
import tappy





start = '20180201'
end = '20180228'
interval = 1

start = pd.to_datetime(start)
end = pd.to_datetime(end)
d = start
w, t, p, r = [], [], [], []

while d < end:
    start_ = d
    end_ = start_ + pd.DateOffset(interval)
    end_ = end_ if end_ < end else end
    water_level, tide = tc.get_water_levels(start_.strftime('%Y%m%d'),
                                            end_.strftime('%Y%m%d'),
                                            -88.2, 30.4)
    water_level = water_level.water_level.astype('float')
    prediction = 0.0 if 'Z0' not in list(tide.speed_dict.keys()) else tide.speed_dict['Z0']
    prediction += sum_signals(tide.key_list, tide.dates, tide.speed_dict, tide.r, tide.phase)
    residual = water_level - prediction
    w.append(water_level)
    p.append(prediction)
    d = end_

water_level = pd.concat(w).to_frame()
water_level.columns = ['observation']
water_level['prediction'] = np.hstack(p)


data = tc.get_tides('20180101', '20181231', -88.2, 30.4)

wl = data.predicted_wl.copy()
grouped = wl.groupby(pd.Grouper(freq='M'))

def f(group):
        return pd.DataFrame({'original': group, 'demeaned': group - group.mean()})

wl_demeaned = grouped.apply(f)

min_month = wl_demeaned.rolling(30).min().groupby(pd.Grouper(freq='M')).last()
max_month = wl_demeaned.rolling(30).max().groupby(pd.Grouper(freq='M')).last()
monthly_minmax = min_month.copy()
monthly_minmax['high'] = max_month['demeaned']
monthly_minmax = monthly_minmax[['demeaned', 'high']]
monthly_minmax.columns = ['low', 'high']
monthly_minmax['range'] = monthly_minmax.high - monthly_minmax.low
monthly_minmax.sort_values('range')