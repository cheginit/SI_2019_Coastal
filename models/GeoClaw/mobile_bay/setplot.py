"""
Set up the plot figures, axes, and items to be done for each frame.

This module is imported by the plotting routines and then the
function setplot is called to set the plot parameters.

"""

from __future__ import absolute_import
import numpy


#--------------------------
def setplot(plotdata=None):
    #--------------------------
    """
    Specify what is to be plotted at each frame.
    Input:  plotdata, an instance of pyclaw.plotters.data.ClawPlotData.
    Output: a modified version of plotdata.

    """

    from clawpack.visclaw import colormaps, geoplot
    from bay import Bay

    mobile = Bay('bay.info')

    if plotdata is None:
        from clawpack.visclaw.data import ClawPlotData
        plotdata = ClawPlotData()

    plotdata.clearfigures()  # clear any old figures,axes,items data

    def set_drytol(current_data):
        # The drytol parameter is used in masking land and water and
        # affects what color map is used for cells with small water depth h.
        # The cell will be plotted as dry if h < drytol.
        # The best value to use often depends on the application and can
        # be set here (measured in meters):
        current_data.user["drytol"] = 1.e-3

    plotdata.beforeframe = set_drytol

    #-----------------------------------------
    # Figure for pcolor plot
    #-----------------------------------------
    plotfigure = plotdata.new_plotfigure(name='pcolor', figno=0)

    # Set up for axes in this figure:
    plotaxes = plotfigure.new_plotaxes('pcolor')
    plotaxes.title = 'Surface'
    plotaxes.scaled = True

    # Water
    plotitem = plotaxes.new_plotitem(plot_type='2d_pcolor')
    plotitem.plot_var = geoplot.surface
    plotitem.pcolor_cmap = geoplot.tsunami_colormap
    plotitem.pcolor_cmin = -0.5
    plotitem.pcolor_cmax = 0.5
    plotitem.add_colorbar = True
    plotitem.amr_celledges_show = [0, 0, 0]
    plotitem.patchedges_show = 1

    # Land
    plotitem = plotaxes.new_plotitem(plot_type='2d_pcolor')
    plotitem.plot_var = geoplot.land
    plotitem.pcolor_cmap = geoplot.land_colors
    plotitem.pcolor_cmin = mobile.z0
    plotitem.pcolor_cmax = mobile.z_r
    plotitem.add_colorbar = False
    plotitem.amr_celledges_show = [0, 0, 0]
    plotitem.patchedges_show = 1
    plotaxes.xlimits = [mobile.x_o1, mobile.x_o2]
    plotaxes.ylimits = [mobile.y0, mobile.y_r]

    # Add contour lines of bathymetry:
    plotitem = plotaxes.new_plotitem(plot_type='2d_contour')
    plotitem.plot_var = geoplot.topo
    from numpy import arange, linspace
    plotitem.contour_levels = linspace(mobile.z0, mobile.z_r, 10)
    plotitem.amr_contour_colors = ['k']  # color on each level
    plotitem.kwargs = {'linestyles': 'solid'}
    plotitem.amr_contour_show = [1]
    plotitem.celledges_show = 0
    plotitem.patchedges_show = 0
    plotitem.show = True

    #-----------------------------------------
    # Figures for gauges
    #-----------------------------------------
    plotfigure = plotdata.new_plotfigure(name='Surface & topo',
                                         figno=1,
                                         type='each_gauge')

    plotfigure.clf_each_gauge = True

    # Set up for axes in this figure:
    plotaxes = plotfigure.new_plotaxes()
    plotaxes.xlimits = 'auto'
    plotaxes.ylimits = [-1.5, 1.5]
    plotaxes.title = 'Surface'

    # Plot surface as blue curve:
    plotitem = plotaxes.new_plotitem(plot_type='1d_plot')
    plotitem.plot_var = 3
    plotitem.plotstyle = 'b-'

    # Plot topo as green curve:
    plotitem = plotaxes.new_plotitem(plot_type='1d_plot')

    def gaugetopo(current_data):
        q = current_data.q
        h = q[0, :]
        eta = q[3, :]
        topo = eta - h
        return topo

    plotitem.plot_var = gaugetopo
    plotitem.plotstyle = 'g-'

    def add_zeroline(current_data):
        from pylab import plot, legend
        t = current_data.t
        legend(('surface', 'topography'), loc='lower left')
        plot(t, 0 * t, 'k')

    plotaxes.afteraxes = add_zeroline

    #-----------------------------------------

    # Parameters used only when creating html and/or latex hardcopy
    # e.g., via pyclaw.plotters.frametools.printframes:

    plotdata.printfigs = True  # print figures
    plotdata.print_format = 'png'  # file format
    plotdata.print_framenos = 'all'  # list of frames to print
    plotdata.print_gaugenos = 'all'  # list of gauges to print
    plotdata.print_fignos = 'all'  # list of figures to print
    plotdata.html = True  # create html files of plots?
    plotdata.html_homelink = '../README.html'  # pointer for top of index
    plotdata.latex = True  # create latex file of plots?
    plotdata.latex_figsperline = 2  # layout of plots
    plotdata.latex_framesperline = 1  # layout of plots
    plotdata.latex_makepdf = False  # also run pdflatex?
    plotdata.parallel = True  # make multiple frame png's at once

    return plotdata
