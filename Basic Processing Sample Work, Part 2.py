

# # Assignment 3 - More Pandas


# ### Question 1 - LOADING DATA, STRING MANIPULATION, MERGING DATA FRAMES

import pandas as pd
import numpy as np


def answer_one():
    def energy():
        ##FIRST DATA FRAME
        ##open file and put into variable. pd.read_excel('Energy Indicators.xls', sheetname='Energy') works too
        energy = pd.read_excel(open('Energy Indicators.xls', 'rb'), sheetname='Energy')
        ##drop first two columns. axis=0 for row, 1 for column
        energy=energy.drop(energy.columns[[0,1]], axis=1)
        ##drop header and footer by just taking the relevant rows with values
        energy=energy.iloc[16:242]
        ##rename columns, Also works: energy.columns=['Country', 'Energy Supply', 'Energy Supply per Capita', '% Renewable']
        for col in energy.columns:
            if col=='Environmental Indicators: Energy':
                energy.rename(columns={col:'Country'}, inplace=True)
            if col=='Unnamed: 3':
                energy.rename(columns={col: 'Energy Supply'}, inplace=True)
            if col=='Unnamed: 4':
                energy.rename(columns={col: 'Energy Supply per Capita'}, inplace=True)
            if col=='Unnamed: 5':
                energy.rename(columns={col: '% Renewable'}, inplace=True)
        ##reset index so that it starts at 0 instead of 16 and delete the 'index' column that results and has the old humbers
        energy=energy.reset_index()
        del energy['index']
        ##where there is a '...' change it to NaN
        energy['Energy Supply per Capita']=energy['Energy Supply per Capita'].replace('...', value=np.NaN)
        energy['Energy Supply']=energy['Energy Supply'].replace('...', value=np.NaN)
        energy['% Renewable']=energy['% Renewable'].astype(np.float64)
        ##convert petajoules to gigajoules
        energy['Energy Supply']*=1000000
        ## set [condition: where Country value starts with x, Look at: Country column for that record] = to a value
        energy.loc[energy['Country'].str.startswith('United States of America'), ['Country']]='United States'
        energy.loc[energy['Country'].str.startswith('Republic of Korea'), ['Country']]='South Korea'
        energy.loc[energy['Country'].str.startswith('United Kingdom of Great Britain and Northern Ireland'), ['Country']]='United Kingdom' 
        energy.loc[energy['Country'].str.startswith('China, Hong Kong Special Administrative Region'), ['Country']]='Hong Kong' 
        ##any value in country column that ends with a ")" replace anything in parentheses with nothing (delete it)
        ##white space, escape special charachters for an actual (, any charachter of any number,
        ##escape special charachters for an actual ) and replace with nothing
        energy.loc[energy['Country'].str.endswith(')'), ['Country']]=energy['Country'].str.replace(" \(.*\)","")
        ##have to take the numbers off of country names otherwise merge won't work properly 'China' != 'China2'
        ##replace any number of digits with nothing
        energy['Country'] = energy['Country'].str.replace('\d+', '')
        return energy
    energy=energy()
    ##SECOND DATA FRAME
    def gdp():
        ##load file and skip header. 'world_bank.csv' is not name of file as saved on local. It's file name that works in Jupyter
        GDP=pd.read_csv('world_bank.csv', skiprows=4)
        ##replace specific values in Country Name column
        GDP['Country Name']=GDP['Country Name'].replace(['Korea, Rep.', 'Iran, Islamic Rep.', 'Hong Kong SAR, China'], value=['South Korea', 'Iran', 'Hong Kong'])
        ##take only last 10 years of GDP data, along with 'Country Name'
        GDP.rename(columns={'Country Name':'Country'}, inplace=True)
        GDP=GDP[['Country', '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015']]
        return GDP
    GDP=gdp()
        
    ##THIRD DATA FRAME
    def scimen():
        ScimEn=pd.read_excel('scimagojr-3.xlsx')
        return ScimEn
    ScimEn=scimen()
    
    ##JOIN THE DATA SETS
    
    ##merge in proper order. 
    merged=pd.merge(GDP, energy, how='inner', on='Country')
    merged=pd.merge(merged, ScimEn, on='Country')
    ##take top 15 by rank
    top15=merged[merged['Rank']<=15]
    ##set 'Country' as index
    top15=top15.set_index('Country')
    #rearrange column names
    top15=top15[['Rank', 'Documents', 'Citable documents', 'Citations', 'Self-citations', 'Citations per document', 'H index', 'Energy Supply', 'Energy Supply per Capita', '% Renewable', '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015']]
    return top15
answer_one()


# ### Question 2 - MERGING DATA FRAMES, OUTER-INNER JOIN COMPARISON
# The previous question joined three datasets then reduced this to just the top 15 entries. When you joined the datasets, but before you reduced this to the top 15 items, how many entries did you lose?
# 

def answer_two():
    merged=pd.merge(energy, GDP, how='inner', left_on='Country', right_on='Country Name')
    merged=pd.merge(ScimEn, merged, on='Country')
    outer=pd.merge(energy, GDP, how='outer', left_on='Country', right_on='Country Name')
    outer=pd.merge(ScimEn, merged, how='outer', on='Country')
    return len(outer)-len(merged)




# ### Question 3 - SUBSETTING, CALCULATION AND SORTING
# What are the top 15 countries for average GDP over the last 10 years?


def answer_three():
    top15=answer_one()
    #average 2006 through 2015 across for each row
    top15['avg']=top15.iloc[:, 10:21].mean(axis=1)
    sorted_GDP=top15.sort_values(by='avg', ascending=False)
    avgGDP=sorted_GDP['avg']
    return avgGDP
answer_three()


# ### Question 4 - SUBSETTING, CALCULATION AND SORTING
# By how much had the GDP changed over the 10 year span for the country with the 6th largest average GDP?


def answer_four():
    top15=answer_one()
    #average 2006 through 2015 across for each row
    top15['avg']=top15.iloc[:, 11:21].mean(axis=1)
    sorted_GDP=top15.sort_values(by='avg', ascending=False)
    return sorted_GDP.iloc[5]['2015']-sorted_GDP.iloc[5]['2006']


# ### Question 5 -CALCULATION
# What is the mean energy supply per capita?

def answer_five():
    top15=answer_one()
    return top15['Energy Supply per Capita'].mean()


# ### Question 6 - INDEX QUERY AND MAXIMUM VALUE
# What country has the maximum % Renewable and what is the percentage?

def answer_six():
    top15=answer_one()
    #get the index value and actual value of row containing max value for '% Renewable'
    return top15['% Renewable'].idxmax(), top15['% Renewable'].max()


# ### Question 7 - COLUMN CREATION, INDEX QUERY AND MAXIMUM VALUE
# Create a new column that is the ratio of Self-Citations to Total Citations. 
# What is the maximum value for this new column, and what country has the highest ratio?


def answer_seven():
    top15=answer_one()
    top15['% citations self']=top15['Self-citations']/top15['Citations']
    #get the index value and actual value of row containing max value for '% citations self'
    return top15['% citations self'].idxmax(), top15['% citations self'].max()


# ### Question 8 - COLUMN CREATION, SORTING AND INDEX QUERY
# 
# Create a column that estimates the population using Energy Supply and Energy Supply per capita. 
# What is the third most populous country according to this estimate?


def answer_eight():
    top15=answer_one()
    top15['Pop. Est.']=top15['Energy Supply']/top15['Energy Supply per Capita']
    sort_pop=top15.sort_values(by='Pop. Est.', ascending=False)
    return sort_pop.iloc[2].name
answer_eight()


# ### Question 9 - COLUMN CREATION, CORRELATION AND PLOTTING
# Create a column that estimates the number of citable documents per person. 
# What is the correlation between the number of citable documents per capita and the energy supply per capita? Use the `.corr()` method, (Pearson's correlation).

def answer_nine():
    top15=answer_one()
    top15['Pop. Est.']=top15['Energy Supply']/top15['Energy Supply per Capita']
    top15['Citable documents per person']=top15['Citable documents']/top15['Pop. Est.']
    return top15['Citable documents per person'].corr(top15['Energy Supply per Capita'])
answer_nine()


def plot9():
    import matplotlib as plt
    get_ipython().magic('matplotlib inline')
    
    
    Top15['PopEst'] = Top15['Energy Supply'] / Top15['Energy Supply per Capita']
    Top15['Citable docs per Capita'] = Top15['Citable documents'] / Top15['PopEst']
    Top15.plot(x='Citable docs per Capita', y='Energy Supply per Capita', kind='scatter', xlim=[0, 0.0006])



# ### Question 10 - COLUMN CREATION ON CONDITION
# Create a new column with a 1 if the country's % Renewable value is at or above the median for all countries in the top 15, and a 0 if the country's % Renewable value is below the median.


def answer_ten():
    top15=answer_one()
    top15.loc[top15['% Renewable'] >= top15['% Renewable'].median(), 'HighRenew'] = 1
    top15.loc[top15['% Renewable'] < top15['% Renewable'].median(), 'HighRenew'] = 0
    HighRenew=top15['HighRenew']
    return HighRenew


# ### Question 11 - GROUPBY FROM DICTIONARY VALUES
# Use the following dictionary to group the Countries by Continent, then create a dateframe that displays the sample size (the number of countries in each continent bin), and the sum, mean, and std deviation for the estimated population of each country.
# 
# ```python
# ContinentDict  = {'China':'Asia', 
#                   'United States':'North America', 
#                   'Japan':'Asia', 
#                   'United Kingdom':'Europe', 
#                   'Russian Federation':'Europe', 
#                   'Canada':'North America', 
#                   'Germany':'Europe', 
#                   'India':'Asia',
#                   'France':'Europe', 
#                   'South Korea':'Asia', 
#                   'Italy':'Europe', 
#                   'Spain':'Europe', 
#                   'Iran':'Asia',
#                   'Australia':'Australia', 
#                   'Brazil':'South America'}
# ```


def answer_eleven():
    top15=answer_one()
    top15['Pop. Est.']=top15['Energy Supply']/top15['Energy Supply per Capita']
    ContinentDict  = {'China':'Asia', 'United States':'North America', 'Japan':'Asia', 'United Kingdom':'Europe', 'Russian Federation':'Europe', 'Canada':'North America', 
                      'Germany':'Europe', 'India':'Asia', 'France':'Europe', 'South Korea':'Asia', 'Italy':'Europe', 'Spain':'Europe', 
                      'Iran':'Asia', 'Australia':'Australia', 'Brazil':'South America'}
    #create a dataframe of the 'Pop. Est.', groupby keys in dictionary, count how many in each group
    continents=pd.DataFrame(top15['Pop. Est.'].groupby(by=ContinentDict).count())
    #rename column to 'size'
    continents.rename(columns={'Pop. Est.':'size'}, inplace=True)
    #rename index
    continents.index.name='Continent'
    #get sum by group, etc.
    continents['sum']=top15['Pop. Est.'].groupby(by=ContinentDict).sum()
    continents['mean']=top15['Pop. Est.'].groupby(by=ContinentDict).mean()
    continents['std']=top15['Pop. Est.'].groupby(by=ContinentDict).std()
    return continents


# ### Question 12 - MAPPING FROM DICTIONARY, BINS AND GROUPBY
# Cut % Renewable into 5 bins. Group Top15 by the Continent, as well as these new % Renewable bins. How many countries are in each of these groups?


def answer_twelve():
    top15=answer_one()
    ContinentDict  = {'China':'Asia', 'United States':'North America', 'Japan':'Asia', 'United Kingdom':'Europe', 'Russian Federation':'Europe', 'Canada':'North America', 
                      'Germany':'Europe', 'India':'Asia', 'France':'Europe', 'South Korea':'Asia', 'Italy':'Europe', 'Spain':'Europe', 
                      'Iran':'Asia', 'Australia':'Australia', 'Brazil':'South America'}
    #create empty data frame
    continents=pd.DataFrame()
    #create column in empty data frame. Map ContinentDict from index values of top15. Need to_series() because mapping from index not column
    continents['Continent']=top15.index.to_series().map(ContinentDict)
    #create another column that takes % Renewables from top15, cuts into bin and assigns to corresponding index value (Country Name)
    continents['% Renewable Bin']=pd.cut(top15['% Renewable'], 5)
    #groupby the two columns. Size returns number of countries/elements per Continent, bin combo. count() doesn't return what you want
    return continents.groupby(['Continent', '% Renewable Bin']).size()
answer_twelve()


# ### Question 13  - FORMAT STRING TO USE COMMA SEPARATOR
# Convert the Population Estimate series to a string with thousands separator (using commas)


def answer_thirteen():
    top15=answer_one()
    top15['Pop. Est.']=top15['Energy Supply']/top15['Energy Supply per Capita']
    #format to a string with thousands separator using comma
    PopEst=top15.apply(lambda x: "{:,}".format(x['Pop. Est.']), axis=1)
    return PopEst
answer_thirteen()

