def tide_data(data_dir, state):
    from pathlib import Path
    import shutil
    
    if state == 'low':
        wl = Path(data_dir, 'water_level_low.bc')
    elif state == 'high':
        wl = Path(data_dir, 'water_level_high.bc')
    else:
        raise ValueError('state can only be low, ref and high')

    if wl.exists():
        shutil.copy(wl, 'tide.data')
    else:
        raise FileNotFoundError('input file was not found: ' + wl)

    return


def discharge_data(fname, state, area):
    from pathlib import Path
    import shutil
    
    
    if Path(fname).exists():
        with open(fname) as f:
            var = list(f)
        var = [float(f.strip().split('=')[1]) for f in var]
        
        with open('discharge.data', 'w') as f:
            if state == 'low':
                f.write(str(var[0] / area))
            elif state == 'ref':
                f.write(str(var[2] / area))
            elif state == 'high':
                f.write(str(var[3] / area))
            else:
                raise ValueError('state can only be low, ref and high')
    else:
        raise FileNotFoundError('input file was not found: ' + fname)
    return

if __name__ == '__main__':
    from bay import Bay

    mobile = Bay('trapezoidal', 10e3, 20.0, 0.67, 1.23, -5e3)

    tide_data('data', 'low')
    discharge_data('data/discharge.bc', 'low', mobile.r_area)
