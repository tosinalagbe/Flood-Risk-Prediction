import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt
import os

date = input("Please input the date (must be from 2019 to date) (YYYY-MM-DD):")
print("Loading data...")
DataF_history = pd.read_csv('http://environment.data.gov.uk/flood-monitoring/archive/readings-full-'+str(date)+'.csv')
history = DataF_history.loc[DataF_history.parameter == 'rainfall']
h_data = history.loc[:,['dateTime','stationReference','value']]

DataF_station = pd.read_csv('http://environment.data.gov.uk/flood-monitoring/id/stations.csv?parameter=rainfall')
station = DataF_station.loc[:, ['stationReference', 'lat', 'long','easting', 'northing']]#latitude longitude
DataF_R4 = pd.merge(h_data, station, on = ['stationReference'])
DataF_R4.value = pd.to_numeric(DataF_R4.value,errors='coerce')
DataF_R4 = DataF_R4.dropna(axis=0,how='any')
uk_mean = DataF_R4.groupby('stationReference').mean()
uk_sum = DataF_R4.groupby('stationReference').sum()
uk_max = DataF_R4.groupby('stationReference').max()

print('Please select by input a number:')
print('1: View UK Maximum Instantaneous Rainfall Map on ' + date)
print('2: View UK daily-total Rainfall Map on ' + date)

sel = input('Number:')
sel = str(sel)

if sel == '1':
    # notice: lat & lon remain the same after average
    uk_rainfall = uk_mean
    uk_rainfall.value = uk_max.value
    title = 'UK Maximum Instantaneous Rainfall Map on '+date
    cmin,cmax = 0, 8


elif sel == '2':
    # assign total rainfall from uk_sum
    uk_rainfall = uk_mean
    uk_rainfall.value = uk_sum.value
    title = 'UK daily-total Rainfall Map on '+date
    cmin,cmax = 0, 100

else:
    raise ValueError

# Start to plot
colors = np.array(uk_rainfall.value)
lat = np.array(uk_rainfall.lat)
lon = np.array(uk_rainfall.long)

plt.figure()
plt.scatter(lon, lat, s=8, c=colors, alpha=0.5,cmap='jet')

# import then plot UK coastline data
gb_coast = np.load(os.getcwd()+'/flood_tool/resources/gb_coastline.npy')
# gb_coast = np.load('gb_coastline.npy')
plt.plot(gb_coast[:,1],gb_coast[:,0],'k')

plt.title(title)
plt.xlabel('Longitute (degree)')
plt.ylabel('Latitude (degree)')
cbar = plt.colorbar()
plt.clim(cmin,cmax)
cbar.set_label('Total Rainfall (mm)')
plt.show()
