import pandas as pd

jumpman = pd.read_csv('analyze_me.csv')

#Order dates & times are grouped together; splitting them up

jumpman = jumpman.join(jumpman.when_the_delivery_started.str.split(' ', expand=True).rename(columns = {0:'delivery_start_date', 1:'delivery_start_time'}))
jumpman = jumpman.join(jumpman.when_the_Jumpman_arrived_at_pickup.str.split(' ', expand=True).rename(columns = {0:'pickup_arrival_date', 1: 'pickup_arrival_time'}))
jumpman = jumpman.join(jumpman.when_the_Jumpman_left_pickup.str.split(' ', expand=True).rename(columns = {0:'pickup_depart_date', 1:'pickup_depart_time'}))
jumpman = jumpman.join(jumpman.when_the_Jumpman_arrived_at_dropoff.str.split(' ', expand=True).rename(columns = {0:'dropoff_date', 1:'dropoff_time'}))

#Deleting extraneous columns

jumpman.drop(jumpman.columns[[14,15,16,17]],1,inplace=True)

#Categorizing by long/lat to identify boroughs & distance b/n pick-up & drop-off
#Using GoogleMaps Geocoding API: https://developers.google.com/maps/documentation/geocoding/start

import googlemaps
gmaps = googlemaps.Client(key='INPUT KEY HERE')

jumpman.dropoff_lat = jumpman.dropoff_lat.astype(str)
jumpman.dropoff_lon = jumpman.dropoff_lon.astype(str)
jumpman.pickup_lat = jumpman.pickup_lat.astype(str)
jumpman.pickup_lon = jumpman.pickup_lon.astype(str)

jumpman['pickup_coordinate'] = jumpman.pickup_lat + ', ' + jumpman.pickup_lon
jumpman['dropoff_coordinate'] = jumpman.dropoff_lat + ', ' + jumpman.dropoff_lon

jumpman.drop(jumpman.columns[[10,11,12,13]],1,inplace=True)

hoods_geo = jumpman.pickup_coordinate.tolist() + jumpman.dropoff_coordinate.tolist()
hoods_geo = set(hoods_geo)

def hood_finder(x):
    hood = gmaps.reverse_geocode(x)
    count = 0
    for i in range(0,len(hood[0])):
        if hood[0]['address_components'][i]['types'] == ['neighborhood', 'political']:
            return hood[0]['address_components'][i]['long_name']
        elif hood[0]['address_components'][i]['types'] == ['political', 'sublocality', 'sublocality_level_1']:
            return hood[0]['address_components'][i]['long_name']

hoods_list = list(map(hood_finder, hoods_geo))
hoods_dict = dict(zip(hoods_geo, hoods_list))

def matcher(x):
    return hoods_dict[x]

jumpman['pickup_hood'] = jumpman.pickup_coordinate.apply(matcher)
jumpman['dropoff_hood'] = jumpman.dropoff_coordinate.apply(matcher)

#A manual key for all the neighborhoods

borough_gen = sorted(set(hoods_list))
borough= ['Manhattan', 'Brooklyn', 'Brooklyn', 'Brooklyn', 'Brooklyn', 'Brooklyn', 'Manhattan', 'Brooklyn', 'Manhattan', 'Brooklyn', 'Brooklyn', 'Brooklyn', 'Brooklyn', 'Brooklyn', 'Brooklyn', 'Manhattan', 'Manhattan', 'Brooklyn', 'Brooklyn', 'Brooklyn', 'Brooklyn', 'Brooklyn', 'Brooklyn', 'Manhattan', 'Manhattan', 'Manhattan', 'Queens', 'Manhattan', 'Manhattan', 'Manhattan', 'Manhattan', 'Manhattan', 'Manhattan', 'Brooklyn', 'Brooklyn', 'Brooklyn', 'Queens', 'Manhattan', 'Manhattan', 'Manhattan', 'Brooklyn', 'Brooklyn', 'Manhattan']
borough_dict = dict(zip(borough_gen, borough))

def borough_match(x):
    return borough_dict[x]

jumpman['pickup_borough'] = jumpman.pickup_hood.apply(borough_match)
jumpman['dropoff_borough'] = jumpman.dropoff_hood.apply(borough_match)

#Returning as CSV so that we don't have to call the API each time

jumpman.to_csv('jumpman.csv')"""
