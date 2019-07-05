import numpy as np
import pandas as pd
from pathlib import Path
import fileinput
import shutil
import os


def get_discharge(gis_dir, start, end, coords, station_id=None):
    '''Downloads climate and observation data from Daymet and USGS, respectively.

        Args:
        gis_dir (str): Path to the location of NHDPlusV21 root directory; GageLoc and GageInfo
                       are required.
        input_dir (str): Path to the location of climate data. The naming convention is
                         input_dir/{watershed name}_climate.h5
        start (datetime): The starting date of the time period.
        end (datetime): The end of the time period.
        coords (float, float): A tuple including longitude and latitude of the observation point.
        swmm_info (str, int): A tuple including path to .inp file and the coordinate system
                              (projection) of the swmm project (https://epsg.io is used).
        new_data (bool): True is data should be downloaded and False if the data exists localy.
        watershed (str): An optional argument for the name of the watershed for saving climate data.

        Note: either coords should be given or swmm_info.

        Return:
        climate (DataFrame): A Pandas dataframe including the following:
                             yday, dayl, prcp, srad, swe, tmax, tmin, vp, pet, qobs, tmean
    '''
    from shapely.geometry import Point
    from shapely.ops import nearest_points
    import geopandas as gpd
    from metpy.units import units

    if station_id is None:
        # Get x, y coords from swmm if given and transform to lat, lon
        lon, lat = coords

        loc_path = Path(gis_dir, 'GageLoc.shp')
        if not loc_path.exists():
            raise FileNotFoundError('GageLoc.shp cannot be found in ' +
                                    str(gis_dir))
        else:
            gloc = gpd.read_file(loc_path)

        # Get station ID based on lat/lon
        point = Point(lon, lat)
        pts = gloc.geometry.unary_union
        station = gloc[gloc.geometry.geom_equals(nearest_points(point, pts)[1])]
        station_id = station.SOURCE_FEA.values[0]

    start, end = pd.to_datetime(start), pd.to_datetime(end)

    # Download streamflow observations from USGS
    df = nwis_json(site=str(station_id),
                   parm='00060',
                   start= start.strftime('%Y-%m-%d'),
                   end=end.strftime('%Y-%m-%d'),
                   freq='dv')

    return df[['sitecode','val', 'unit']].copy()


def nwis_json(site, parm='00060', start=None, end=None, period=None, freq='dv'):
    """Obtain NWIS data via JSON.

    Parameters
    ----------
    site : str, optional
        NWIS site code. Default '01646500'
    parm : str, optional
        Parameter code. Default '00065'
        e.g. '00065' for water level, '00060' for discharge.
    freq : str, optional
        Data frequency. Valid values are:
        - 'iv' for unit-value data
        - 'dv' for daily average data (default)
    start : str, optional
    end : str, optional
        Start and end dates in ISO-8601 format (e.g. '2016-07-01').
        If specifying start and end, do not specify period.
    period : str, optional
        Duration following ISO-8601 duration format, e.g. 'P1D' for one day
        Default one day.
        If specifying period, do not specify start and end.

    Returns
    -------
    pandas.DataFrame
        A Pandas DataFrame of the returned data with the following columns:
        - 'time': time in UTC
        - 'sitename': site name
        - 'sitecode': site code
        - 'val': value
        - 'unit': unit
        - 'variableName': variable name
        - 'timelocal': local time
        - 'latitude': site latitude
        - 'longitude': site longitude
        - 'srs': latitude and longitude spatial reference system

    More info about the URL format is at https://waterservices.usgs.gov

    dnowacki@usgs.gov 2016-07
    """
    import requests
    from dateutil import parser
    import pytz

    if period is None and start is None and end is None:
        period='P1D'

    if period is None:
        url = ('http://waterservices.usgs.gov/nwis/' + freq +
              '/?format=json&sites=' + str(site) +
              '&startDT=' + start +
              '&endDt=' + end +
              '&parameterCd=' + str(parm))
    else:
        url = ('http://waterservices.usgs.gov/nwis/' + freq +
              '/?format=json&sites=' + str(site) +
              '&period=' + period +
              '&parameterCd=' + str(parm))

    payload = requests.get(url).json()
    v = payload['value']['timeSeries'][0]['values'][0]['value']
    pvt = payload['value']['timeSeries'][0]
    nwis = {}
    nwis['timelocal'] = np.array(
        [parser.parse(v[i]['dateTime']) for i in range(len(v))])
    # Convert local time to UTC
    nwis['time'] = np.array([x.astimezone(pytz.utc) for x in nwis['timelocal']])
    nwis['sitename'] = pvt['sourceInfo']['siteName']
    nwis['sitecode'] = pvt['sourceInfo']['siteCode'][0]['value']
    nwis['latitude'] = pvt['sourceInfo']['geoLocation']['geogLocation']['latitude']
    nwis['longitude'] = pvt['sourceInfo']['geoLocation']['geogLocation']['longitude']
    nwis['srs'] = pvt['sourceInfo']['geoLocation']['geogLocation']['srs']
    nwis['unit'] = pvt['variable']['unit']['unitCode']
    nwis['variableName'] = pvt['variable']['variableName']
    nwis['val'] = np.array([float(v[i]['value']) for i in range(len(v))])
    nwis['val'][nwis['val'] == pvt['variable']['noDataValue']] = np.nan

    return pd.DataFrame(nwis,
                        columns=['time',
                                 'sitename',
                                 'sitecode',
                                 'val',
                                 'unit',
                                 'variableName',
                                 'timelocal',
                                 'latitude',
                                 'longitude',
                                 'srs']).set_index('time')


def get_peaks(site):
    import io
    from metpy.units import units


    url = ('http://nwis.waterdata.usgs.gov/usa/nwis/peak?site_no=' + str(site) + '&agency_cd=USGS&format=hn2')
    payload = requests.get(url).content
    rawData = pd.read_csv(io.StringIO(payload.decode('utf-8')), skiprows=4, header=None, delim_whitespace=True)
    rawData = rawData.loc[:, 1:3]
    rawData.columns = ['date', 'qpeak']
    rawData['date'] = pd.to_datetime(rawData.date.astype('str'))
    rawData.set_index('date', inplace=True, drop=True)
    rawData['qpeak'] = rawData.qpeak.apply(lambda x: (x * units('ft^3/s')).to_base_units().magnitude)

    return rawData


def get_lulc(input_dir, geometry, station_id, width=2000):
    '''Download and compute land use, canopy and cover from NLCD database
       inside a given Polygon with epsg:4326 projection (lat/lon).
       Note: NLCD data corresponds to 30 m cells.
       Args:
           input_dir (str): path to inpu directory for saving the data
           geometry (Polygon): a Polygon object encompassing the whole watershed.
           station_id (str):station id of the watershed for naming the output files.
           width (int): width of the output files in pixels (height will be
                        computed automatically from aspect ratio of the domain)
       Returns:
           impervious (dict): a dictionary containing min, max, mean and count
                              of the imperviousness of the watershed
           canpoy (dict): a dictionary containing min, max, mean and count
                              of the canpoy of the watershed
           cover (dataframe): a dataframe containing watershed's land coverage
                              percentage.
    '''
    from owslib.wms import WebMapService
    from rasterstats import zonal_stats
    from src.nlcd_helper import NLCD

    if not Path(input_dir).is_dir():
        try:
            import os
            os.mkdir(input_dir)
        except OSError:
            print("input directory cannot be created: {:s}".format(path))

    urls = {'impervious' : 'https://www.mrlc.gov/geoserver/mrlc_display/' \
                           + 'mrlc_nlcd_2011_impervious_2011_edition_2014_10_10/' \
                           + 'wms?service=WMS&request=GetCapabilities',
            'cover' : 'https://www.mrlc.gov/geoserver/mrlc_display/' \
                      + 'mrlc_nlcd_2011_landcover_2011_edition_2014_10_10/' \
                      + 'wms?service=WMS&request=GetCapabilities',
            'canopy' : 'https://www.mrlc.gov/geoserver/mrlc_display/' \
                       + 'mrlc_nlcd2011_usfs_conus_canopy_cartographic/'\
                       + 'wms?service=WMS&request=GetCapabilities'}

    params = {}
    for data_type, url in urls.items():
        data = "/".join([input_dir, "_".join([station_id, data_type])]) + '.geotiff'
        if not Path(data).exists():
            bbox = geometry.bounds
            height = int(
                np.abs(bbox[1] - bbox[3]) / np.abs(bbox[0] - bbox[2]) * width)
            wms = WebMapService(url)
            try:
                img = wms.getmap(layers=list(wms.contents),
                                 srs='epsg:4326',
                                 bbox=geometry.bounds,
                                 size=(width, height),
                                 format='image/geotiff',
                                 transparent=True)
            except ConnectionError:
                raise ('Data is not availble on the server.')

            with open(data, 'wb') as out:
                out.write(img.read())
        else:
            pass  # print('Using existing local data for ' + data_type)

        categorical = True if data_type == 'cover' else False
        params[data_type] = zonal_stats(geometry,
                                        data,
                                        categorical=categorical)[0]

    cover = pd.Series(params['cover'])
    cover = cover / cover.sum() * 100
    cover.index = cover.index.astype('str')
    cover = cover.to_frame('percent')
    cover['type'] = [
        cat for name, cat in NLCD().values.items() for i in cover.index
        if i in name
    ]
    #cover = cover.groupby('type').sum()
    return params['impervious'], params['canopy'], cover


def daac_download(saveDir, files):
    """
    ---------------------------------------------------------------------------------------------------
     How to Access the LP DAAC Data Pool with Python
     The following Python code example demonstrates how to configure a connection to download data from
     an Earthdata Login enabled server, specifically the LP DAAC's Data Pool.
    ---------------------------------------------------------------------------------------------------
     Author: Cole Krehbiel
     Last Updated: 11/20/2018
    ---------------------------------------------------------------------------------------------------
    Args:
        saveDir (str): Specify directory to save files to
        files (str): A single granule URL, or the location of textfile containing granule URLs
    return:
        path (str): path to the downloaded file
    """
    # Load necessary packages into Python
    from subprocess import Popen
    from getpass import getpass
    from netrc import netrc
    import time
    import requests

    # ----------------------------------USER-DEFINED VARIABLES--------------------------------------- #
    prompts = [
        'Enter NASA Earthdata Login Username \n(or create an account at urs.earthdata.nasa.gov): ',
        'Enter NASA Earthdata Login Password: '
    ]

    # ---------------------------------SET UP WORKSPACE---------------------------------------------- #
    # Create a list of files to download based on input type of files above
    if files.endswith('.txt'):
        fileList = open(files,
                        'r').readlines()  # If input is textfile w file URLs
    elif isinstance(files, str):
        fileList = [files]  # If input is a single file

    # Generalize download directory
    if saveDir[-1] != '/' and saveDir[-1] != '\\':
        saveDir = saveDir.strip("'").strip('"') + os.sep
    urs = 'urs.earthdata.nasa.gov'  # Address to call for authentication

    # --------------------------------AUTHENTICATION CONFIGURATION----------------------------------- #
    # Determine if netrc file exists, and if so, if it includes NASA Earthdata Login Credentials
    try:
        netrcDir = os.path.expanduser("~/.netrc")
        netrc(netrcDir).authenticators(urs)[0]

    # Below, create a netrc file and prompt user for NASA Earthdata Login Username and Password
    except FileNotFoundError:
        homeDir = os.path.expanduser("~")
        Popen(
            'touch {0}.netrc | chmod og-rw {0}.netrc | echo machine {1} >> {0}.netrc'
            .format(homeDir + os.sep, urs),
            shell=True)
        Popen('echo login {} >> {}.netrc'.format(getpass(prompt=prompts[0]),
                                                 homeDir + os.sep),
              shell=True)
        Popen('echo password {} >> {}.netrc'.format(getpass(prompt=prompts[1]),
                                                    homeDir + os.sep),
              shell=True)

    # Determine OS and edit netrc file if it exists but is not set up for NASA Earthdata Login
    except TypeError:
        homeDir = os.path.expanduser("~")
        Popen('echo machine {1} >> {0}.netrc'.format(homeDir + os.sep, urs),
              shell=True)
        Popen('echo login {} >> {}.netrc'.format(getpass(prompt=prompts[0]),
                                                 homeDir + os.sep),
              shell=True)
        Popen('echo password {} >> {}.netrc'.format(getpass(prompt=prompts[1]),
                                                    homeDir + os.sep),
              shell=True)

    # Delay for up to 1 minute to allow user to submit username and password before continuing
    tries = 0
    while tries < 30:
        try:
            netrc(netrcDir).authenticators(urs)[2]
        except:
            time.sleep(2.0)
        tries += 1

    # -----------------------------------------DOWNLOAD FILE(S)-------------------------------------- #
    # Loop through and download all files to the directory specified above, and keeping same filenames
    for f in fileList:
        if not os.path.exists(saveDir):
            os.makedirs(saveDir)
        saveName = os.path.join(saveDir, f.split('/')[-1].strip())

        # Create and submit request and download file
        with requests.get(
                f.strip(),
                stream=True,
                auth=(netrc(netrcDir).authenticators(urs)[0],
                      netrc(netrcDir).authenticators(urs)[2])) as response:
            if response.status_code != 200:
                print(
                    "{} not downloaded. Verify that your username and password are correct in {}"
                    .format(f.split('/')[-1].strip(), netrcDir))
            else:
                response.raw.decode_content = True
                content = response.raw
                with open(saveName, 'wb') as d:
                    while True:
                        chunk = content.read(16 * 1024)
                        if not chunk:
                            break
                        d.write(chunk)
                print('Downloaded file: {}'.format(saveName))
    return saveName


def get_inputs(f_in):
    if not Path(f_in).exists():
        raise FileNotFoundError(f'input file not found: {f_in}')

    with open(f_in, 'r') as f:
        lines = filter(None, (line.rstrip() for line in f))
        lines = [line for line in lines if not line.lstrip()[0] == '#']

    prop = []
    prop_dic = {}
    prop_size = 0
    for line in lines:
        if line[0] == '[':
            prop.append(line.strip('[]'))
            prop_size += 1
            dic = {}
        else:
            var = line.strip().partition(" ")[0]
            val = line.strip().partition(" ")[2].strip().partition(";")[0]
            dic[var] = val
        if len(prop_dic) < prop_size:
            prop_dic[prop[-1]] = dic

    dtype = np.dtype([(p, np.float64) for p in list(prop_dic['CONSTANTS'].keys())])
    constants = np.zeros(1, dtype=dtype)
    for p, v in prop_dic['CONSTANTS'].items():
        constants[p] = v

    bounds = {}
    for p, v in prop_dic['BOUNDS'].items():
        b = v.strip("()").strip().split(',')
        bounds[p] = (np.float64(b[0]), np.float64(b[1]))

    left = list(prop_dic['CONSTRAINTS'].keys())
    right = list(prop_dic['CONSTRAINTS'].values())
    ineq = []
    for i in right:
        eq = i.strip().split("=")
        if len(eq) == 1:
            ineq.append(eq[0][0])
        else:
            ineq.append(eq[0][0] + '=')
    right = [i.strip(" <>=") for i in right]
    constraints = [(l, i, r) for l, i, r in zip(left, ineq, right)]
    cons = []
    for i in constraints:
        ineq = 1 if '=' in i[1] else 1.01
        n = [(1, 1), (2, ineq)] if '>' in i[1] else [(2, ineq), (1, 1)]

        cons.append(((-1)**n[0][0] * n[0][1], i[0],
                     (-1)**n[1][0] * n[1][1], i[2]))

    dtype = np.dtype([(p, np.float64) for p in list(prop_dic['BOUNDS'].keys())])

    return constants[0], bounds, cons, dtype, prop_dic['CONFIG']


def conversion(coords):
    direction = {'N':1, 'S':-1, 'E': 1, 'W':-1}
    new = coords.replace(u'°',' ').replace('\'',' ').replace('"',' ').split()
    new_dir = new.pop()
    return (float(new[0]) + float(new[1])/60.0 + float(new[2])/3600.0) * direction[new_dir]


def write_wl_bc(water_level, key, ptype):
    if not Path(ptype).exists():
        Path(ptype).mkdir()

    if ptype == 'dflow':
        bcs = ['templates/WaterLevel_1.bc', 'templates/WaterLevel_2.bc']
        bc_1 = 'WaterLevel_1.bc'
        bc_2 = 'WaterLevel_2.bc'

        shutil.copyfile(bcs[0], bc_1)
        shutil.copyfile(bcs[1], bc_2)

        with fileinput.FileInput([bc_1, bc_2], inplace=True) as file:
            for line in file:
                print(line.replace('seconds since 2001-01-01 00:00:00', 'seconds since ' + str(water_level.index[0])), end='')
        [water_level.to_csv(f, sep=' ', mode='a', header=None, index=False) for f in [bc_1, bc_2]]

        with open(Path(ptype, 'WaterLevel_' + key.strip() + '.bc'), 'w') as f:
            for bc in [bc_1, bc_2]:
                with open(bc,'r') as file: f.write(file.read())

        [os.remove(f) for f in Path().glob('*.bak')]
        [os.remove(f) for f in Path().glob('*.bc')]
    elif ptype == 'geoclaw':
        water_level.to_csv(Path(ptype, 'water_level_' + key.strip() + '.bc'),
                           sep=' ', mode='a', header=None, index=False)
    else:
        raise KeyError('key can only be dflow or geoclaw')


def write_q_bc(start_date, start_sec, end_sec, discharge, ptype):
    if not Path(ptype).exists():
        Path(ptype).mkdir()

    if ptype == 'dflow':
        tmp = 'templates/Discharge.bc'
        bcs = [Path(ptype, 'Discharge_low.bc'),
               Path(ptype, 'Discharge_ref.bc'),
               Path(ptype, 'Discharge_high.bc')]

        [shutil.copyfile(tmp, bc) for bc in bcs]

        with fileinput.FileInput(bcs, inplace=True) as file:
            for line in file:
                print(line.replace('seconds since 2001-01-01 00:00:00', 'seconds since ' + str(start_date)), end='')

        for bc, q in zip(bcs, discharge):
            with fileinput.FileInput(bc, inplace=True) as file:
                for line in file:
                    print(line.replace('tmin     Q', str(start_sec) + '    ' + str(q)), end='')

            with fileinput.FileInput(bc, inplace=True) as file:
                for line in file:
                    print(line.replace('tmax     Q', str(end_sec) + '    ' + str(q)), end='')

        [os.remove(f) for f in Path().glob('*.bak')]
        [os.remove(f) for f in Path().glob('*.bc')]
    elif ptype == 'geoclaw':
        file = Path(ptype, 'discharge.bc')
        with open(file, 'w') as f:
            f.write(f'Q_low = {discharge[0]:.5f}\n')
            f.write(f'Q_ref = {discharge[1]:.5f}\n')
            f.write(f'Q_high = {discharge[2]:.5f}\n')
            
    else:
        raise KeyError('key can only be dflow or geoclaw')