def read_data(fname):
    from pathlib import Path
    from numpy import float64 as float

    if Path(fname).exists():
        with open(fname, 'r') as f:
            inputs = filter(None, (line.rstrip() for line in f))
            inputs = [line for line in inputs if not line.lstrip()[0] == '#']
        keys = [
            f.strip().partition(';')[0].split('=')[0].strip() for f in inputs
        ]
        values = [
            f.strip().partition(';')[0].split('=')[1].strip() for f in inputs
        ]
        for i in range(len(values)):
            try:
                values[i] = float(values[i])
            except ValueError:
                continue

        config = dict(zip(keys, values))
    else:
        raise FileNotFoundError(f'info file was not found: {fname}')

    return config


def make_canvas(width, height, nx=1, ny=1):
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    import matplotlib.gridspec as gridspec

    # latexify(width, height)
    fig = Figure(figsize=(width, height), frameon=True)
    canvas = FigureCanvas(fig)
    gs = gridspec.GridSpec(nx,
                           ny,
                           left=0.15,
                           right=0.95,
                           bottom=0.15,
                           top=0.95,
                           wspace=0.0,
                           hspace=0.0,
                           width_ratios=None,
                           height_ratios=None)
    return fig, gs, canvas


def latexify(fig_width=None, fig_height=None, columns=1):
    import matplotlib
    from math import sqrt
    """Set up matplotlib's RC params for LaTeX plotting.
    Call this before plotting a figure.

    Parameters
    ----------
    fig_width : float, optional, inches
    fig_height : float,  optional, inches
    columns : {1, 2}
    """

    # code adapted from http://www.scipy.org/Cookbook/Matplotlib/LaTeX_Examples

    # Width and max height in inches for IEEE journals taken from
    # computer.org/cms/Computer.org/Journal%20templates/transactions_art_guide.pdf

    assert (columns in [1, 2])

    if fig_width is None:
        fig_width = 3.39 if columns == 1 else 6.9  # width in inches

    if fig_height is None:
        golden_mean = (sqrt(5) - 1.0) / 2.0  # Aesthetic ratio
        fig_height = fig_width * golden_mean  # height in inches

    MAX_HEIGHT_INCHES = 8.0
    if fig_height > MAX_HEIGHT_INCHES:
        print("WARNING: fig_height too large:" + fig_height +
              "so will reduce to" + MAX_HEIGHT_INCHES + "inches.")
        fig_height = MAX_HEIGHT_INCHES

    params = {
        'backend': 'ps',
        'text.latex.preamble':
        ['\\usepackage{gensymb}', '\\usepackage{mathtools}'],
        'axes.labelsize': 11,  # fontsize for x and y labels (was 10)
        'axes.titlesize': 11,
        'font.size': 11,
        'xtick.labelsize': 11,
        'ytick.labelsize': 11,
        'text.usetex': True,
        'figure.figsize': [fig_width, fig_height],
        'font.family': 'serif'
    }

    matplotlib.rcParams.update(params)


def animation(func,
              frames,
              output,
              fname,
              video=True,
              gif=False,
              clean_up=True):
    import time as dt
    import subprocess
    import multiprocessing
    from pathlib import Path
    import os

    if not Path('images').exists():
        Path('images').mkdir()
    if not Path(output).exists():
        Path(output).mkdir()

    starttime = dt.time()
    pool = multiprocessing.Pool()
    print(f'Plotting in parallel with {pool._processes} processors ...')

    pool.map(func, frames)
    pool.close()

    print(f'Plotting finished after {dt.time() - starttime:.1f} seconds')

    if video:
        print('Making a video from the plots ...')

        p = subprocess.Popen([
            'ffmpeg',
            '-framerate', '12',
            '-i', Path('images', 'frame_%03d.png'),
            '-c:v', 'libx264',
            '-preset', 'slow',
            '-profile:v', 'high',
            '-level:v', '4.0',
            '-pix_fmt', 'yuv420p',
            '-crf', '22',
            '-hide_banner',
            '-loglevel', 'panic',
            '-y',
            Path(output, f'{fname}.mp4')
        ])
        p.communicate()

    if gif:
        print('Making a gif from the plots ...')

        p = subprocess.Popen([
            'convert',
            '-delay', '10',
            '-resize', '30%',
            '-quiet',
            Path('images', '*.png'),
            Path(output, f'{fname}.gif')
        ])
        p.communicate()

    if clean_up:
        for f in list(Path('images').glob('*.png')):
            os.remove(f)

    print('Completed successfully')
