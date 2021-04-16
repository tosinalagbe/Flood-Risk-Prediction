"""Live and historical flood monitoring data from the Environment Agency API"""
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import flood_tool.tool as tool
import flood_tool.geo as geo

import sys

arg_str = ' '.join(sys.argv[1:]) 
post_code = arg_str

#requirement3 
tl = tool.Tool()
r = str(10)
lat_long = tl.get_lat_long([post_code])
latitude = lat_long[0,0]
longitude = lat_long[0,1]
DataF_value = pd.read_csv('http://environment.data.gov.uk/flood-monitoring/id/measures.csv?parameter=rainfall')
value = DataF_value.loc[:, ['dateTime', 'stationReference', 'value']]
DataF_station = pd.read_csv('http://environment.data.gov.uk/flood-monitoring/id/stations.csv?parameter=rainfall&lat='+str(latitude)+'&long='+str(longitude)+'&dist='+r)
station = DataF_station.loc[:, ['stationReference', 'lat', 'long','easting', 'northing']]
station_ref = DataF_station.loc[:, 'stationReference'].values
ref = station_ref[0]
max_val = 0.0
for ref in station_ref:
    testt = pd.read_csv('http://environment.data.gov.uk/flood-monitoring/id/stations/'+str(ref)+'/readings.csv')
    temp_max = testt.loc[:,'value'].max()
    if temp_max > max_val:
        max_val = temp_max 

print("Maximum rain in your desired location over last 24hrs: "+ str(max_val) + " inches of rainfall")
if max_val <= 0.0:
    print("There has been no rainfall in your desired location in the last 24 hrs")
if max_val > 0 and max_val <= 0.1:
    print("There has been light rainfall in your desired location in the last 24 hrs")
if max_val > 0.1 and max_val <= 0.3:
    print("There has been moderate rainfall in your desired location in the last 24 hrs")
if max_val > 0.3:
    print("There has been heavy rainfall in your desired location!, please wait to see the" 
          "chance of flooding in this area...")

lat = [latitude]
longit = [longitude]

easting, northing = geo.get_easting_northing_from_lat_long(lat, longit)
probability = tl.get_easting_northing_flood_probability(easting, northing)
print("Your location has a "+ probability[0]+" chance of flooding")

print("now checking for flood risk based on property values in your area...")
flood_risk = tl.get_annual_flood_risk([post_code], [probability[0]])
print("Your desired location has a flood risk of: £"+str(flood_risk[0]) )

if max_val > 0.3 and (probability[0]=='Medium' or probability[0]=='High'):
    print("This area with postcode "+post_code+"is likely to be affected by Flood, BRACE YOURSELF!!!!")
else:
    print("This area with postcode "+post_code+" won't be affected by flood any time soon, cheers.")







