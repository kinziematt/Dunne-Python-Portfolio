

# # Assignment 2 - Pandas Introduction
# THIS IS A FILE SUBMITTED THROUGH JUPYTER NOTEBOOK DOWNLOADED AND DOWNLOADED BY ME FROM THERE.
# IT IS FROM THE FIRST COURSE IN COURSERA'S APPLIED DATA SCIENCE IN PYTHON SPECIALIZATION. IT IS INTENDED AS AND
# INTRODUCTION TO DATA PROCESSING IN PANDAS AND USES TWO SEPARATE DATA SETS. 
# THE CODE TO READ THE DATA, AND REFORMAT COLUMNS WAS NOT WRITTEN BY ME. HOWEVER, ALL SUBSEQUENT CODE WAS.


# ## Part 1
# The following code loads the olympics dataset (olympics.csv), which was derrived from the Wikipedia entry on [All Time Olympic Games Medals](https://en.wikipedia.org/wiki/All-time_Olympic_Games_medal_table), and does some basic data cleaning. 
# 
# The columns are organized as # of Summer games, Summer medals, # of Winter games, Winter medals, total # number of games, total # of medals. Use this dataset to answer the questions below.

# In[28]:

import pandas as pd

df = pd.read_csv('olympics.csv', index_col=0, skiprows=1)

for col in df.columns:
    if col[:2]=='01':
        df.rename(columns={col:'Gold'+col[4:]}, inplace=True)
    if col[:2]=='02':
        df.rename(columns={col:'Silver'+col[4:]}, inplace=True)
    if col[:2]=='03':
        df.rename(columns={col:'Bronze'+col[4:]}, inplace=True)
    if col[:1]=='№':
        df.rename(columns={col:'#'+col[1:]}, inplace=True)

names_ids = df.index.str.split('\s\(') # split the index by '('

df.index = names_ids.str[0] # the [0] element is the country name (new index) 
df['ID'] = names_ids.str[1].str[:3] # the [1] element is the abbreviation or ID (take first 3 characters from that)

df = df.drop('Totals')
df.head()


# ### Question 0 (Example)
# 
# What is the first country in df?
# 


def answer_zero():
   return df.iloc[0]
answer_zero() 


# ### Question 1 - DATA FRAME SUBSETTING AND CALCULATION
# Which country has won the most gold medals in summer games?



def answer_one():
    ##dropna() b/c otherwise you get the whole data frame with all rows with NaN values 
    ##except the one you want (USA)
    df1=df.where(df['Gold']==df['Gold'].max()).dropna()
    return df1.index[0]
    ## also works df1.iloc[0].name
answer_one()



# ### Question 2 - DATA FRAME COLUMN CREATION, SUBSETTING AND CALCULATION
# Which country had the biggest difference between their summer and winter gold medal counts?

def answer_two():
    df['diff'] = df['Gold']-df['Gold.1']
    df1=df.where(df['diff']==df['diff'].max()).dropna()
    return df1.index[0]
answer_two()


# ### Question 3 - DATA FRAME COLUMN CREATION, SUBSETTING, CALCULATION AND QUERYING INDEX
# Which country has the biggest difference between their summer gold medal counts and winter gold medal counts relative to their total gold medal count? 


def answer_three():
    df1=df[(df['Gold']>0) & (df['Gold.1']>0)]
    df1['diffper']=((df['Gold'])-(df['Gold.1']))/(df['Gold.2'])
    df2=df1.where(df1['diffper']==df1['diffper'].max()).dropna()
    return df2.index[0]
     
answer_three()


# ### Question 4 - DATA FRAME COLUMN CREATION AND BROADCASTING
# Write a function to update the dataframe to include a new column called "Points" which is a weighted value where each gold medal counts for 3 points, silver medals for 2 points, and bronze mdeals for 1 point. The function should return only the column (a Series object) which you created.

def answer_four():
    df['Points']=(df['Gold.2']*3)+(df['Silver.2']*2)+(df['Bronze.2']*1)
    return df['Points']
answer_four()



# ## Part 2
# For the next set of questions, we will be using census data from the [United States Census Bureau](http://www.census.gov/popest/data/counties/totals/2015/CO-EST2015-alldata.html). Counties are political and geographic subdivisions of states in the United States. This dataset contains population data for counties and states in the US from 2010 to 2015. [See this document](http://www.census.gov/popest/data/counties/totals/2015/files/CO-EST2015-alldata.pdf) for a description of the variable names.
# 
# The census dataset (census.csv) should be loaded as census_df. Answer questions using this as appropriate.


# ### Question 5 - DATA FRAME SUBSETTING, COUNTING AND INDEX QUERY
# Which state has the most counties in it? (hint: consider the sumlevel key carefully! You'll need this for future questions too...)


census_df = pd.read_csv('census.csv')
census_df.head()


def answer_five():
    ##limit data frame to county level data
    clevel = census_df.where(census_df['SUMLEV']==50)
    ##count up all the records by the value in 'STNAME' column. Get the index (State name here) of the maximum count
    return clevel['STNAME'].value_counts().idxmax()
answer_five()


# ### Question 6 - DATA FRAME SUBSETTING, SORT, GROUPBY AND LOOP THROUGH LIST
# Only looking at the three most populous counties for each state, what are the three most populous states (in order of highest population to lowest population)?


def answer_six():

    ##limit data frame to county level data
    clevel = census_df.where(census_df['SUMLEV'] == 50)
    ##sort by state name and then population, descending
    a = clevel.sort(['STNAME', 'CENSUS2010POP'], ascending = False)
    ##group by state name, get top three counties in each state
    a=a.groupby('STNAME').head(3)
    ##group by state name, sum the populations (there are only 3 records per state)
    a=a.groupby('STNAME')['CENSUS2010POP'].sum()
    ##sort by index (0=index instead of 1=columns), descending
    a=a.sort_values(0, False)
    ##get top three
    s=a.index[0:3]
    ##adds these to a list of string values, also works list(a.head(3).index.values)
    list=[]
    for i in s:
        list.append(i)
    return list 
  

answer_six()



# ### Question 7 - DATA FRAME SUBSETTING, CALCULATION ACROSS COLUMNS, SORTING AND INDEX QUERY
# Which county has had the largest absolute change in population within the period 2010-2015? (Hint: population values are stored in columns POPESTIMATE2010 through POPESTIMATE2015, you need to consider all six columns.)
# 
# e.g. If County Population in the 5 year period is 100, 120, 80, 105, 100, 130, then its largest change in the period would be |130-80| = 50.

def answer_seven():
    clevel = census_df.where(census_df['SUMLEV']==50).dropna()
    ##find the largest value for each record in this list of columns, axis=1 for columns instead of index, create a new column in data frame
    clevel['max']=clevel[['POPESTIMATE2010', 'POPESTIMATE2011', 'POPESTIMATE2012', 'POPESTIMATE2013', 'POPESTIMATE2014', 'POPESTIMATE2015']].max(axis=1)
    ##find the smallest value for each record in this list of columns, axis=1 for columns instead of index, create a new column in data frame
    clevel['min']=clevel[['POPESTIMATE2010', 'POPESTIMATE2011', 'POPESTIMATE2012', 'POPESTIMATE2013', 'POPESTIMATE2014', 'POPESTIMATE2015']].min(axis=1)
    ##create a new column of the difference between max and min for each record
    clevel['change']=(clevel['max']-clevel['min'])
    ##sort data frame by change
    clevel=clevel.sort(['change'], ascending=False)
    ##extract value from 'CTYNAME' column from first row
    a=clevel.iloc[0]['CTYNAME']
    return a
answer_seven()



# ### Question 8 - SUBSETTING BASED ON CONDITION
# In this datafile, the United States is broken up into four regions using the "REGION" column. 
# 
# Create a query that finds the counties that belong to regions 1 or 2, whose name starts with 'Washington', and whose POPESTIMATE2015 was greater than their POPESTIMATE 2014.

def answer_eight():
    ##only county level
    clevel = census_df[(census_df['SUMLEV']==50)].dropna()
    ##only region 1 or 2
    clevel = clevel[(clevel['REGION']==1) | (clevel['REGION']==2)]
    ##only where 2015 pop. > 2014 pop.
    clevel = clevel[(clevel['POPESTIMATE2015'])>(clevel['POPESTIMATE2014'])]
    ##only where county name starts with Washington
    clevel = clevel[(clevel['CTYNAME'].str.startswith("Washington"))]
    ##return just state name and county name columns as a new data frame
    return clevel[['STNAME', 'CTYNAME']]
answer_eight()





