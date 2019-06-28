def generate_bc_files(year, wl_gage, q_gage):
    import tide_constituents as tc
    import pandas as pd
    from calendar import monthrange
    import utils
    from metpy.units import units

    start = year + '0101'
    end = year + '1231'
    lon, lat = wl_gage
    data = tc.get_water_levels(start, end, lon, lat)

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

        prediction = tc.wl_prediction(data, start, end, interval=1)
        prediction['sec'] = prediction.index
        prediction['sec'] = prediction.sec.apply(lambda x: (
            x - prediction.index[0]).total_seconds()).astype('int')
        prediction = prediction[['sec', 'prediction']]
        utils.write_wl_bc(prediction, key, 'dflow')

    lon, lat = q_gage
    start, end = year + '0101', year + '1231'

    q = utils.get_discharge('gage_data', start, end, (lon, lat))
    q_range = [q.val.min(), q.val.mean(), q.val.max()]
    q_range = [(i * units('ft^3/s')).to_base_units().magnitude
               for i in q_range]
    utils.write_q_bc(prediction.index[0], prediction.sec[0],
                     prediction.sec[-1], q_range, 'dflow')


if __name__ == '__main__':
    from sys import argv

    year = argv[1]
    wl_gage = (float(argv[2]), float(argv[3]))
    q_gage = (float(argv[4]), float(argv[5]))
    generate_bc_files(year, wl_gage, q_gage)
