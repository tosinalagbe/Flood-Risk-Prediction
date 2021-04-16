"""Live and historical flood monitoring data from the Environment Agency API"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


__all__  = []

LIVE_URL = "http://environment.data.gov.uk/flood-monitoring/id/stations"
ARCHIVE_URL = "http://environment.data.gov.uk/flood-monitoring/archive/"


#requirement 4

# DataF_history = pd.read_csv('https://environment.data.gov.uk/flood-monitoring/data/readings?date=2019-10-06)
# DataF_history = pd.read_csv('http://environment.data.gov.uk/flood-monitoring/archive/readings-2019-10-06.csv')

date = input("Please input the date(YYYY-MM-DD):")
DataF_history = pd.read_csv('http://environment.data.gov.uk/flood-monitoring/archive/readings-full-'+date+'.csv')
history = DataF_history.loc[DataF_history.parameter == 'rainfall']
h_data = history.loc[:,['dateTime','stationReference','value']]
# h_data
DataF_station = pd.read_csv('http://environment.data.gov.uk/flood-monitoring/id/stations.csv?parameter=rainfall')
station = DataF_station.loc[:, ['stationReference', 'lat', 'long','easting', 'northing']]#latitude longitude
DataF_R4 = pd.merge(h_data, station, on = ['stationReference'])
DataF_R4.value = pd.to_numeric(DataF_R4.value,errors='coerce')
uk_mean = DataF_R4.groupby('stationReference').mean()
uk_sum = DataF_R4.groupby('stationReference').sum()
uk_max = DataF_R4.groupby('stationReference').max()

# select case
print('Please select:')
print('1: UK Maximum Instantaneous Rainfall Map')
print('2: UK daily-total Rainfall Map')
print('3: Weather Station which has the highest daily-averaged rainfall')

sel = input('Number:')
sel = str(sel)

if sel == '1' or sel == '2': 
    if sel == '1':
        # notice: lat & lon remain the same after average
        uk_rainfall = uk_mean
        uk_rainfall.value = uk_max.value
        title = 'UK Maximum Instantaneous Rainfall Map on '+date
        cmin,cmax = 0, 8
        
    if sel == '2':
        # assign total rainfall from uk_sum
        uk_rainfall = uk_mean
        uk_rainfall.value = uk_sum.value
        title = 'UK daily-total Rainfall Map on '+date
        cmin,cmax = 0, 100
    
    # Start to plot
    colors = np.array(uk_rainfall.value)
    lat = np.array(uk_rainfall.lat)
    lon = np.array(uk_rainfall.long)

    plt.figure()
    plt.scatter(lon, lat, s=8, c=colors, alpha=0.5,cmap='jet')

    # import then plot UK coastline data
    gb_coast = np.load('./flood_tool/resources/gb_coastline.npy')
    # gb_coast = np.load('gb_coastline.npy')
    plt.plot(gb_coast[:,1],gb_coast[:,0],'k')

    plt.title(title)
    plt.xlabel('Longitute (degree)')
    plt.ylabel('Latitude (degree)')
    cbar = plt.colorbar()
    plt.clim(cmin,cmax)
    cbar.set_label('Total Rainfall (mm)')
    plt.gca().set_aspect('equal',adjustable='box')

    print('Please select:')
    print('1: print on screen')
    print('2: save figure at working directory')
    sel = input('Number:')
    sel = str(sel)
    if sel == '1':
        plt.show()

    elif sel == '2':
        title = title + '.png'
        plt.savefig(title)
        print('Figure has been saved!')

    else:
        print('Input not valid!!')

elif sel == '3':
    DataF_R4.dateTime = pd.to_datetime(DataF_R4.dateTime)
    station_mean = DataF_R4.groupby('stationReference').value.mean()
    # station_mean
    DataF_mean1 = DataF_R4.sort_values("value",inplace=True,ascending=False)
    DataF_mean1 = DataF_R4[0:5]
    stationR = DataF_mean1.stationReference
    data_mean = DataF_mean1.stationReference.iloc[0]
    
    print("The highest average rainfall occurred in "+data_mean+" station")
    


    DataF_R4.groupby('dateTime').value.mean()
    DataF_R4.sort_values("value",inplace=True,ascending=False)
    DataF_mean1 = DataF_R4[0:5]
    dateT = DataF_mean1.dateTime
    data_max = DataF_mean1.dateTime.iloc[0]
    print("The highest average rainfall occurred in "+str(data_max))
    

    DataF_R4.groupby('stationReference').value.max()
    DataF_R4.sort_values("value",inplace=True,ascending=False)
    DataF_max = DataF_R4[0:5]
    stationR = DataF_max.stationReference
    data_max0 = DataF_max.stationReference.iloc[0]
    print("The highest instantaneous rainfall occurred in "+data_max0+" station")

    DataF_R4.groupby('dateTime').value.max()
    DataF_R4.sort_values("value",inplace=True,ascending=False)
    DataF_max1 = DataF_R4[0:5]
    dateT1 = DataF_max1.dateTime
    data_max1 = DataF_max1.dateTime.iloc[0]
    print("The highest instantaneous rainfall occurred in "+str(data_max1))
    
    DataF_R4.groupby('stationReference').value.mean()
    DataF_R4.sort_values("dateTime",inplace=True,ascending=True)
    data = DataF_R4.loc[DataF_R4.stationReference==data_mean]
    dateTime = data.dateTime
    value = data.value
    
    plt.figure()
    time = np.linspace(0,24,len(dateTime))
    image = plt.plot(time,value)
    plt.xticks(np.linspace(0,24,9))
    plt.xlabel("Datetime")
    plt.ylabel("Rainfall (mm)")
    title = "Average Rainfall Time Serires for the station on " +date 
    plt.title(title)
    
    print('Please select:')
    print('1: print on screen')
    print('2: save figure at working directory')
    sel = input('Number:')
    sel = str(sel)
    if sel == '1':
        plt.show()

    elif sel == '2':
        title = title + '.png'
        plt.savefig(title)
        print('Figure has been saved!')

    else:
        print('Input not valid!!')
    
else:
    raise ValueError
