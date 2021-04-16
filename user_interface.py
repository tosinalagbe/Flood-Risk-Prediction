""" Output user interface for flood_tool. """

# INITIALISE INTERFACE
import numpy as np
import pandas as pd
import flood_tool.tool as tool
import flood_tool.geo as geo
from flood_tool.api_functions import *
from flood_tool.my_plot_functions import *

# USER TO IMPORT POSTCODES OF INTEREST
test_data = pd.read_csv('./flood_tool/tests/test_data.csv')

# LOAD REQUIRED DATA
postcodes = test_data['Postcode']
data = pd.DataFrame({'Postcode':postcodes})
data = pd.DataFrame.drop_duplicates(data)
data = data.reset_index(drop=True)
gb_coast = np.load('./flood_tool/resources/gb_coastline.npy')

# OBTAIN POSTCODE DATA
t = tool.Tool()
lat_long = t.get_lat_long(data.Postcode)
data['Latitude'] = lat_long[:,0]
data['Longitude'] = lat_long[:,1]
data = data[pd.notnull(data.Latitude)]
[data['Easting'],data['Northing']] = geo.get_easting_northing_from_lat_long(data.Latitude,data.Longitude)
data['Probability'] = t.get_easting_northing_flood_probability(data.Easting,data.Northing)
data['Int_probability'] = val_str2int(data.Probability)
data['Flood_risk'] = t.get_annual_flood_risk(data.Postcode,data.Probability)
data = get_flood_warning(data)
 
# PLOT BASIC DATA
# plot probability bands
data = data.sort_values(by='Int_probability')
data = data.reset_index(drop=True)
fig, axes = plt.subplots(1,2,figsize=(20, 10))
fig.suptitle('Flood probability for input postcodes', fontsize=20)
plt.sca(axes[0])
plt.plot(gb_coast[:,1],gb_coast[:,0],'k')
plot_map_band(data.Postcode,data.Latitude,data.Longitude,data.Probability)
plt.sca(axes[1])
plt.plot(gb_coast[:,1],gb_coast[:,0],'k')
plot_map_band(data.Postcode,data.Latitude,data.Longitude,data.Probability,True)
plt.savefig('./results/probability_band.png')
plt.show()
# plot flood risk
data = data.sort_values(by='Flood_risk')
data = data.reset_index(drop=True)
fig, axes = plt.subplots(1,2,figsize=(20, 10))
fig.suptitle('Annual flood risk for input postcodes', fontsize=20)
plt.sca(axes[0])
plt.plot(gb_coast[:,1],gb_coast[:,0],'k')
plot_map(data.Postcode,data.Latitude,data.Longitude,data.Flood_risk,'Risk (£/year)')
plt.sca(axes[1])
plt.plot(gb_coast[:,1],gb_coast[:,0],'k')
plot_map(data.Postcode,data.Latitude,data.Longitude,data.Flood_risk,'Risk (£/year)',True)
plt.savefig('./results/risk_value.png')
plt.show()
# TALK WITH API AND PRINT RESULTS
# plot rainfall
data = data.sort_values(by='Rainfall')
data = data.reset_index(drop=True)
fig, axes = plt.subplots(1,2,figsize=(20, 10))
fig.suptitle('Recent and live rainfall for input postcodes', fontsize=20)
plt.sca(axes[0])
plt.plot(gb_coast[:,1],gb_coast[:,0],'k')
plot_map(data.Postcode,data.Latitude,data.Longitude,data.Rainfall,'Rainfall (mm)')
plt.sca(axes[1])
plt.plot(gb_coast[:,1],gb_coast[:,0],'k')
plot_map(data.Postcode,data.Latitude,data.Longitude,data.Rainfall,'Rainfall (mm)',True)
plt.savefig('./results/rainfall_value.png')
plt.show()
# plot warning
data = data.sort_values(by='Flood_warning')
data = data.reset_index(drop=True) 
fig, axes = plt.subplots(1,2,figsize=(20, 10))
fig.suptitle('Recent and live warnings for input postcodes', fontsize=20)
plt.sca(axes[0])
plt.plot(gb_coast[:,1],gb_coast[:,0],'k')
plot_map(data.Postcode,data.Latitude,data.Longitude,data.Flood_warning,'Warning')
plt.sca(axes[1])
plt.plot(gb_coast[:,1],gb_coast[:,0],'k')
plot_map(data.Postcode,data.Latitude,data.Longitude,data.Flood_warning,'Warning',True)
plt.savefig('./results/warning.png')
plt.show()
# print warning to user
for lab, row in data[data.Flood_warning==1].iterrows() :
    print('/!\ Warning flood in ' + row['Postcode'] + " where a recent rainfall of " + str(row['Rainfall']) + " mm occured ")
    
# PRINT DATA AND SAVE
# print postcodes and probability in descending manner
data = data.sort_values(by='Int_probability',ascending=False)
data = data.reset_index(drop=True)
data[['Postcode','Probability']].to_csv('./results/flood_prob.csv')
# print postcodes and floodrisk in descending manner
data = data.sort_values(by='Flood_risk',ascending=False)
data = data.reset_index(drop=True)
data[['Postcode','Flood_risk']].to_csv('./results/flood_risk.csv')
# print all data in alphabetical postcode order
data = data.sort_values(by='Postcode')
data = data.reset_index(drop=True)
data.to_csv('./results/flood_data.csv')
