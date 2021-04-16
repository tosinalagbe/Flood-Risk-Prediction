## Flood Risk Prediction tool

In environmental hazard assessment, risk is defined as the probability of a hazardous event occuring multiplied by the consequences of that event. Thus high risk can be the result of frequent events of low consequence or rare events of high consequence; the highest risk scenarios are often not obvious.

The Environment Agency routinely collects data on rainfall, sea level and river discharge and has published flooding probability maps that indicate areas of England that fall within four flood probability bands, based on the recurrence interval of flood levels that cause property damage and threat to life. These bands are very low probability (flooding expected once per 1000 years), low probability (flooding expected once per 100 years), medium probability (flooding expected once per 50 years), and high probability (flooding expected once per 10 years).

This tool calculates flood probabilities and risks for postcodes in England.

### Installation Guide

Please click ‘Clone or download ‘button and you will get whole project of ’acse-4-flood-tool-bann’.
Before running tool, ‘postcodes.csv’, ‘flood_probability.csv’ and ‘property_value.csv’ are under ‘./acse-4-flood-tool-bann/flood_tool/resources/’, and users can replace or update their data.
After replacing or updating data, user can start to run 'user_interface.py' and ‘analysis_date_rainfall.py’.

### User instructions

'user_interface.py' is the user interface built to access real time rainfall data from the Environment Agency API. 
The user should input a path to list of postcodes on line 12.
It returns and saves results in the './results' directory: 'flood_prob.csv' contains postcode and flood probability band in decreasing order of probability; 'flood_risk.csv' contains postcode and flood risk values in decreasing order of flood risk; 'flood_data.csv' contains various data for all input postcodes in alphabetical order; 'probability_band.png' maps the flood probability bands on the GB map and region of interest; 'risk_value.png' maps the flood risk values on the GB map and region of interest; 'rainfall_value.png' maps the rainfall values on the GB map and region of interest; 'warning.png' maps the warnings on the GB map and region of interest.
To run 
```
'python user_interface.py'.
```

‘analysis_date_rainfall.py’ is the analysis of a specified day’s rainfall.


To run an analysis of the rainfall on a particular date, please change your working directory to 'acse-4-flood-tool-bann' then run
```
'python analysis_date_rainfall.py'.
```

When users run this file with Python, you can enter a date (YYYY-MM-DD) that you want to analysis, and then, please press a button (‘ENTER’) using the keyboard to get analysis.

'analysis_date_rainfall.py' provides three main functions:
  1. providing UK maximum instantaneous rainfall map on a specified date
  2. providing UK daily-total rainfall map on a specified date
  3. picking up the station name and datetime of the highest daily-average and instantaneous rainfall across UK  
  
  for plotting a map or rainfall series, you can choose print the result on screen or save it as a png file in 'acse-4-flood-tool-bann' folder.
  
  To check if your postcode area is at risk of flooding and also check the flood cost, run:
  ```
  python flood_warning_script.py <postcode>
  ```
  For example: python flood_warning_script.py DA1 2NE







