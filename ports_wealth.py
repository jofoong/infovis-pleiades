# Scatterplot showing number of ports in a country and its wealth
import IOReader as io
import altair as alt
import numpy as np
import pandas as pd
import re
from country_bbox import longRange, latRange
from vega_datasets import data

#Data filtered and retrieved from https://wid.world/data/
income = io.open_file("income.csv")
names_data = io.open_file("pleiades-locations-latest.csv")

# Filtering out the columns we want
names_data = names_data[
    (names_data['featureType'].astype(str).str.contains(
        'port', 
        flags=re.IGNORECASE, 
        regex=True))
].filter(items=[
    'featureType', 'reprLat', 'reprLong', 'timePeriods'])
names_data = names_data.dropna()

#add bbox value to gdp dataset
def add_bbox():
    for i in range(len(income['country'])):
        ccode = income.at[i, 'ccode']
        maxLong, minLong = longRange(ccode)
        maxLat, minLat = latRange(ccode)
        income.at[i, 'minLong'] = minLong
        income.at[i, 'maxLong'] = maxLong
        income.at[i, 'minLat'] = minLat
        income.at[i, 'maxLat'] = maxLat

#find if a port's coordinates fall within a bbox
def add_port_value():
    #loop through all rows in names_data
    for i in range(names_data['reprLat'].size):
        lat = names_data.iloc[i]['reprLat']
        long = names_data.iloc[i]['reprLong']

        for j in range(len(income['country'])):
            minLong = income.at[j, 'minLong']
            maxLong = income.at[j, 'maxLong']
            minLat = income.at[j, 'minLat']
            maxLat = income.at[j, 'maxLat']
            
            #if the coordinates fall in range, set value in 'port' to yes.
            if minLat < lat and lat < maxLat and minLong < long and  long < maxLong:
                income.loc[j, 'port'] = 'yes'

def construct_graph():

    chart = alt.Chart(income).mark_trail().encode(
        x='year:Q',
        y=alt.Y('income:Q', scale=alt.Scale(type='log'), title="Average income per adult"),
        color='country:N',
        tooltip='country:N',
        size='port:N'
    ).interactive(
    ).properties(width=800, height=600)

    chart.show()

add_bbox()
add_port_value()
construct_graph()