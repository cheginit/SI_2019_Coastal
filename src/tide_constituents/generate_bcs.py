def generate_bc_files(gauge, year, coords=(None, None), gid=None):
    import tide_constituents as tc
    import pandas as pd
    from calendar import monthrange
    import utils
    from metpy.units import units


    start = year + '0101'
    end = year + '1231'
    lon, lat = coords

    if gauge == 'water_level':
        data = tc.get_water_levels(start, end, lon, lat, gid)

        wl = data.water_level.copy()
        grouped = wl.groupby(pd.Grouper(freq='M'))

        def demeaner(group):
            return pd.DataFrame({
                'original': group,
                'demeaned': group - group.mean()
            })

        wl_demeaned = grouped.apply(demeaner)

        min_month = wl_demeaned.rolling(30).min().groupby(
            pd.Grouper(freq='M')).last()
        max_month = wl_demeaned.rolling(30).max().groupby(
            pd.Grouper(freq='M')).last()

        monthly_minmax = min_month.copy()
        monthly_minmax['high'] = max_month['demeaned']
        monthly_minmax = monthly_minmax[['demeaned', 'high']]
        monthly_minmax.columns = ['low', 'high']
        monthly_minmax['range'] = monthly_minmax.high - monthly_minmax.low
        ranked = monthly_minmax.sort_values('range')

        low, high = ranked.index[0], ranked.index[1]
        for date, key in zip([low, high], ['low', 'high']):
            days = monthrange(date.year, date.month)[1]
            end = date
            start = end - pd.DateOffset(days - 1)

            prediction = tc.get_tides(start.strftime('%Y%m%d'), end.strftime('%Y%m%d'), lon, lat)
            prediction['sec'] = prediction.index
            prediction['sec'] = prediction.sec.apply(lambda x: (
                x - prediction.index[0]).total_seconds()).astype('int')
            prediction = prediction[['sec', 'predicted_wl']]
            utils.write_wl_bc(prediction, key, 'dflow')
            utils.write_wl_bc(prediction, key, 'geoclaw')
    elif gauge == 'discharge':
        q = utils.get_discharge('gage_data', start, end, (lon, lat), gid)
        q['sec'] = q.index
        q['sec'] = q.sec.apply(lambda x: (x - q.index[0]).total_seconds()).astype('int')
        q_range = [q.val.min(), q.val.mean(), q.val.max()]
        q_range = [(i * units('ft^3/s')).to_base_units().magnitude
                   for i in q_range]
        utils.write_q_bc(q.index[0], q.sec[0],
                         q.sec[-1], q_range, 'dflow')
        utils.write_q_bc(q.index[0], q.sec[0],
                         q.sec[-1], q_range, 'geoclaw')
    else:
        raise ValueError('gauge type could only be water_leve or discharge.')

if __name__ == '__main__':
    from sys import argv

    gauge = argv[1]
    year = argv[2]
    if len(argv) == 5:
        coords = (float(argv[3]), float(argv[4]))
        gid = None
    elif len(argv) == 4:
        coords = (None, None)
        gid = argv[3]
    else:
        raise ValueError('3 or 4 arguments are required: gauge_type, year, [lon, lat], [station_id]')

    generate_bc_files(gauge, year, coords, gid)