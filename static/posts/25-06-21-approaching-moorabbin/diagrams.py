import plotly.express as px
import plotly.graph_objects as go

import pandas as pd
from pprint import pprint

## Lines

lines = [
    ['Runway35L', '', 'Grey'          , -37.971995610881926, 145.09678104395854],
    ['Runway35L', '', 'Grey'          , -37.971983636419985, 145.09699117243792],
    ['Runway35L', '', 'Grey'          , -37.98312642540333, 145.09795834415394],
    ['Runway35L', '', 'Grey'          , -37.98313731791472, 145.09775381381513],
    ['Runway35L', '', 'Grey'          , -37.971995610881926, 145.09678104395854],

    ['Runway 35L Circuit', '', 'Grey' , -37.9837081, 145.1003462],
    ['Runway 35L Circuit', '', 'Grey' , -37.9563125, 145.0977230],
    ['Runway 35L Circuit', '', 'Grey' , -37.9557034, 145.1177216],
    ['Runway 35L Circuit', '', 'Grey' , -37.9999504, 145.1210690],
    ['Runway 35L Circuit', '', 'Grey' , -38.0010325,	145.1021004],
    ['Runway 35L Circuit', '', 'Grey' , -37.9837081, 145.1003462],
    
    ['Runway35R', '', 'Grey'          , -37.971759669770805, 145.09915291318435],
    ['Runway35R', '', 'Grey'          , -37.97173773322626, 145.09943118476878],
    ['Runway35R', '', 'Grey'          , -37.98370314471934, 145.10050253036877],
    ['Runway35R', '', 'Grey'          , -37.98372684000924, 145.10018262186404],
    ['Runway35R', '', 'Grey'          , -37.971759669770805, 145.0991250860259],

    ['Runway 35R Circuit', '', 'Grey' , -37.9831326,	145.0978571],
    ['Runway 35R Circuit', '', 'Grey' , -37.9564478,	145.0956631],
    ['Runway 35R Circuit', '', 'Grey' , -37.9573953,	145.0761795],
    ['Runway 35R Circuit', '', 'Grey' , -38.0023176,	145.0802994],
    ['Runway 35R Circuit', '', 'Grey' , -38.0011678,	145.0997400],
    ['Runway 35R Circuit', '', 'Grey' , -37.9831378,	145.0978585],

    ['Runway31R', '', 'Grey'          , -37.982145887197596, 145.10444007328826],
    ['Runway31R', '', 'Grey'          , -37.974633300429375, 145.09714935777657],
    ['Runway31R', '', 'Grey'          , -37.974457814759376, 145.09727457998957],
    ['Runway31R', '', 'Grey'          , -37.98200331971691, 145.10466269055578],
    ['Runway31R', '', 'Grey'          , -37.982145887197596, 145.10444007328826],

    ['Runway 31R Circuit', '', 'Grey' , -37.9820290,	145.1045533],
    ['Runway 31R Circuit', '', 'Grey' , -37.9581397,	145.0809431],
    ['Runway 31R Circuit', '', 'Grey' , -37.9678841,	145.0629616],
    ['Runway 31R Circuit', '', 'Grey' , -38.0073899,	145.1013279],
    ['Runway 31R Circuit', '', 'Grey' , -37.9973802,	145.1194382],
    ['Runway 31R Circuit', '', 'Grey' , -37.9820353,	145.1045600],


    ['Runway31L', '', 'Grey'          , -37.98036925727342, 145.10583143121033],
    ['Runway31L', '', 'Grey'          , -37.97226420848601, 145.09774764168307],
    ['Runway31L', '', 'Grey'          , -37.97206678070608, 145.09799808610904],
    ['Runway31L', '', 'Grey'          , -37.98022668634116, 145.10602622131944],
    ['Runway31L', '', 'Grey'          , -37.98036925727342, 145.10583143121033],

    ['Runway 31L Circuit', '', 'Grey' , -37.9802806,	145.1059279],
    ['Runway 31L Circuit', '', 'Grey' , -37.9574291,	145.0831747],
    ['Runway 31L Circuit', '', 'Grey' , -37.9477171,	145.1019287],
    ['Runway 31L Circuit', '', 'Grey' , -37.9848661,	145.1398659],
    ['Runway 31L Circuit', '', 'Grey' , -37.9961627,	145.1214123],
    ['Runway 31L Circuit', '', 'Grey' , -37.9802869,	145.1059366],
]
df = pd.DataFrame(lines, columns=['color', 'text', 'actual_color', 'lat', 'lon'])

## Places

places = [
    # ['YMMB'    , 'airport'         , -37.97788594631526, 145.10042699512127],
    ['GMH'     , 'commercial'      , -38.00770719417761, 145.2489190535805],
    ['Parkmore', 'shop'            , -37.99262154620369, 145.17309044775334],
    ['Sandown' , 'landmark'       , -37.95144269873589, 145.1668571262973],
    ['Carrum'  , 'swimming'        , -38.072642674243156, 145.12180747260584],
]

## Draw Lines

fig = px.line_map(df, 
                  lat="lat", 
                  lon="lon", 
                  text="text",
                  color="color",
                  color_discrete_map={x[0]:x[2] for x in lines}
                #   color_discrete_map={'Runway35R': 'blue'}
                  )

## Draw Places

# fig.add_trace(go.Scattermap(
#     mode = "markers+text",
#     lat = [x[2] for x in places], 
#     lon = [x[3] for x in places], 
#     marker = {'size': 15, 'symbol': [x[1] for x in places]},
#     text = [x[0] for x in places],
#     legend = [x[0] for x in places],
#     textposition = "bottom center",
#     textfont = {'size': 10, 'color': "red"},
#     hoverinfo = "skip"
#     )
#     )

for place in places:
    fig.add_trace(go.Scattermap(
        mode="markers+text",
        lat=[place[2]],
        lon=[place[3]],
        marker={'size': 20, 'symbol': place[1]},
        text=[place[0]],
        name=place[0],  # This sets the legend label
        textposition="bottom center",
        textfont={'size': 20, 'color': "red"},
        hoverinfo="skip"
    ))


## Format Figure

fig.update_layout(
    margin_autoexpand=True,
    margin_b=0,
    margin_l=0,
    margin_r=0,
    margin_t=0,
    map_center = {'lat': -37.978, 'lon': 145.100},
    map_style="open-street-map",
    map_zoom=10, 
    legend_title_text="Items",
    legend_yanchor="top",
    legend_y=0.99,
    legend_xanchor="left",
    legend_x=0.01
    )

## Output

fig.show()
fig.write_html("./map.html")