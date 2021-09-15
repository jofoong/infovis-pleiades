import IOReader as io
import altair as alt
import numpy as np
import pandas as pd
import re
from vega_datasets import data

names_data = io.open_file("pleiades-places-latest.csv")

# Filtering out the columns we want
names_data = names_data[
    (names_data['featureTypes'].astype(str).str.contains(
        'church|altar|temple|mosque|abbey|sanctuary|shrine|synagogue', 
        flags=re.IGNORECASE, 
        regex=True))
    & (names_data['maxDate'].astype(str).str.len() > 0)
    & (names_data['minDate'].astype(str).str.len() > 0)
    & (names_data['reprLat'].astype(str).str.len() > -10)
    & (names_data['reprLong'].astype(str).str.len() > -10)
].filter(items=[
    'featureTypes', 'description', 'maxDate', 'minDate', 'reprLat', 'reprLong', 'title'])
names_data = names_data.dropna()

def construct_graph():
    countries = alt.topo_feature(data.world_110m.url, 'countries')

    slider = alt.binding_range(
        min=-4999,
        max=names_data['minDate'].max().astype(float),
        step=1
    )
    slider_selection = alt.selection_single(
        name="year_by",
        fields=['minDate'],
        on='none',
        bind=slider,
        init={'minDate': -5000}
    )

    coordinates = alt.Chart(names_data).mark_point().encode(
        longitude='reprLong:Q',
        latitude='reprLat:Q',
        size=alt.value(10),
        color='featureTypes:N',
        tooltip='title:N'  
    ).add_selection(slider_selection
    # Reference: Adapted from https://github.com/altair-viz/altair/issues/1013#issuecomment-508251308
    ).transform_filter(
        (alt.datum.minDate <= slider_selection.minDate)# & (alt.datum.minDate <= slider_selection.maxDate)
    )

    chart = alt.Chart(countries).mark_geoshape(
        fill='green',
        stroke='white',
        opacity=0.15)
    
    view = alt.layer(chart, coordinates).project(
        type='mercator', scale=1000, center=[20, 40]
    ).properties(
        width=800, height=600
    ).configure(background='#0F6F7C'
    ).configure_view(stroke=None)

    view.show()

construct_graph()