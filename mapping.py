import pandas as pd
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np

jumpman = pd.read_csv('jumpman.csv')

#Mapping drop-offs to get user locations. NYC coordinates are 40.7N, -74W.
#Borough shapefiles located here: https://data.cityofnewyork.us/City-Government/Borough-Boundaries/tqmj-j8zm/data

map = Basemap(projection='cyl', lat_0=40.7, lon_0=-74, llcrnrlon=-74.2, llcrnrlat=40.5, urcrnrlon=-73.58, urcrnrlat=40.9, resolution='f')
map.fillcontinents(color='darkgreen', lake_color='aqua')
map.drawmapboundary(fill_color='aqua')
map.readshapefile('/Users/jaeyu2/Documents/Other/Jumpman23/geo_export_b4191298-31a6-4cb4-8c99-2e171192d0bb', 'borough', color='aqua')

dropoff_lons = jumpman.dropoff_coordinate.str.split(', ', expand=True)[1]
dropoff_lats = jumpman.dropoff_coordinate.str.split(', ', expand=True)[0]
dropff_lons, dropoff_lats = map(dropoff_lons, dropoff_lats)

#Note: Plot takes in longitudes first, latitude second

map.plot(dropoff_lons, dropoff_lats, 'bo', color='coral', markersize=0.5)

pick_map = Basemap(projection='cyl', lat_0=40.7, lon_0=-74, llcrnrlon=-74.2, llcrnrlat=40.5, urcrnrlon=-73.58, urcrnrlat=40.9, resolution='f')
pick_map.fillcontinents(color='darkgreen', lake_color='aqua')
pick_map.drawmapboundary(fill_color='aqua')
pick_map.readshapefile('/Users/jaeyu2/Documents/Other/Jumpman23/geo_export_b4191298-31a6-4cb4-8c99-2e171192d0bb', 'borough', color='aqua')

pickup_lons = jumpman.pickup_coordinate.str.split(', ', expand=True)[1]
pickup_lats = jumpman.pickup_coordinate.str.split(', ', expand=True)[0]
pickup_lons, pickup_lats = pick_map(pickup_lons, pickup_lats)

pick_map.plot(pickup_lons, pickup_lats, 'bo', color='papayawhip', markersize=0.5)
