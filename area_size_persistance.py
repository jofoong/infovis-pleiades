# Show size area vs persistance over time periods
import IOReader as io
import altair as alt
import numpy as np
import pandas as pd
import re
from country_bbox import get_key, longRange, latRange
from itertools import groupby

def get_names_data():
    names_data = io.open_file("pleiades-names-latest.csv")
    # Filtering out the columns we want
    names_data = names_data.filter(items=[
        'bbox', 'id', 'maxDate', 'minDate', 'title', 'timePeriodsRange'])
    #Retain any data with occuring bbox value
    # Reference: https://stackoverflow.com/a/25266510
    unq, unq_id, unq_cnt = np.unique(names_data['bbox'].astype(str), return_inverse=True, return_counts=True)
    cnt_mask = unq_cnt > 2
    dup_bbox = unq[cnt_mask]
    # Reference: Adapted from https://stackoverflow.com/a/17071908
    names_data = names_data.loc[names_data['bbox'].isin(dup_bbox)]
    names_data.sort_values('timePeriodsRange')
    
    names_data.to_csv('persist.csv')
    return names_data

def calc_bbox_area(names_data):
   #loop through all rows in names_data
    for i in range(len(names_data['bbox'])):
        bbox_str = names_data.iloc[i]['bbox']
        bbox_arr = bbox_str.split(",")

        swLat = float(bbox_arr[0])
        swLong = float(bbox_arr[1])
        neLat = float(bbox_arr[2])
        neLong = float(bbox_arr[3])

        area = (swLong - neLong) * (swLat - neLat)
        names_data.loc[i, 'area'] = area

def filter_data(names_data):
    calc_bbox_area(names_data)
    names_data = names_data[
        (names_data['area'] > 10.0)
    ]
    return names_data

def draw(source):
    palette = alt.Scale(
        #Qualitative colour scheme selected from https://colorbrewer2.org/#type=qualitative&scheme=Set1&n=9
        range=['#276419', '#f7f7f7', '#8e0152'],
        type='linear'
    )

    chart = alt.Chart(source).mark_circle(
        stroke='black',
        strokeWidth=0.5
    ).encode(
        x=alt.X('minDate:O'),
        y=alt.Y('area'),
        color=alt.Color('bbox', scale=palette, legend=None),
        size=alt.Size('area:Q',
            scale=alt.Scale(range=[100,1000]),
            legend=alt.Legend(title='Bbox area')),
        tooltip='title:N' 
    ).interactive(
    ).properties(width=700, height=600)

    chart.show()

#names_data = get_names_data()
names_data = io.open_file('persist.csv')
names_data = filter_data(names_data)
print(names_data.shape)

print(len(names_data['bbox'].unique()))
draw(names_data)