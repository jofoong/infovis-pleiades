import IOReader as io
import altair as alt
import numpy as np
import pandas as pd
from vega_datasets import data

names_data = io.open_file("pleiades-names-latest.csv")

# Filtering out the columns we want
names_data = names_data[
        names_data['locationPrecision'].astype(str).str.contains('precise')].filter(items=[
        'minDate', 'maxDate', 'nameTransliterated','reprLat','reprLatLong', 'reprLong', 'timePeriods', 'timePeriodsKeys'])
names_data = names_data[
        (names_data['timePeriods'].astype(str).str.isalpha()
        & (names_data['maxDate'] < -501)
)]

def construct_graph():
    sphere = alt.sphere()
    graticule = alt.graticule()
    countries = alt.topo_feature(data.world_110m.url, 'countries')

    palette = alt.Scale(
        #Qualitative colour scheme selected from https://colorbrewer2.org/#type=qualitative&scheme=Set1&n=9
        range=['#fff7ec', '#fc8d59', '#b30000'],
        type='linear'
    )

    coordinates = alt.Chart(names_data).mark_point().encode(
        longitude='reprLong:Q',
        latitude='reprLat:Q',
        size=alt.value(10),
        color=alt.Color('minDate', scale=palette),
        tooltip=[
            alt.Tooltip('nameTransliterated:N', title='Name'),
            alt.Tooltip('timePeriodsKeys:N', title='Time period'),
            alt.Tooltip('minDate:N', title='Min'),
            alt.Tooltip('maxDate:N', title='Max')] 
    )

    chart = alt.layer(
        #Complimentary scheme selected from https://paletton.com/#uid=52P0u0kNyb6ugjJD5fyVk6w+625
        alt.Chart(sphere).mark_geoshape(fill='#055E5E'),
        alt.Chart(countries).mark_geoshape(fill='#004700'),
    ).project(
        type='mercator', scale=1100, center=[39.59, 32.20]
    ).properties(width=700, height=600).configure_view(stroke=None)
    
    (chart + coordinates).show()
    
construct_graph()