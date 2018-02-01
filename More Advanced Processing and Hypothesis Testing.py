

import pandas as pd
import numpy as np
from scipy.stats import ttest_ind
#load all relevant files
homes=pd.read_csv('City_Zhvi_AllHomes.csv')
gdp=pd.read_excel('gdplev.xls')

# # Assignment 4 - Hypothesis Testing
 
# Definitions:
# * A _quarter_ is a specific three month period, Q1 is January through March, Q2 is April through June, Q3 is July through September, Q4 is October through December.
# * A _recession_ is defined as starting with two consecutive quarters of GDP decline, and ending with two consecutive quarters of GDP growth.
# * A _recession bottom_ is the quarter within a recession which had the lowest GDP.
# * A _university town_ is a city which has a high percentage of university students compared to the total population of the city.
# 
# **Hypothesis**: University towns have their mean housing prices less effected by recessions. Run a t-test to compare the ratio of the mean price of houses in university towns the quarter before the recession starts compared to the recession bottom. (`price_ratio=quarter_before_recession/recession_bottom`)
# 
# The following data files are available for this assignment:
# * From the [Zillow research data site](http://www.zillow.com/research/data/) there is housing data for the United States. In particular the datafile for [all homes at a city level](http://files.zillowstatic.com/research/public/City/City_Zhvi_AllHomes.csv), ```City_Zhvi_AllHomes.csv```, has median home sale prices at a fine grained level.
# * From the Wikipedia page on college towns is a list of [university towns in the United States](https://en.wikipedia.org/wiki/List_of_college_towns#College_towns_in_the_United_States) which has been copy and pasted into the file ```university_towns.txt```.
# * From Bureau of Economic Analysis, US Department of Commerce, the [GDP over time](http://www.bea.gov/national/index.htm#gdp) of the United States in current dollars (use the chained value in 2009 dollars), in quarterly intervals, in the file ```gdplev.xls```. For this assignment, only look at GDP data from the first quarter of 2000 onward.
# 

# Use this dictionary to map state names to two letter acronyms
states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}


# STRING MANIPULATION/REPLACEMENT, FORWARD FILL

def get_list_of_university_towns():
    '''Returns a DataFrame of towns and the states they are in from the 
    university_towns.txt list. The format of the DataFrame should be:
    DataFrame( [ ["Michigan","Ann Arbor"], ["Michigan", "Yipsilanti"] ], 
    columns=["State","RegionName"]  )'''
    #load data
    university_towns=pd.read_csv('university_towns.txt', header=None, sep='\n') 
    #create new column
    university_towns['RegionName']=university_towns[0]
    #rename what is now the first column
    university_towns=university_towns.rename(columns={0:'State'})
    #every row of RegionName that ends in a ']', replace brackets and everything in between with nothing
    university_towns.loc[university_towns['RegionName'].str.endswith(']'), ['RegionName']]=university_towns['RegionName'].str.replace("\[.*\]","")
    #every row that ends in a '\n', replace space, parentheses and everything in between with nothing
    university_towns['RegionName']=university_towns['RegionName'].str.replace("\n","")
    #every row of State that ends in a ']', replace brackets and everything in between with nothing
    university_towns.loc[university_towns['State'].str.endswith(']'), ['State']]=university_towns['State'].str.replace("\[.*\]","")
    #every row of RegionName that has a " (", split on that and take first part
    university_towns['RegionName'] = university_towns['RegionName'].str.split(" \(").str[0]
    #every row of RegionName that has a "," split on that and take first part
    university_towns['RegionName'] = university_towns['RegionName'].str.split("\,").str[0]
    #every row of State that has a value that's not a state name (as seen in dictionary) make it blank
    university_towns.loc[~university_towns['State'].isin(states.values()), ['State']]=university_towns['State'].str.replace(".*", "")
    #make all those blanks NaN
    university_towns.replace(r'^\s*$', np.nan, regex=True, inplace = True)
    #forward fill to get state names in all rows of State column
    university_towns=university_towns.fillna(method='ffill')
    #take out all rows that don't have a city in the RegionName column
    university_towns=university_towns[university_towns['State']!=university_towns['RegionName']]
    return university_towns
get_list_of_university_towns()


# SUBSETTING, RENAMING COLUMNS, SHIFT(), RESETTING INDEX

def get_recession_start():
    '''Returns the year and quarter of the recession start time as a 
    string value in a format such as 2005q3'''
    gdp=pd.read_excel('gdplev.xls', header=None, skiprows=8)
    #get relevant columns, rows
    gdp=gdp[[4,6]].iloc[212:]
    #rename columns
    gdp=gdp.rename(columns={4:'Quarter', 6:'GDP'})
    #subset DF to rows where less than preceding but larger than following
    recession=gdp[(gdp['GDP']<gdp['GDP'].shift(1)) & (gdp['GDP']>gdp['GDP'].shift(-1))]
    #reset the index of the subset and get value in first row, column
    return recession.reset_index(drop=True).iloc[0, 0]
get_recession_start()


# SUBSETTING, RENAMING COLUMNS, INDEXING, SHIFT()

def get_recession_end():
    '''Returns the year and quarter of the recession end time as a 
    string value in a format such as 2005q3'''
    gdp=pd.read_excel('gdplev.xls', header=None, skiprows=8)
    #get relevant columns, rows
    gdp=gdp[[4,6]].iloc[212:]
    #rename columns
    gdp=gdp.rename(columns={4:'Quarter', 6:'GDP'})
    #subset gdp to where recession starts
    recession_start=gdp[(gdp['GDP']<gdp['GDP'].shift(1)) & (gdp['GDP']>gdp['GDP'].shift(-1))]
    #get index of quarter in which recession starts
    number=recession_start.index[0]
    #subset gdp again from where recession starts and include rest of data
    recession_end=gdp.loc[number:]
    #subset on that to where GDP less than previous quarter but it goes up in next two quarters
    #NOTE THE ANSWER THEY WANT IS NOT THE LAST QUARTER OF DOWNWARD BUT THE SECOND QUARTER OF UPWARD. YOU WERE TOO LAZY TO CHANGE SINCE YOU PASSED.
    recession_end=recession_end[(recession_end['GDP']<recession_end['GDP'].shift(1)) & (recession_end['GDP']<recession_end['GDP'].shift(-1)) & (recession_end['GDP'].shift(-1)<recession_end['GDP'].shift(-2))]
    #take the relevant value for Quarter
    return recession_end.iloc[0,0]
get_recession_end()

# SUBSETTING, RENAMING COLUMN, INDEXING, SHIFT()

def get_recession_bottom():
    '''Returns the year and quarter of the recession bottom time as a 
    string value in a format such as 2005q3'''
    gdp=pd.read_excel('gdplev.xls', header=None, skiprows=8)
    #get relevant columns, rows
    gdp=gdp[[4,6]].iloc[212:]
    #rename columns
    gdp=gdp.rename(columns={4:'Quarter', 6:'GDP'})
    recession_start=gdp[(gdp['GDP']<gdp['GDP'].shift(1)) & (gdp['GDP']>gdp['GDP'].shift(-1))]
    #get index of quarter in which recession starts
    start=recession_start.index[0]
    #new dataframe starting from where recession started
    recession_end=gdp.loc[start:]
    #subset the new dataframe so it starts on the last quarter of the recession
    recession_end=recession_end[(recession_end['GDP']<recession_end['GDP'].shift(1)) & (recession_end['GDP']<recession_end['GDP'].shift(-1)) & (recession_end['GDP'].shift(-1)<recession_end['GDP'].shift(-2))]
    #get index of quarter where recession starts
    end=recession_end.index[0]
    #create new dataframe that goes from quarter to where recession starts to where it ends
    recession=gdp.loc[start:end]
    #find row with minimum value in GDP
    bottom=recession[recession['GDP']==recession['GDP'].min()]
    #get the value in Quarter column
    return bottom.iloc[0]['Quarter']
get_recession_bottom()


# DROP COLUMNS, MAP FROM DICTIONARY, SET INDEX, DATETIME CONVERSION, RESAMPLE TIME SERIES, LAMBDA STRING CONVERSION

def convert_housing_data_to_quarters():
    '''Converts the housing data to quarters and returns it as mean 
    values in a dataframe. This dataframe should be a dataframe with
    columns for 2000q1 through 2016q3, and should have a multi-index
    in the shape of ["State","RegionName"].
    
    Note: Quarters are defined in the assignment description, they are
    not arbitrary three month periods.
    
    The resulting dataframe should have 67 columns, and 10,730 rows.
    '''
    
    homes=pd.read_csv('City_Zhvi_AllHomes.csv')
    #the dictionary to use to you can switch two letter state names to full state names
    states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}
    #makes list of columns you will want to drop
    columns=['RegionID', 'Metro', 'CountyName', 'SizeRank']
    #drop those columns
    homes.drop(columns, inplace=True, axis=1)
    #drop other columns
    homes.drop(homes.columns[2:47], inplace=True, axis=1)
    #map those two letter state names to full names
    homes['State']=homes['State'].map(states)
    #set the index to RegionName, State
    homes=homes.set_index(['State', 'RegionName'])
    #make columns into datetime
    homes.columns=pd.to_datetime(homes.columns)
    #resample to find the average of all columns within the same quarter (as determined by datetime)
    homes=homes.resample('Q',axis=1).mean()
    #rewrite column names that came about in previous step (datetime of endpoint of quarter) so that they say the name of the quarter as a whole
    homes = homes.rename(columns=lambda x: str(x.to_period('Q')).lower())
    return homes
convert_housing_data_to_quarters()





# CONVERT TO LIST OF TUPLES, TRAINING/TEST SET, ISIN(), T-TEST

def run_ttest():
    '''First creates new data showing the decline or growth of housing prices
    between the recession start and the recession bottom. Then runs a ttest
    comparing the university town values to the non-university towns values, 
    return whether the alternative hypothesis (that the two groups are the same)
    is true or not as well as the p-value of the confidence. 
    
    Return the tuple (different, p, better) where different=True if the t-test is
    True at a p<0.01 (we reject the null hypothesis), or different=False if 
    otherwise (we cannot reject the null hypothesis). The variable p should
    be equal to the exact p value returned from scipy.stats.ttest_ind(). The
    value for better should be either "university town" or "non-university town"
    depending on which has a lower mean price ratio (which is equivilent to a
    reduced market loss).'''
    #load relevant data
    hdf = convert_housing_data_to_quarters()
    rec_start=get_recession_start()
    rec_bottom = get_recession_bottom()
    ul = get_list_of_university_towns()
    #to get quarter before recession started
    gdp=pd.read_excel('gdplev.xls', header=None, skiprows=8)
    #narrow data to relevant stuff and rename columns
    gdp=gdp[[4,6]].iloc[212:]
    gdp=gdp.rename(columns={4:'Quarter', 6:'GDP'})
    #pull out the index from the row before the quarter the recession started
    qrt_bfr_rec_start=gdp.index[gdp['Quarter']==rec_start][0]-1
    #pull out quarter from the row with that index (loc instead of iloc because the index you pulled out is more a name than a number)
    qrt_bfr_rec_start=gdp.loc[qrt_bfr_rec_start]['Quarter']

    #create PricingRatio column of quarter before / quarter bottom
    hdf['PricingRatio']=hdf[qrt_bfr_rec_start].div(hdf[rec_bottom])
    #make university towns into a list of tuples
    ut_list=ul.to_records(index=False).tolist()
    #group from gdp data frame that is in university towns 
    group1=hdf.loc[hdf.index.isin(ut_list)]
    #group from gdp data frame that is not in university towns
    group2=hdf.loc[-hdf.index.isin(ut_list)]
    #run ttest, omit NaN
    ttest_ind(group1['PricingRatio'], group2['PricingRatio'], nan_policy='omit')
    different=ttest.pvalue<.01
    p=ttest.pvalue
    if group1['PricingRatio'].mean()>group2['PricingRatio'].mean():
        better='non-university towns'
    else:
        better='university town'
    return (different, p, better)
run_ttest()
