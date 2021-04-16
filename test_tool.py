import unittest
import flood_tool.geo
import flood_tool.tool as tool
import numpy as np
import pandas as pd
import os


"""Unit test suite to validate methods in tool file"""

class TestTool(unittest.TestCase):

    def setUp(self):
        """Initial set up to load tool data and testcases
        Includes test cases for valid and invalid postcodes, clean and dirty postcodes, and duplicate postcodes"""
        self.tool = tool.Tool()
        
        self.valid_clean_postcodes = ['CT147NW','DA9 9TY','CT3 3EL','DA2 6LL']
        self.valid_dirty_postcodes = ['cT14 7nW','da99ty','cT3 3eL','dA26lL']
        self.desired_lat_long_from_valid_postcodes = np.array([[51.200131, 1.395154],
                                                               [51.444248, 0.275078],
                                                               [51.22145, 1.196329],
                                                               [51.437398, 0.250708]] )
                                                               
        self.actual_lat_long_from_valid_clean_postcodes = self.tool.get_lat_long(self.valid_clean_postcodes)
        self.actual_lat_long_from_valid_dirty_postcodes = self.tool.get_lat_long(self.valid_dirty_postcodes) 
    
        self.invalid_postcodes = ['tosin', 'marion', 'nemo','DA9w9TY', 'invalid postcode']
        self.desired_lat_long_from_invalid_postcodes = np.full((len(self.invalid_postcodes),2), np.nan)
        self.actual_lat_long_from_invalid_postcodes = self.tool.get_lat_long(self.invalid_postcodes)

        self.valid_invalid_clean_postcodes = ['tosin','DA9 9TY', 'invalid postcode', 'CT3 3EL', 'CT147NW' ]
        self.valid_invalid_dirty_postcodes = ['tosin','Da99Ty', 'invalid postcode', 'Ct33EL', 'Ct14 7nW']
        self.desired_lat_long_from_valid_invalid_postcodes = np.array([[np.nan, np.nan],
                                                                             [51.444248,0.275078],
                                                                             [np.nan, np.nan],
                                                                             [51.22145,1.196329],
                                                                             [51.200131, 1.395154]])
        self.actual_lat_long_from_valid_invalid_clean_postcodes = self.tool.get_lat_long(self.valid_invalid_clean_postcodes)
        self.actual_lat_long_from_valid_invalid_dirty_postcodes = self.tool.get_lat_long(self.valid_invalid_dirty_postcodes)

        self.easting_array = [605197, 572869,554385, 601592]
        self.northing_array = [126960, 147575, 172531, 161987]
        self.desired_probabilty_from_easting_northing = np.array(['Very Low','Zero','Medium','High'])
        self.actual_probability_from_easting_northing = self.tool.get_easting_northing_flood_probability(self.easting_array, self.northing_array)

        self.valid_invalid_duplicate_postcodes = ['tosin', 'Ct14 7Pf', 'DA1 1PT', 'tosin', 'DA99nT','cT147PF', 'da11Pt' ]
        self.desired_sorted_flood_brobability_df = pd.DataFrame({'Postcode':['DA1 1PT','DA9 9NT','CT147PF'], 'Probability Band': np.array(['Medium','Low', 'Zero']) }).set_index("Postcode")
        self.actual_sorted_flood_probability_df = self.tool.get_sorted_flood_probability(self.valid_invalid_duplicate_postcodes)

        self.desired_flood_costs = np.array([np.nan, 0.0, 1406250.17, np.nan, 0.0, 0.0, 1406250.17])
        self.actual_flood_costs = self.tool.get_flood_cost(self.valid_invalid_duplicate_postcodes)

        self.desired_flood_costs_for_invalid_postcodes = np.full(len(self.invalid_postcodes), np.nan)
        self.actual_flood_costs_for_invalid_postcodes = self.tool.get_flood_cost(self.invalid_postcodes)

        self.desired_annual_flood_risk = np.array([np.nan, 0.0, 1406.25017, np.nan, 0.0, 0.0, 1406.25017])
        self.actual_annual_flood_risk = self.tool.get_annual_flood_risk(self.valid_invalid_duplicate_postcodes, ['Zero', 'Zero', 'Medium', 'Zero', 'Low', 'Zero', 'Medium'])
        
        self.desired_sorted_annual_flood_risk_df = pd.DataFrame({'Postcode':['DA1 1PT', 'CT147PF', 'DA9 9NT' ], 'Flood Risk':np.array([1406.25017, 0.0, 0.0])}).set_index("Postcode")
        self.actual_sorted_annual_flood_risk_df = self.tool.get_sorted_annual_flood_risk(self.valid_invalid_duplicate_postcodes)
                                                           
    def test_get_lat_long(self):
        """Test to validate get_lat_long method"""
        #test for all valid postcodes
        np.testing.assert_almost_equal(self.actual_lat_long_from_valid_clean_postcodes, self.desired_lat_long_from_valid_postcodes)
        np.testing.assert_almost_equal(self.actual_lat_long_from_valid_dirty_postcodes, self.desired_lat_long_from_valid_postcodes)
        #test for all invalid postcodes
        np.testing.assert_allclose(self.actual_lat_long_from_invalid_postcodes, self.desired_lat_long_from_invalid_postcodes,equal_nan = True)
        #test for valid and invalid clean postcodes
        np.testing.assert_allclose(self.actual_lat_long_from_valid_invalid_clean_postcodes, self.desired_lat_long_from_valid_invalid_postcodes,equal_nan = True)
        #test for valid and invalid dirty postcodes
        np.testing.assert_allclose(self.actual_lat_long_from_valid_invalid_dirty_postcodes, self.desired_lat_long_from_valid_invalid_postcodes, equal_nan = True )

    def test_get_easting_northing_flood_probability(self):
        """Test to validate get_easting_northing_flood_probability method """
        np.testing.assert_array_equal(self.actual_probability_from_easting_northing, self.desired_probabilty_from_easting_northing)

    def test_get_sorted_flood_probability(self):
        """Test to validate get_sorted_flood_probability method """
        pd.testing.assert_frame_equal(self.actual_sorted_flood_probability_df, self.desired_sorted_flood_brobability_df)
    
    def test_get_flood_cost(self):
        """Test to validate get_flood_cost method """
        np.testing.assert_allclose(self.actual_flood_costs, self.desired_flood_costs,equal_nan = True)
        #test for all invalid postcodes
        np.testing.assert_allclose(self.actual_flood_costs_for_invalid_postcodes, self.desired_flood_costs_for_invalid_postcodes)
    
    def test_get_annual_flood_risk(self):
        """Test to validate get_annual_flood_risk method """
        np.testing.assert_allclose(self.actual_annual_flood_risk, self.desired_annual_flood_risk, equal_nan = True)

    def test_get_sorted_annual_flood_risk(self):
        """Test to validate get_sorted_annual_flood_risk method """
        pd.testing.assert_frame_equal(self.actual_sorted_annual_flood_risk_df, self.desired_sorted_annual_flood_risk_df)


if __name__ == '__main__':
    unittest.main()

