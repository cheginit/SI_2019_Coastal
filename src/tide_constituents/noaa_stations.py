import pandas as pd


def deg2float(old):
    direction = {'N':1, 'S':-1, 'E': 1, 'W':-1}
    new = old.replace(u'°',' ').replace('\'',' ')
    new = new.split()
    new_dir = new.pop()
    return (float(new[0]) + float(new[1])/60.0) * direction[new_dir]


def parse(url, tag):
    import requests
    from bs4 import BeautifulSoup

    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    return soup.find_all(tag)


def get_stations_id():
    tags = parse('https://tidesandcurrents.noaa.gov/stations.html?type=Water%20Levels&sort=1', 'a')
    stations_id = []

    for t in tags:
        if t.has_attr('href'):
            if 'waterlevels.html?id' in t['href']:
                stations_id.append(re.findall(r'\d+', t['href'])[0])
    return stations_id


def get_stations_info(stations_id):
    import re


    established, lats, lons = [], [], []
    for st in stations_id:
        tags = parse('https://tidesandcurrents.noaa.gov/stationhome.html?id=' + st, 'td')
        for i in range(len(tags)-1):
            t = tags[i].contents[0]
            if isinstance(t, str):
                t = t.replace(':', '')
                if t == 'Established':
                    established.append(tags[i+1].contents[0])
                elif t == 'Latitude':
                    lats.append(deg2float(tags[i+1].contents[0]))
                elif t == 'Longitude':
                    lons.append(deg2float(tags[i+1].contents[0]))
    return established, lats, lons


stations_id = get_stations_id()
established, lats, lons = get_stations_info(stations_id)
df = pd.DataFrame({'ID': stations_id, 'Established': established, 'Longitude':lons, 'Latitude':lats})
df.to_csv('noaa_stations.csv', index=False)
