def tide_constituents(dates, elevation):
    from tappy import tappy

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
        outputts=outputts,
        outputxml=outputxml,
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
    (x.zeta, x.nu, x.nup, x.nupp, x.kap_p, x.ii, x.R, x.Q, x.T, x.jd, x.s, x.h,
     x.N, x.p, x.p1) = package
    (x.speed_dict, x.key_list) = x.which_constituents(len(x.dates),
                                                      package,
                                                      rayleigh_comp=ray)

    # the analysis
    x.constituents()

    return x


def _decompose(dates, elvs_list):
    from tqdm import tqdm

    amps_list, phases_list = [], []
    for elvs in tqdm(elvs_list):
        con = tide_constituents(dates, elvs)
        amps_list.append((con.r['M2'], con.r['M4']))
        phases_list.append((con.phase['M2'], con.phase['M4']))
    return [amps_list, phases_list]


def decompose(dates, elvs_list):
    import multiprocessing
    from functools import partial
    import numpy as np

    pool = multiprocessing.Pool()
    print('Computing the tidal constituents in parallel with ' +
          f'{pool._processes} processors ...')
    decompose_el = partial(_decompose, dates)
    tide_list = pool.map(decompose_el, elvs_list)
    pool.close()
    amps_list = [np.column_stack(tide[0]) for tide in tide_list]
    phases_list = [np.column_stack(tide[1]) for tide in tide_list]
    return amps_list, phases_list
