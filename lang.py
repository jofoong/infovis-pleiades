import IOReader as io
import altair as alt
import numpy as np
import pandas as pd
import re


names_data = pd.DataFrame()
lang_data = pd.DataFrame()

# -----------------Data processing--------------------#
def prep_data(names_data, lang_data):
    names_data = io.open_file('pleiades-places-latest.csv')
    # Filtering out the columns we want
    names_data = names_data[names_data['bbox'].notna()]
    names_data = names_data[
        (names_data['featureTypes'].astype(str).str.contains(
            'bridge|road|port|tunnel|pass|station|aqueduct|isthmus'))
        ].filter(items=[
        'featureTypes', 'minDate', 'title', 'reprLat'])

    #languages-and-dialects-geo dataset from https://www.kaggle.com/rtatman/world-language-family-map?select=languages-and-dialects-geo.csv
    lang_data = io.open_file('languages-and-dialects-geo.csv')
    lang_data = lang_data[
        (lang_data['lat'].notna())
        & (lang_data['long'].notna())
    ]
    lang_data = lang_data.filter(items=[
        'name', 'lat'
    ])
    return names_data, lang_data

#Find any lang coordinates that fall within a place's bbox
def set_count(names_data, lang_data):
    #add new columns for the number of occurences of places and languages in a latitude subsection
    placesCount = [0] * len(names_data['minDate'])
    langCount = [0] * len(names_data['minDate'])
    names_data['placesCount'] = placesCount
    names_data['langCount'] = langCount
    #first, rearrange the df by reptLat value
    names_data.sort_values(by=['reprLat'])
    lang_data.sort_values(by=['lat'])
    #then group values together by every 2 degrees latitude
    for i in range(len(names_data['minDate'])):
        curr = names_data.iloc[i]['reprLat']

        data = names_data[(names_data['reprLat'] > curr - 2)
            & (names_data['reprLat'] < curr + 2)]
        count = len(data)
        names_data.at[i, 'placesCount'] = count

        data2 = lang_data[(lang_data['lat'] >= curr)
            & (lang_data['lat'] < curr + 2)]
        count2 = len(data2)
        names_data.at[i, 'langCount'] = count2

names_data, lang_data = prep_data(names_data, lang_data)
set_count(names_data, lang_data)
names_data = names_data.dropna()
names_data = names_data[
        (names_data['placesCount'] > 0)
        & (names_data['langCount'] > 0)
]
print(names_data)
# -----------------End of data processing--------------------#

def plot(names_data):
    chart = alt.Chart(names_data).mark_rect().encode(
        alt.X('placesCount:O', bin=alt.Bin(maxbins=50), title='Number of connecting infrastructure per area'),
        alt.Y('langCount:O', bin=alt.Bin(maxbins=50), title='Number of languages per area'),
        color=alt.Color('lang_per_infrastructure:Q', scale=alt.Scale(scheme='greenblue')),
        tooltip='lang_per_infrastructure:Q'
    ).transform_calculate(
        lang_per_infrastructure='(datum.langCount / datum.placesCount) * datum.placesCount'
    ).properties(width=500, height=500)
    
    chart.show()
plot(names_data)
