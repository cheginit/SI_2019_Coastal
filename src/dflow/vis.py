#!/usr/bin/env python

import numpy as np
from pathlib import Path
import utils
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()


class CrossSection():
    def __init__(self, res_list, inp_list):
        self.res_list = res_list
        self.inp_list = inp_list

        self.output = self.inp_list[-1]['output']
        if not Path(self.output).exists():
            Path(self.output).mkdir()

        self.nx = self.res_list[0].mesh2d_face_x.values
        self.ny = self.res_list[0].mesh2d_face_y.values
        self.center = np.where((self.nx > self.inp_list[0]['x_center'] - 300)
                               & (self.nx < self.inp_list[0]['x_center']))
        self.ny_center = self.ny[self.center]
        self.idx_sort = np.argsort(self.ny_center)[::-1]
        self.ny_center = self.ny_center[self.idx_sort]
        self.wd_center = [
            res.mesh2d_s1.values[:, self.center] for res in self.res_list
        ]

        self.ymax = np.array([
            np.absolute(res.mesh2d_s1.values).max() * 1.1
            for res in self.res_list
        ]).max()
        self.ymin = -self.ymax

        self.labels = [inp['label'] for inp in self.inp_list]
        self.title = [inp['title'] for inp in self.inp_list]
        if "Ref" in self.title:
            self.title.remove("Ref")

    def animate(self):
        print("Cross section visualization ...")
        utils.animation(self.plot_func,
                        range(0, self.res_list[0].time.shape[0],
                              1), self.output,
                        'cs_' + self.inp_list[-1]['label'].replace(' ', ''))

    def plot_func(self, t):
        import matplotlib.colors as mcolors

        output = Path('images', f'frame_{t:03d}.png')
        if output.exists():
            return

        fig, gs, canvas = utils.make_canvas(8, 5)
        ax = fig.add_subplot(gs[0])

        colors = list(mcolors.TABLEAU_COLORS.keys())[:len(self.wd_center)]
        for w, l, c in zip(self.wd_center, self.labels, colors):
            ax.plot(self.ny_center, w[t][0][self.idx_sort], label=f'{l}', c=c)

        ax.set_title(
            f'{self.title[0]} study; cross-section across the middle of the ' +
            'domain (y-direction)')
        ax.set_xlim(self.ny_center.min(), self.ny_center.max())
        ax.set_ylim(self.ymin, self.ymax)
        ax.set_xlabel('Distance (m)')
        ax.set_ylabel('Water Level (m)')
        ax.legend(loc='upper right')
        ax.ticklabel_format(style='sci', axis='x', scilimits=(3, 3))
        canvas.print_figure(output, format="png", dpi=300)


class WaterSurface():
    def __init__(self, res_list, inp_list):
        self.res_list = res_list
        self.inp_list = inp_list

        self.output = self.inp_list[-1]['output']
        if not Path(self.output).exists():
            Path(self.output).mkdir()

        self.vmax = np.array([
            np.absolute(res.mesh2d_s1.values).max() * 1.1
            for res in self.res_list
        ]).max()
        self.vmin = -self.vmax
        self.title = [inp['title'] for inp in self.inp_list]
        if "Ref" in self.title:
            self.title.remove("Ref")

    def animate(self):
        from matplotlib import tri, cm
        from tqdm import tqdm

        print("Water surface visualization ...")
        itr = 0

        for res, inp in tqdm(zip(self.res_list, self.inp_list),
                             total=len(self.res_list)):
            self.nx = res.mesh2d_face_x.values
            self.ny = res.mesh2d_face_y.values
            self.wd = res.mesh2d_s1

            self.norm = cm.colors.Normalize(vmax=self.vmax, vmin=self.vmin)
            self.cmap = cm.PRGn
            self.levels = np.arange(self.vmin, self.vmax, 0.05)

            self.triang = tri.Triangulation(self.nx, self.ny)
            x = self.nx[self.triang.triangles].mean(axis=1)
            y = self.ny[self.triang.triangles].mean(axis=1)

            m = []
            if inp['class'] == 1:
                m.append(
                    np.where((x > inp['x_o1']) & (x < inp['x_r1']) &
                             (y > inp['y_o']), 1, 0))
                m.append(
                    np.where((x > inp['x_r2']) & (x < inp['x_o2']) &
                             (y > inp['y_o']), 1, 0))
            else:
                if (inp['x_b3'] - inp['x_b1']) < 1e-2:
                    s_w, s_e = 0e0, 0e0
                else:
                    s_w = (inp['y_r'] - inp['y_b']) / (inp['x_b3'] -
                                                       inp['x_b1'])
                    s_e = (inp['y_r'] - inp['y_b']) / (inp['x_b4'] -
                                                       inp['x_b2'])

                m.append(
                    np.where((x > inp['x_o1']) & (x < inp['x_b1']) &
                             (y > inp['y_o']), 1, 0))
                m.append(
                    np.where((x > inp['x_b2']) & (x < inp['x_o2']) &
                             (y > inp['y_o']), 1, 0))
                m.append(
                    np.where((x > inp['x_b1']) & (x < inp['x_b3']) &
                             (y > inp['y_b']), 1, 0))
                m.append(
                    np.where((x > inp['x_b4']) & (x < inp['x_b2']) &
                             (y > inp['y_b']), 1, 0))
                m.append(
                    np.where((x > inp['x_b3']) & (x < inp['x_r1']) &
                             (y > inp['y_b']), 1, 0))
                m.append(
                    np.where((x > inp['x_r2']) & (x < inp['x_b4']) &
                             (y > inp['y_b']), 1, 0))
                m.append(
                    np.where((x > inp['x_b1']) & (x < inp['x_b3']) &
                             (y > inp['y_b'] + s_w * (x - inp['x_b1'])), 1, 0))
                m.append(
                    np.where((x > inp['x_b4']) & (x < inp['x_b2']) &
                             (y > inp['y_b'] + s_e * (x - inp['x_b2'])), 1, 0))

            mask = m[0]
            for i in m[1:]:
                mask = mask + i
            mask[mask > 1] = 1

            self.triang.set_mask(mask)

            self.label = 'wl_' + inp['label']
            utils.animation(self.plot_func, range(0, self.wd.time.shape[0], 1),
                            self.output, self.label.replace(' ', ''))
            if itr > 0:
                self.wd = self.res_list[0].mesh2d_s1 - self.wd
                self.label = 'RDiff ' + self.label
                utils.animation(self.plot_func,
                                range(0, self.wd.time.shape[0], 1),
                                self.output, self.label.replace(' ', ''))
            itr = +1

    def plot_func(self, t):
        from matplotlib import cm
        from scipy.interpolate import griddata

        output = Path('images', f'frame_{t:03d}.png')
        if output.exists():
            return

        fig, gs, canvas = utils.make_canvas(5.5, 7)
        ax = fig.add_subplot(gs[0])

        wdt = griddata((self.nx, self.ny),
                       self.wd.isel(time=t).values,
                       (self.triang.x, self.triang.y),
                       method='linear')

        tcf = ax.tricontourf(self.triang,
                             wdt,
                             self.levels,
                             cmap=cm.get_cmap(self.cmap,
                                              len(self.levels) - 1),
                             norm=self.norm)
        ax.tricontour(self.triang, wdt, tcf.levels, colors='k')

        ax.set_title(
            f'{self.title[0]} study; water level contours for {self.label.strip()}'
        )
        ax.set_xlim(self.nx.min(), self.nx.max())
        ax.set_ylim(self.ny.min(), self.ny.max())
        ax.ticklabel_format(style='sci', scilimits=(3, 3))
        fig.colorbar(tcf,
                     norm=self.norm,
                     ax=ax,
                     use_gridspec=True,
                     extend=[self.vmin, self.vmax])
        canvas.print_figure(output, format="png", dpi=300)


class TidalConstituents():
    def __init__(self, res_list, inp_list):
        from datetime import datetime
        import pandas as pd
        import analysis

        self.res_list = res_list
        self.inp_list = inp_list
        self.title = [inp['title'] for inp in self.inp_list]
        if "Ref" in self.title: self.title.remove("Ref")

        self.output = self.inp_list[-1]['output']
        if not Path(self.output).exists():
            Path(self.output).mkdir()

        self.dates = res_list[0].time.values.astype(int) * 1e-9
        self.dates = np.array(
            [datetime.utcfromtimestamp(t) for t in self.dates])

        self.nx = self.res_list[0].mesh2d_face_x.values
        self.ny = self.res_list[0].mesh2d_face_y.values
        self.center = np.where((self.nx > self.inp_list[0]['x_center'] - 300)
                               & (self.nx < self.inp_list[0]['x_center']))[0]
        self.mouth_idx = np.where(
            (self.ny > self.inp_list[0]['y_mouth'] - 100)
            & (self.ny < self.inp_list[0]['y_mouth'] + 1100))[0]

        self.mouth_idx = np.intersect1d(self.center, self.mouth_idx)

        if not Path(self.output).exists():
            Path(self.output).mkdir()

        for i in range(len(inp_list)):
            if not inp_list[i]['class'] == 1:
                bay_idx = np.where(
                    (self.ny > self.inp_list[0]['y_o'] - 100)
                    & (self.ny < self.inp_list[0]['y_o'] + 1100))[0]
                bay_idx = np.intersect1d(self.center, bay_idx)

                uy_bay = np.array(
                    [u[bay_idx].values[0] for u in res_list[i].mesh2d_ucy])
                el_bay = np.array(
                    [w[bay_idx].values[0] for w in res_list[i].mesh2d_s1])

                df = pd.DataFrame(columns=['date', 'water level', 'velocity'])
                df['date'] = self.dates
                df['water level'] = el_bay
                df['velocity'] = uy_bay
                df.to_csv(Path(
                    self.output,
                    f'bay_{inp_list[i]["label"].replace(" ", "_")}.csv'),
                          index=False)

        self.ny_center = self.ny[self.center[::4]]
        self.idx_sort = np.argsort(self.ny_center)[::-1]
        self.ny_center = self.ny_center[self.idx_sort]

        wl_list = [res.mesh2d_s1 for res in res_list]
        self.elv_mouth, self.wd_center, self.elvs_list = [], [], []
        for wl in wl_list:
            self.elv_mouth.append(
                np.array([w[self.mouth_idx].values[0] for w in wl]))
            self.wd_center.append(wl.values[:, self.center])
            self.elvs_list.append(
                np.column_stack([
                    wl.isel(time=t)[self.center[::4]].values
                    for t in range(wl_list[0].time.shape[0])
                ]))

        uy_list = [res.mesh2d_ucy for res in res_list]
        self.uy_mouth = [
            np.array([u[self.mouth_idx].values[0] for u in uy])
            for uy in uy_list
        ]

        self.amps_list, self.phases_list = analysis.decompose(
            self.dates, self.elvs_list)

        self.labels = [inp['label'] for inp in self.inp_list]

        df = pd.DataFrame(columns=['date', 'water level', 'velocity'])
        itr = 0
        for label in self.labels:
            df['date'] = self.dates
            df['water level'] = self.elv_mouth[itr]
            df['velocity'] = self.uy_mouth[itr]
            df.to_csv(Path(self.output,
                           f'mouth_{label.replace(" ", "_")}.csv'),
                      index=False)
            itr += 1

        df = pd.DataFrame(
            columns=['distance', 'M2 amp', 'M2 phase', 'M4 amp', 'M4 phase'])
        itr = 0
        for label in self.labels:
            df['distance'] = self.ny_center
            df['M2 amp'] = self.amps_list[itr][0][self.idx_sort]
            df['M2 phase'] = self.phases_list[itr][0][self.idx_sort]
            df['M4 amp'] = self.amps_list[itr][1][self.idx_sort]
            df['M4 phase'] = self.phases_list[itr][1][self.idx_sort]
            df.to_csv(Path(self.output, f'tide_{label.replace(" ", "_")}.csv'),
                      index=False)
            itr += 1

    def plot_constituents(self):
        import matplotlib.colors as mcolors

        print("Tidal constituents visualization ...")
        for tc, name in zip([0, 1], ['M2', 'M4']):
            output = Path(self.output, f'tide_{name}.png')
            if output.exists():
                continue

            fig, gs, canvas = utils.make_canvas(9, 6, nx=2, ny=1)
            ax = [fig.add_subplot(g) for g in gs]

            colors = list(mcolors.TABLEAU_COLORS.keys())[:len(self.wd_center)]
            for a, p, l, c in zip(self.amps_list, self.phases_list,
                                  self.labels, colors):
                ax[0].plot(self.ny_center,
                           a[tc][self.idx_sort],
                           label=f'{l}',
                           c=c)
                ax[1].plot(self.ny_center,
                           p[tc][self.idx_sort],
                           label=f'{l}',
                           c=c)

            fig.suptitle(
                f'{self.title[0]} study; the ${name}$ tidal constituent ' +
                'of water level along the center of the domain',
                y=0.99,
                horizontalalignment='center',
                verticalalignment='top',
                fontsize=12)

            ax[1].set_xlim(self.ny_center.min(), self.ny_center.max())

            ax[1].set_xlabel('Distance (m)')
            ax[0].set_ylabel(f'${name}$ ampl. (m/s)')
            ax[1].set_ylabel(f'${name}$ phase (deg)')
            [x.legend(loc='upper right') for x in ax]
            ax[1].ticklabel_format(style='sci', axis='x', scilimits=(3, 3))
            canvas.print_figure(output, format="png", dpi=300)

    def plot_mouth(self):
        import matplotlib.colors as mcolors
        import matplotlib.dates as mdates

        print("River's mouth visualization ...")
        output = Path(self.output, 'mouth.png')

        if output.exists():
            return

        fig, gs, canvas = utils.make_canvas(9, 6, nx=2, ny=1)
        ax = [fig.add_subplot(g) for g in gs]

        colors = list(mcolors.TABLEAU_COLORS.keys())[:len(self.wd_center)]
        for e, u, l, c in zip(self.elv_mouth, self.uy_mouth, self.labels,
                              colors):
            ax[0].plot(self.dates, e, label=f'{l}', c=c)
            ax[1].plot(self.dates, u, label=f'{l}', c=c)

        fig.autofmt_xdate()

        fig.suptitle(
            f'{self.title[0]} study; velocity and water level at the mouth ' +
            'of the river',
            y=0.99,
            horizontalalignment='center',
            verticalalignment='top',
            fontsize=12)

        uy_max = np.max(np.absolute(self.uy_mouth)) * 1.1
        elv_max = np.max(np.absolute(self.elv_mouth)) * 1.1
        ax[0].set_ylim(-elv_max, elv_max)
        ax[1].set_ylim(-uy_max, uy_max)
        [x.set_xlabel('') for x in ax]
        ax[0].set_ylabel('Water Level (m)')
        ax[1].set_ylabel('Velocity (m/s)')

        ax[1].fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
        [x.legend(loc='upper right') for x in ax]

        canvas.print_figure(output, format="png", dpi=300)
