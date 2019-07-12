def read_data(fname):
    from pathlib import Path
    from numpy import float64 as float

    if Path(fname).exists():
        with open(fname) as f:
            inputs = list(f)
        keys = [f.strip().split('=')[0].strip() for f in inputs]
        values = [f.strip().split('=')[1].strip() for f in inputs]
        for i in range(len(values)):
            try:
                values[i] = float(values[i])
            except ValueError:
                pass
        config = dict(zip(keys, values))
    else:
        raise FileNotFoundError(f'info file was not found: {fname}')

    return config


def tide_data(data_dir, state):
    from pathlib import Path
    import shutil

    if state == 'low':
        wl = Path(data_dir, 'water_level_low.bc')
    elif state == 'high':
        wl = Path(data_dir, 'water_level_high.bc')
    else:
        raise ValueError('state can only be low or high')

    if wl.exists():
        shutil.copy(wl, 'tide.data')
    else:
        raise FileNotFoundError(f'input file was not found: {str(wl)}')

    return


def discharge_data(fname, state, bay):
    config = read_data(fname)

    with open('discharge.data', 'w') as f:
        if state == 'low' or state == 'high' or state == 'ref':
            f.write(f'{config[state] / bay.r_width} {bay.x_r1} {bay.x_r2}')
        else:
            raise ValueError('state can only be low, ref or high')


if __name__ == '__main__':
    from bay import Bay

    mobile = Bay('bay.info')
    tide_data('data', 'low')
    discharge_data('data/discharge.bc', 'low', mobile)
    print(mobile.min_ref)
