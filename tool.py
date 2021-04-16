import pandas as pd
import numpy as np
from .geo import *
import os

"""Locator functions to interact with geographic data"""

__all__ = ['Tool']

class Tool(object):
    """Class to interact with a postcode database file."""

    def __init__(self, postcode_file=None, risk_file=None, values_file=None):
        """
        Reads postcode and flood risk files and provides a postcode locator service.
        Parameters
        ---------
        postcode_file : str, optional
            Filename of a .csv file containing geographic location data for postcodes.
        risk_file : str, optional
            Filename of a .csv file containing flood risk data.
        values_file : str, optional
            Filename of a .csv file containing property value data for postcodes.
        """
        
        # Import postcode data
        if postcode_file == None:
            postcodes = pd.read_csv(os.getcwd()+'/flood_tool/resources/postcodes.csv')
        else:
            postcodes = pd.read_csv(postcode_file)
            
        # Import property values data
        if values_file == None:
            property_values = pd.read_csv(os.getcwd()+'/flood_tool/resources/property_value.csv')
        else:
            property_values = pd.read_csv(values_file)
        
        # Fill nan and set postcode type in property_values
        property_values = property_values[pd.notnull(property_values.Postcode)]
        property_values['Postcode_length'] = property_values['Postcode'].apply(len)
        correct = pd.DataFrame(property_values.loc[property_values.Postcode_length > 7].Postcode.map(lambda s: s.replace(' ','')))
        property_values.loc[property_values.Postcode_length > 7, 'Postcode'] = correct
        del property_values['Postcode_length']
        property_values.rename(columns={'Total Value': 'Total_value'}, inplace=True)
        
        # Import risk data
        if risk_file == None:
            self.risk_data = pd.read_csv(os.getcwd()+'/flood_tool/resources/flood_probability.csv')
        else:
            self.risk_data = pd.read_csv(risk_file)
        del self.risk_data['Unnamed: 0']
        
        # Merge postcode and property values 
        self.postcode_data = postcodes.set_index('Postcode').join(property_values.set_index('Postcode'))
        del self.postcode_data['Lat']
        del self.postcode_data['Long']
        self.postcode_data = self.postcode_data.fillna(0)
        pass
    

    def get_lat_long(self, postcodes):
        """Get an array of WGS84 (latitude, longitude) pairs from a list of postcodes.

        Parameters
        ----------

        postcodes: sequence of strs
            Ordered sequence of N postcode strings

        Returns
        -------
       
        ndarray
            Array of Nx2 (latitude, longitude) pairs for the input postcodes.
            Invalid postcodes return [`numpy.nan`, `numpy.nan`].
        """
        
        # Check postcodes syntax is correct
        postcodes = [pc.upper() for pc in postcodes]
        postcodes = [pc.replace(' ', '') if len(pc)>7 else pc for pc in postcodes]
        postcodes = [ pc[0:2]+'  '+pc[2:] if len(pc)==5 else pc for pc in postcodes]
        postcodes = [ pc[0:3]+' '+pc[3:] if (len(pc)==6) and (pc[2]!=' ') else pc for pc in postcodes]

        try:  
            # Fetch latitude and longitude values
            lat_long = self.postcode_data.loc[postcodes,['Latitude','Longitude']]
            return lat_long.values
        except KeyError:
            return np.full((len(postcodes),2), np.nan)

    
    def get_easting_northing_flood_probability(self, easting, northing):
        """Get an array of flood risk probabilities from arrays of eastings and northings.

        Flood risk data is extracted from the Tool flood risk file. Locations
        not in a risk band circle return `Zero`, otherwise returns the name of the
        highest band it sits in.

        Parameters
        ----------

        easting: numpy.ndarray of floats
            OS Eastings of locations of interest
        northing: numpy.ndarray of floats
            OS Northings of locations of interest

        Returns
        -------
       
        numpy.ndarray of strs
            numpy array of flood probability bands corresponding to input locations.
        # """
    
        if len(easting) != len(northing):
            print('Size of input mismatch')
            return None
        
        length_locations = len(easting)
        pb_result = []
        
        for j in range(length_locations):
            selected_area = self.risk_data.loc[(self.risk_data.X <= (easting[j] + self.risk_data.radius.max()))
                & (self.risk_data.X >= (easting[j]-self.risk_data.radius.max()))]
            selected_area = self.risk_data.loc[(self.risk_data.Y <= (northing[j]+self.risk_data.radius.max())) 
            & (self.risk_data.Y >= (northing[j]-self.risk_data.radius.max()))]
            count = np.array(selected_area.X.count())
            index_vals = selected_area.index[0:].values
            
            distance = np.sqrt((selected_area.X[index_vals]-easting[j])**2 + (selected_area.Y[index_vals]-northing[j])**2)
            condition = distance.le(selected_area.radius[index_vals]).values
            valid_index_values = index_vals[condition]
            ls = (selected_area.prob_4band[valid_index_values].values)
            if np.any(ls == 'High'):
                pb_result.append('High')  
        
            elif np.any(ls == 'Medium'):
                pb_result.append('Medium')
        
            elif np.any(ls == 'Low'):
                pb_result.append('Low')
        
            elif np.any(ls == 'Very Low'):
                pb_result.append('Very Low')
        
            else:
                pb_result.append('Zero')

        pb_result = np.asarray(pb_result)
        return pb_result
    

    def get_sorted_flood_probability(self, postcodes):
        """Get an array of flood risk probabilities from a sequence of postcodes.

        Probability is ordered High>Medium>Low>Very low>Zero.
        Flood risk data is extracted from the `Tool` flood risk file. 

        Parameters
        ----------

        postcodes: sequence of strs
            Ordered sequence of postcodes

        Returns
        -------
       
        pandas.DataFrame
            Dataframe of flood probabilities indexed by postcode and ordered from `High` to `Zero`,
            then by lexagraphic (dictionary) order on postcode. The index is named `Postcode`, the
            data column is named `Probability Band`. Invalid postcodes and duplicates
            are removed.
        """  
        # Check postcodes syntax is correct
        postcodes = [pc.upper() for pc in postcodes]
        postcodes = [pc.replace(' ', '') if len(pc)>7 else pc for pc in postcodes]
        postcodes = [ pc[0:2]+' '+pc[2:] if len(pc)==5 else pc for pc in postcodes]
        postcodes = [ pc[0:3]+' '+pc[3:] if (len(pc)==6) and (pc[2]!=' ') else pc for pc in postcodes]

        lat_long = self.get_lat_long(postcodes)
        
        #get index with nan lat_long
        nan_index = np.argwhere(np.isnan(lat_long))
        nan_index = np.unique(nan_index[:,0])
        
        #remove postcodes with nan lat_long(invalied postcodes)
        postcodes = np.delete(postcodes, tuple(nan_index))
        
        #remove nan lat_long values
        lat_long = lat_long[~np.isnan(lat_long).any(axis=1)]
       
        easting,northing = get_easting_northing_from_lat_long(lat_long[:,0], lat_long[:,1])
        p_bands = self.get_easting_northing_flood_probability(easting, northing)
        flood_prob_df = pd.DataFrame({'Postcode': postcodes, 'Probability Band': p_bands }).drop_duplicates()
        flood_prob_df['Probability Band'] = pd.Categorical(flood_prob_df['Probability Band'],['High','Medium','Low','Very Low', 'Zero'])
        flood_prob_df = flood_prob_df.set_index("Postcode").sort_values(by=['Probability Band', 'Postcode'])
        flood_prob_df['Probability Band'] = flood_prob_df['Probability Band'].astype(str)
        return flood_prob_df 
        

    def get_flood_cost(self, postcodes):
        """Get an array of estimated cost of a flood event from a sequence of postcodes.
        Parameters
        ----------

        postcodes: sequence of strs
            Ordered collection of postcodes

        Returns
        -------

        numpy.ndarray of floats
            array of floats for the pound sterling cost for the input postcodes.
            Invalid postcodes return `numpy.nan`.
        """
        # Check postcodes syntax is correct
        postcodes = [pc.upper() for pc in postcodes]
        postcodes = [pc.replace(' ', '') if len(pc)>7 else pc for pc in postcodes]
        postcodes = [ pc[0:2]+' '+pc[2:] if len(pc)==5 else pc for pc in postcodes]
        postcodes = [ pc[0:3]+' '+pc[3:] if (len(pc)==6) and (pc[2]!=' ') else pc for pc in postcodes]       

        try:
            flood_cost = self.postcode_data.loc[postcodes,['Total_value']]
            n,i = flood_cost.values.shape
            return flood_cost.values.reshape((n,))
        except KeyError:
            return np.full((len(postcodes),), np.nan)


    def get_annual_flood_risk(self, postcodes, probability_bands):
        """Get an array of estimated annual flood risk in pounds sterling per year of a flood
        event from a sequence of postcodes and flood probabilities.

        Parameters
        ----------

        postcodes: sequence of strs
            Ordered collection of postcodes
        probability_bands: sequence of strs
            Ordered collection of flood probabilities

        Returns
        -------

        numpy.ndarray
            array of floats for the annual flood risk in pounds sterling for the input postcodes.
            Invalid postcodes return `numpy.nan`.
        """ 

        prob_dict = {'High': 0.1, 'Medium': 0.02, 'Low': 0.01, 'Very Low': 0.001, 'Zero': 0.0}
        total_values = self.get_flood_cost(postcodes)
        prob_values = np.vectorize(prob_dict.get)(probability_bands)
        return np.array(0.05* prob_values *total_values)

         
    def get_sorted_annual_flood_risk(self, postcodes):
        """Get a sorted pandas DataFrame of flood risks.

        Parameters
        ----------

        postcodes: sequence of strs
            Ordered sequence of postcodes

        Returns
        -------
       
        pandas.DataFrame
            Dataframe of flood risks indexed by (normalized) postcode and ordered by risk,
            then by lexagraphic (dictionary) order on the postcode. The index is named
            `Postcode` and the data column `Flood Risk`.
            Invalid postcodes and duplicates are removed.
        """
        # Calculate probability of poscodes
        #function(get_sorted_flood_probability) can remove invalid postcodes and duplicates 
        flood_probability_df = self.get_sorted_flood_probability(postcodes)
        new_postcodes = flood_probability_df.index.values
        
        # Calculate annual_flood_risk of poscodes
        risk = self.get_annual_flood_risk(new_postcodes, flood_probability_df.values.reshape((-1)))
        
        annual_flood_risk = pd.DataFrame({'Postcode': new_postcodes, 'Flood Risk': risk})
        annual_flood_risk = annual_flood_risk.sort_values(by=['Flood Risk', 'Postcode'], ascending=[False, True])
        annual_flood_risk.set_index('Postcode', inplace=True)

        return annual_flood_risk
        
        


