
import dash
from dash import dcc
from dash import html

import requests
import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc



from datetime import datetime, timezone
from datetime import timedelta
from collections import deque
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate 


from dash import dash_table as dt
import plotly.graph_objects as go

from plotly.subplots import make_subplots 
import json  
import warnings 

import xarray as xr


#matplotlib inline
warnings.simplefilter("ignore")





#TODO: filter NANs, so that the website still shows something!
# Add the Oceanographic data

#global constants
lookbacktime=50 
    
#functions
token="pk.eyJ1IjoiczIxMzUzNSIsImEiOiJja3Y5ZjU2azI1dXByMnVzN2xkNzM1MXdsIn0.UX-Yc5568zDhcQ9uZ3ytJw"

#Copernicus Data
def access_oceanographic_prediction(indicator,current_time=datetime.utcnow(), lonmin=-30, lonmax=30, latmin=0, latmax=80):
    
    #convert times to strings
    datestr_now = (current_time).date().strftime("%Y-%m-%d")
    hour=slice(0, 48, 8)
    lookfut = timedelta(days=4, hours=0)
    
    datestr_fut = (current_time+lookfut).date().strftime("%Y-%m-%d")

    #set access data
    USERNAME = 'pmariani'
    PASSWORD = 'JkxJcsY6'
    
    if indicator==1:
        DATASET_ID = 'global-analysis-forecast-wav-001-027'
        
        #read data from url 
        data = xr.open_dataset("https://"+USERNAME+":"+PASSWORD+"@nrt.cmems-du.eu/thredds/dodsC/"+DATASET_ID).sel(time=slice(datestr_now+"T00:00:00.000000000", datestr_fut+"T00:00:00.000000000"),longitude=slice(lonmin,lonmax),latitude=slice(latmin,latmax))[['VHM0', 'VPED']]
    elif indicator==2:
        DATASET_ID = 'global-analysis-forecast-phy-001-024'
        
        #read data from url 
        data = xr.open_dataset("https://"+USERNAME+":"+PASSWORD+"@nrt.cmems-du.eu/thredds/dodsC/"+DATASET_ID).sel(time=slice(datestr_now+"T00:00:00.000000000", datestr_fut+"T00:00:00.000000000"),longitude=slice(lonmin,lonmax),latitude=slice(latmin,latmax))[['uo','vo']]     
        
    return data

def create_figure_VPED(data,lon,lat):

    slice_d = data.isel(time=slice(0, 32, 8))

    # Create figure
    fig = go.Figure()

    for t in range(len(slice_d.indexes['time'])): 
        vhmo_slice = slice_d["VPED"][t]
        #vhmo_data=vhmo_data.to_series()

        df_pd_vhmo_df=vhmo_slice.to_dataframe()

        lat_arr=np.array(df_pd_vhmo_df.index.get_level_values(0))
        lon_arr=np.array(df_pd_vhmo_df.index.get_level_values(1))
        pow_arr= np.array(df_pd_vhmo_df['VPED'])

        lat_arr=lat_arr[~np.isnan(pow_arr)]
        lon_arr=lon_arr[~np.isnan(pow_arr)]
        pow_arr=pow_arr[~np.isnan(pow_arr)]

        fig.add_trace(
            go.Scattermapbox(visible=False,
                             lat=lat_arr, 
                             lon=lon_arr, 
                             mode="markers",
                             marker=dict(opacity=0.3,
                                         size=11,
                                         color=pow_arr,showscale=True,
                                         colorbar=dict(title={
                                                         'text':'<b>Wavedirection in [°]</b>',
                                                         'side':'right'},
                                                       x=1,
                                                       xanchor="right"),
                                         colorscale=['lightblue','green','yellow','orange','red'],
                                         cmax=360,
                                         cmin=0,
                                        ),
                            hoverinfo='skip',
                             ))

    fig.data[0].visible = True   
    
    #add current position
    fig.add_trace(
            go.Scattermapbox(visible=True,
                             lat=[lat], 
                             lon=[lon], 
                             mode="markers",
                             marker=dict(opacity=1,
                                         size=12,
                                         color="black"
                                        ),
                             name="current position"
                             ))

    # Create and add slider
    steps = []
    times=slice_d.indexes['time'].round('H')
    for i in range(len(fig.data)-1):
        step = dict(
            method="update",
            args=[{"visible": [False] * len(fig.data)}],
            label=times[i].strftime("%m/%d/%Y"),  # layout attribute
        )
        step["args"][0]["visible"][i] = True  # Toggle i'th trace to "visible"
        step["args"][0]["visible"][-1] = True
        steps.append(step)

    sliders = [dict(
        active=10,
        currentvalue={"prefix": "Date: "},
        pad={"t": 10,"l":30,"b":20},
        steps=steps,
        len=0.5
    )]

    fig.update_layout(
        sliders=sliders,
        margin={"r":0,"t":0,"l":0,"b":0},
        mapbox= {
            'style': "mapbox://styles/s213535/cl0dt0lzo000115mrm7ev76ph",   #mapbox://styles/s213535/ckvjeiz2d8yho15o2euqwbt9z
            'center': {'lon': lon, 'lat': lat}, 
            'zoom': 4,
            #'domain':dict(x=[0.2,0.8],y=[0.3,0.5]),
            #'layers':[
            #    dict(below='traces',maxzoom=20,minzoom=3)],
            'accesstoken':token},
        showlegend=False,
        paper_bgcolor=colors['lightblue'],
        plot_bgcolor=colors['lightblue']
    )

    return fig

def create_figure_VHMO(data,lon,lat): 
    
    slice_d = data.isel(time=slice(0, 32, 8))

    # Create figure
    fig = go.Figure()

    for t in range(len(slice_d.indexes['time'])): 
        vhmo_slice = slice_d["VHM0"][t]
        #vhmo_data=vhmo_data.to_series()

        df_pd_vhmo_df=vhmo_slice.to_dataframe()

        lat_arr=np.array(df_pd_vhmo_df.index.get_level_values(0))
        lon_arr=np.array(df_pd_vhmo_df.index.get_level_values(1))
        pow_arr= np.array(df_pd_vhmo_df['VHM0'])

        lat_arr=lat_arr[~np.isnan(pow_arr)]
        lon_arr=lon_arr[~np.isnan(pow_arr)]
        pow_arr=pow_arr[~np.isnan(pow_arr)]

        fig.add_trace(
            go.Scattermapbox(visible=False,
                             lat=lat_arr, 
                             lon=lon_arr, 
                             mode="markers",
                             marker=dict(opacity=0.3,
                                         size=11,
                                         color=pow_arr,showscale=True,
                                         colorbar=dict(title={
                                                         'text':'<b>Waveheight in [m]</b>',
                                                         'side':'right'},
                                                       x=1,
                                                       xanchor="right"),
                                         colorscale=['lightblue','green','yellow','orange','red'],
                                         cmax=10,
                                         cmin=0,
                                        ),
                            hoverinfo='skip',
                             ))

    fig.data[0].visible = True   
    
    #Add dot for current position
    fig.add_trace(
            go.Scattermapbox(visible=True,
                             lat=[lat], 
                             lon=[lon], 
                             mode="markers",
                             marker=dict(opacity=1,
                                         size=12,
                                         color="black"
                                        ),
                             name="current position"
                             ))

    # Create and add slider
    steps = []
    times=slice_d.indexes['time'].round('H')
    for i in range(len(fig.data)-1):
        step = dict(
            method="update",
            args=[{"visible": [False] * len(fig.data)}],
            label=times[i].strftime("%m/%d/%Y"),  # layout attribute
        )
        step["args"][0]["visible"][i] = True  # Toggle i'th trace to "visible"
        step["args"][0]["visible"][-1] = True
        steps.append(step)

    sliders = [dict(
        active=10,
        currentvalue={"prefix": "Date: "},
        pad={"t": 10,"l":30,"b":20},
        steps=steps,
        len=0.5
    )]
    

    fig.update_layout(
        sliders=sliders,
        margin={"r":0,"t":0,"l":0,"b":0},
        mapbox= {
            'style': "mapbox://styles/s213535/cl0dt0lzo000115mrm7ev76ph",   #mapbox://styles/s213535/ckvjeiz2d8yho15o2euqwbt9z
            'center': {'lon': lon, 'lat': lat}, 
            'zoom': 4,
            'accesstoken':token},
        showlegend=False,
        paper_bgcolor=colors['lightblue'],
        plot_bgcolor=colors['lightblue']
        )

    return fig

def create_figure_north_current(data,lon,lat): 
    
    north_slice = data.isel(depth=slice(None,1))

    slice_d = north_slice.isel(time=slice(0, 4, 1))

    # Create figure
    fig = go.Figure()

    for t in range(len(slice_d.indexes['time'])): 
        north_slice = slice_d["vo"][t]
        #vhmo_data=vhmo_data.to_series()

        df_pd_north_df=north_slice.to_dataframe()

        lat_arr=np.array(df_pd_north_df.index.get_level_values(1))
        lon_arr=np.array(df_pd_north_df.index.get_level_values(2))
        pow_arr= np.array(df_pd_north_df['vo'])

        lat_arr=lat_arr[~np.isnan(pow_arr)]
        lon_arr=lon_arr[~np.isnan(pow_arr)]
        pow_arr=pow_arr[~np.isnan(pow_arr)]

        fig.add_trace(
            go.Scattermapbox(visible=False,
                             lat=lat_arr, 
                             lon=lon_arr, 
                             mode="markers",
                             marker=dict(opacity=0.4,
                                         size=11,
                                         color=pow_arr,showscale=True,
                                         colorbar=dict(title={
                                                         'text':'<b>Current velocity <br> north direction <br> [m/s]</b>',
                                                         'side':'right'},
                                                       x=1,
                                                       xanchor="right"),
                                         colorscale=['pink','purple','darkblue','lightblue','green','yellow','orange'],
                                         cmax=1.2,
                                         cmin=-1.2,
                                        ),
                            hoverinfo='skip',
                             ))

    fig.data[0].visible = True   
    
    #Add dot for current position
    fig.add_trace(
            go.Scattermapbox(visible=True,
                             lat=[lat], 
                             lon=[lon], 
                             mode="markers",
                             marker=dict(opacity=1,
                                         size=12,
                                         color="black"
                                        ),
                             name="current position"
                             ))

    # Create and add slider
    steps = []
    times=slice_d.indexes['time'].round('H')
    for i in range(len(fig.data)-1):
        step = dict(
            method="update",
            args=[{"visible": [False] * len(fig.data)}],
            label=times[i].strftime("%m/%d/%Y"),  # layout attribute
        )
        step["args"][0]["visible"][i] = True  # Toggle i'th trace to "visible"
        step["args"][0]["visible"][-1] = True
        steps.append(step)

    sliders = [dict(
        active=10,
        currentvalue={"prefix": "Date: "},
        pad={"t": 10,"l":30,"b":20},
        steps=steps,
        len=0.5
    )]
    

    fig.update_layout(
        sliders=sliders,
        margin={"r":0,"t":0,"l":0,"b":0},
        mapbox= {
            'style': "mapbox://styles/s213535/cl0dt0lzo000115mrm7ev76ph",   #mapbox://styles/s213535/ckvjeiz2d8yho15o2euqwbt9z
            'center': {'lon': lon, 'lat': lat}, 
            'zoom': 4,
            'accesstoken':token},
        showlegend=False,
        paper_bgcolor=colors['lightblue'],
        plot_bgcolor=colors['lightblue']
        )

    return fig

def create_figure_east_current(data,lon,lat): 
    
    east_slice = data.isel(depth=slice(None,1))

    slice_d = east_slice.isel(time=slice(0, 4, 1))

    # Create figure
    fig = go.Figure()

    for t in range(len(slice_d.indexes['time'])): 
        east_slice = slice_d["uo"][t]
        #vhmo_data=vhmo_data.to_series()

        df_pd_east_df=east_slice.to_dataframe()

        lat_arr=np.array(df_pd_east_df.index.get_level_values(1))
        lon_arr=np.array(df_pd_east_df.index.get_level_values(2))
        pow_arr= np.array(df_pd_east_df['uo'])

        lat_arr=lat_arr[~np.isnan(pow_arr)]
        lon_arr=lon_arr[~np.isnan(pow_arr)]
        pow_arr=pow_arr[~np.isnan(pow_arr)]

        fig.add_trace(
            go.Scattermapbox(visible=False,
                             lat=lat_arr, 
                             lon=lon_arr, 
                             mode="markers",
                             marker=dict(opacity=0.4,
                                         size=11,
                                         color=pow_arr,showscale=True,
                                         colorbar=dict(title={
                                                         'text':'<b>Current velocity <br> east direction <br> [m/s]</b>',
                                                         'side':'right'},
                                                       x=1,
                                                       xanchor="right"),
                                         colorscale=['pink','purple','darkblue','lightblue','green','yellow','orange'],
                                         cmax=1.2,
                                         cmin=-1.2,
                                        ),
                            hoverinfo='skip',
                             ))

    fig.data[0].visible = True   
    
    #Add dot for current position
    fig.add_trace(
            go.Scattermapbox(visible=True,
                             lat=[lat], 
                             lon=[lon], 
                             mode="markers",
                             marker=dict(opacity=1,
                                         size=12,
                                         color="black"
                                        ),
                             name="current position"
                             ))

    # Create and add slider
    steps = []
    times=slice_d.indexes['time'].round('H')
    for i in range(len(fig.data)-1):
        step = dict(
            method="update",
            args=[{"visible": [False] * len(fig.data)}],
            label=times[i].strftime("%m/%d/%Y"),  # layout attribute
        )
        step["args"][0]["visible"][i] = True  # Toggle i'th trace to "visible"
        step["args"][0]["visible"][-1] = True
        steps.append(step)

    sliders = [dict(
        active=10,
        currentvalue={"prefix": "Date: "},
        pad={"t": 10,"l":30,"b":20},
        steps=steps,
        len=0.5
    )]
    

    fig.update_layout(
        sliders=sliders,
        margin={"r":0,"t":0,"l":0,"b":0},
        mapbox= {
            'style': "mapbox://styles/s213535/cl0dt0lzo000115mrm7ev76ph",   #mapbox://styles/s213535/ckvjeiz2d8yho15o2euqwbt9z
            'center': {'lon': lon, 'lat': lat}, 
            'zoom': 4,
            'accesstoken':token},
        showlegend=False,
        paper_bgcolor=colors['lightblue'],
        plot_bgcolor=colors['lightblue']
        )

    return fig


#time=datetime.utcnow()
#vhmo_p,html_text,encoded=plot_oceanographic_prediction()
#unique_url = py.plot_mpl(vped_p, filename="my first plotly plot")

        
#@app.server.route('/static/<resource>')
#def serve_static(resource):
#    return flask.send_from_directory(STATIC_PATH, resource)


def datacollection():
    

    #can be left out
    history_o2 = deque(maxlen=10000)
    history_wvgl = deque(maxlen=10000)
    history_pw = deque(maxlen=10000) 
    history_power_status = deque(maxlen=10000)
    history_weather = deque(maxlen=10000)
     
    user = "aqua" 
    pw = "baeG2eezaiph"
    current_time = datetime.utcnow()
    lookback = timedelta(days=lookbacktime, hours=1)
    datestr = (current_time-lookback).strftime("%Y-%m-%dT%H:%M:%S")
    
    url_o2 = "https://api.usv.no/wg/v2/o2?timestamp=gt.{}".format(datestr) 
    url_co2 = "https://api.usv.no/wg/v2/pco2?timestamp=gt.{}".format(datestr)
    url_pw = "https://api.usv.no/wg/v2/pth?timestamp=gt.{}".format(datestr)
    url_wvgl = "https://api.usv.no/wg/v2/wg_status?timestamp=gt.{}".format(datestr)
    url_power_status="https://api.usv.no:443/wg/v2/power_status?timestamp=gt.{}".format(datestr) # total_battery_power (wh) , solar_power_generated (mW) , battery_charging_power (mW)
    url_weather="https://api.usv.no:443/wg/v2/weather?timestamp=gt.{}".format(datestr) # avg_wind_dir , max_wind_speed , pressure , temperature
    
    #for CO2 Data:
    #url = "https://api.usv.no/wg/v2/pco2?timestamp=gt.{}".format(datestr)
    #for O2 Data:
    #url = "https://api.usv.no/wg/v2/o2?timestamp=gt.{}".format(datestr)
    #for powerstatus
    #url = "https://api.usv.no/wg/v2/pth?timestamp=gt.{}".format(datestr)
    #for waveglider status
    #url = "https://api.usv.no/wg/v2/wg_status?timestamp=gt.{}".format(datestr)
    
    
    r= requests.get(url_o2, auth=(user, pw))
    [history_o2.append(i) for i in r.json()]
    df = pd.DataFrame(history_o2)

    def reducedata(url,user,pw):
    
        history = deque(maxlen=10000)
    
        r= requests.get(url, auth=(user, pw))
        [history.append(i) for i in r.json()]
        df_temp = pd.DataFrame(history)
        
        if {'vehicle_id'}.issubset(df_temp.columns):
            del df_temp['vehicle_id'] 
        if {'timestamp'}.issubset(df_temp.columns):
            del df_temp['timestamp']
        if {'longitude'}.issubset(df_temp.columns):
            del df_temp['longitude']
        if {'latitude'}.issubset(df_temp.columns):
            del df_temp['latitude']
        if {'timestamp_accurate'}.issubset(df_temp.columns):
            del df_temp['timestamp_accurate']
        if {'temperature'}.issubset(df_temp.columns):
            del df_temp['temperature'] #several temperatures --> which is "right" one?
        return df_temp
    
    #merg with co2 data into one data frame
    df_temp=reducedata(url_co2,user,pw)
    df=pd.concat([df, df_temp], axis=1)
    #merg with power data into one data frame
    #df_temp=reducedata(url_pw,user,pw)
    #df=pd.concat([df, df_temp], axis=1)
    
    
    #waveglider data has different timestamps than scientific data!
    r=requests.get(url_wvgl, auth=(user, pw))
    [history_wvgl.append(i) for i in r.json()]
    df_wvgl= pd.DataFrame(history_wvgl)
    
    #pw data has different timestamps than scientific data!
    r=requests.get(url_pw, auth=(user, pw))
    [history_pw.append(i) for i in r.json()]
    df_pw= pd.DataFrame(history_pw)
    
    #power status data has different timestamps than scientific data!
    r=requests.get(url_power_status, auth=(user, pw))
    [history_power_status.append(i) for i in r.json()]
    df_power_status= pd.DataFrame(history_power_status)
    
    #weather data has different timestamps than scientific data!
    r=requests.get(url_weather, auth=(user, pw))
    [history_weather.append(i) for i in r.json()]
    df_weather= pd.DataFrame(history_weather)
    
    #TODO: - different temperatures/ humidities.. 
    #      - different length of data (unequal number of retrieved data for different URLs)
    
    print(f"df: {df.columns}, {len(df)}")#", {df['target_waypoint']} , {df['heading_desired']}")
    print(f"df_wvgl: {df_wvgl.columns}, {len(df_wvgl)}")
    print(f"df_pw: {df_pw.columns} , {len(df_pw)}")
    print(f"df_power_status: {df_power_status.columns} , {len(df_power_status)}")
    print(f"df_weather: {df_weather.columns} , {len(df_weather)}")
    
    return df,df_wvgl,df_power_status,df_weather

def draw_plots(df):
    if {'timestamp'}.issubset(df.columns):
        df = df.set_index('timestamp')
        
        #maybe I need this - but don't think so!
        #df.plot(y=["temperature", "co2_concentration", "o2_concentration"])
        
        #temp=np.array(df.temperature)[np.newaxis].T
        #print(f"temp {temp}")
        #df.plot(x=["longitude"],y=["latitude"], kind="scatter", colorbar=True, cmap="jet", c=temp)
        #plt.show()
        temp_alert=False
        co2_alert=False
        o2_alert=False
        
        df1 = df
        fig_o2co2temp = go.Figure()
        
        if {'temperature'}.issubset(df.columns):
            fig_o2co2temp.add_trace(go.Scatter(
                x=df1.index,
                y=df1["temperature"],
                name="Temperature",
                mode="markers+lines",
                marker=dict(color="blue",size=1),
                line=dict(color="blue")
            ))
        else:
            temp_alert=True
            print("Alert: no temperature data")
            
        if {'co2_concentration'}.issubset(df.columns):
            fig_o2co2temp.add_trace(go.Scatter(
                x=df1.index,
                y=df1["co2_concentration"],
                name="O2 Concentration",
                yaxis="y2",
                mode="markers+lines",
                marker=dict(color="orange",size=1),
                line=dict(color="orange")
            ))
        else:
            co2_alert=True
            print("Alert: no co2 data")
        if {'o2_concentration'}.issubset(df.columns):
            fig_o2co2temp.add_trace(go.Scatter(
                x=df1.index,
                y=df1["o2_concentration"],
                name="O2 Concentration",
                yaxis="y3",
                mode="markers+lines",
                marker=dict(color="red",size=1),
                line=dict(color="red")
            ))
        else:
            o2_alert=True
            print("Alert: no o2 data")
        fig_o2co2temp.update_layout(
        xaxis=dict(
            domain=[0.15, 1]
        ),
        yaxis=dict(
            title="Temperature in Degree Celsius °C",
            showgrid=False,
            ticks="outside", 
            tickwidth=3, 
            tickcolor='blue', 
            ticklen=5
            #gridcolor='LightPink',
        ),
        yaxis2=dict(
            title="CO2 concentration in mg/l", ## what is the unit here?
            anchor="free",
            overlaying="y",
            side="left",
            position=0.05,
            showgrid=False,
            ticks="outside", 
            tickwidth=3, 
            tickcolor='orange', 
            ticklen=5
            #gridcolor='green'
        ),
        yaxis3=dict(
            title="Oxygen in µmol/l", ##what is the unit here?
            anchor="x",
            overlaying="y",
            side="right",
            showgrid=False,
            ticks="outside", 
            tickwidth=3, 
            tickcolor='red', 
            ticklen=5
            #gridcolor='blue'
        ))
        fig_o2co2temp.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
        ))
        fig_o2co2temp.update_layout(
            margin={'l':0,'t':10,'r':0},
        )
    
        #fig2=px.line(df1, x=df1.index, y=["temperature", "air_saturation", "o2_concentration"])
        return fig_o2co2temp,temp_alert,co2_alert,o2_alert

def draw_engplots(df):
    
    if {'timestamp'}.issubset(df.columns):
        df1 = df.set_index('timestamp')
        N = 1000
        t = np.linspace(0, 10, 100)
        y = np.sin(t)
        
        fig = go.Figure(data=go.Scatter(x=t, y=y, mode='markers'))
        '''
        
        if {'solar_power_generated'}.issubset(df1.columns) and {'battery_charging_power'}.issubset(df1.columns) and {'total_battery_power'}.issubset(df1.columns):
        
            df.plot(y=["solar_power_generated", "battery_charging_power", "total_battery_power"])
            
            fig_bat = make_subplots(rows=2, cols=1)
        
            fig_bat.append_trace(go.Scatter(
                x=df1.index,
                y=df1["solar_power_generated"],
                name="Generated solar power",
            ),row=1, col=1)
            fig_bat.append_trace(go.Scatter(
                x=df1.index,
                y=df1["battery_charging_power"],
                name="Battery charging power",
            ),row=1, col=1)
            fig_bat.append_trace(go.Scatter(
                x=df1.index,
                y=df1["total_battery_power"],
                name="Total battery power",
                yaxis="y2",
            ),row=2, col=1)
            
            fig_bat.update_yaxes(title_text="Power usage and <br> generation in mW", row=1, col=1)
            fig_bat.update_yaxes(title_text="Total battery <br> power in Wh", row=2, col=1)
            
            fig_bat.update_layout(
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
            ))
            fig_bat.update_layout(
                margin={'l':0,'t':10,'r':0}
            )
        
            #fig2=px.line(df1, x=df1.index, y=["temperature", "air_saturation", "o2_concentration"])
            return fig_bat,False
        else:
            return None, True
    else:
        return None, True
    '''
    
    return fig, False
    
def gps_track(df):
    
    
    #return plt.plot(df['longitude'], df['latitude'], color='red', marker='o', markersize=3, linewidth=2, alpha=0.4)
    #mplleaflet.display(fig=ax.figure)  # shows map inline in Jupyter but takes up full width  #px.scatter_mapbox(df,
    
    fig=go.Figure()
    fig.add_trace(go.Scattermapbox(
        name="previous track",
        mode = "markers+lines",
        lon = df['longitude'],
        lat = df['latitude'],
        marker = {'size': 10, 'color':'red'}))
    
    #arrowhead=findheading(df)
    #print(arrowhead[0])
    #print(arrowhead[1])
    '''
    fig4.add_annotation(
        x = [arrowhead[1]],
        y = [arrowhead[0]],
        xref = "x", yref = "y",
        axref = "x", ayref = "y", 
        ax = [df['longitude'].iloc[-1]],
        ay = [df['latitude'].iloc[-1]],
        text = "",
        showarrow = True 
    )
    '''
    fig.add_trace(go.Scattermapbox( 
        name="current location",
        mode="markers",
        lon=[df['longitude'].iloc[-1]],
        lat=[df['longitude'].iloc[-1]],
        marker = {'size': 60, 'color':'yellow'}))
    
    
    
    fig.update_layout(
        margin ={'l':0,'t':0,'b':10,'r':0},
        mapbox = {
            'style': "mapbox://styles/s213535/ckvjeiz2d8yho15o2euqwbt9z",  #stamen-terrain
            'center': {'lon': df.longitude.mean(), 'lat': df.latitude.mean()}, 
            'zoom': 4,
            'accesstoken':token},
        showlegend=False,
        paper_bgcolor=colors['lightblue'],
        plot_bgcolor=colors['lightblue'])
    #data=[trackdata,currentloc]
    #fig4 = dict(data=data, layout=layout)
    return fig

def gps_track_temp(df):
    
    
    #return plt.plot(df['longitude'], df['latitude'], color='red', marker='o', markersize=3, linewidth=2, alpha=0.4)
    #mplleaflet.display(fig=ax.figure)  # shows map inline in Jupyter but takes up full width  #px.scatter_mapbox(df,
    fig4 = go.Figure(go.Scattermapbox(
    mode = "markers",
    lon = df['longitude'],
    lat = df['latitude'],
    marker = {'size': 4, 'color':df['temperature'],
              'colorscale':'Jet',
              'showscale':True,
              'colorbar':{
                  'title':{
                      'text':'temperature in °C',
                      'side':'right'},
                  'x':1,
                  'xanchor':"right"}}))    
    '''
    fig.add_trace(go.Scattermapbox(
        mode = "markers+lines",
        lon = [-50, -60,40],
        lat = [30, 10, -20],
        marker = {'size': 10}))
    '''
    fig4.update_layout(
        margin ={'l':0,'t':0,'b':10,'r':0},
        mapbox = {
            'style': "mapbox://styles/s213535/ckvjeiz2d8yho15o2euqwbt9z",
            'center': {'lon': df.longitude.mean(), 'lat': df.latitude.mean()}, 
            'zoom': 4,
            'accesstoken':token},
        paper_bgcolor=colors['lightblue'],
        plot_bgcolor=colors['lightblue'])
    #fig4.update_coloraxes(colorbar_x=-2,colorbar_xanchor="right")
    return fig4

def gps_track_o2(df):
    
    
    #return plt.plot(df['longitude'], df['latitude'], color='red', marker='o', markersize=3, linewidth=2, alpha=0.4)
    #mplleaflet.display(fig=ax.figure)  # shows map inline in Jupyter but takes up full width  #px.scatter_mapbox(df,
    fig4 = go.Figure(go.Scattermapbox(
    mode = "markers",
    lon = df['longitude'],
    lat = df['latitude'],
    marker = {'size': 4, 'color':df["o2_concentration"],'colorscale':'temps','showscale':True,'colorbar':{'title':{'text':'O2 concentration in µmol/l','side':'right'},'x':1,'xanchor':"right"}}))    
    '''
    fig.add_trace(go.Scattermapbox(
        mode = "markers+lines",
        lon = [-50, -60,40],
        lat = [30, 10, -20],
        marker = {'size': 10}))
    '''
    fig4.update_layout(
        margin ={'l':0,'t':0,'b':10,'r':0},
        mapbox = {
            'style': "mapbox://styles/s213535/ckvjeiz2d8yho15o2euqwbt9z",
            'center': {'lon': df.longitude.mean(), 'lat': df.latitude.mean()}, 
            'zoom': 4,
            'accesstoken':token},
        
        paper_bgcolor=colors['lightblue'],
        plot_bgcolor=colors['lightblue'])
    return fig4

def gps_track_co2(df):
    
    
    #return plt.plot(df['longitude'], df['latitude'], color='red', marker='o', markersize=3, linewidth=2, alpha=0.4)
    #mplleaflet.display(fig=ax.figure)  # shows map inline in Jupyter but takes up full width  #px.scatter_mapbox(df,
    fig4 = go.Figure(go.Scattermapbox(
    mode = "markers",
    lon = df['longitude'],
    lat = df['latitude'],
    marker = {'size': 4, 
              'color':df["co2_concentration"],
              'colorscale':'Turbo','showscale':True,
              'colorbar':{'title':{'text':'co2 concentration in mg/l','side':'right'},
                          'x':1,'xanchor':"right"}}))    
    '''
    fig.add_trace(go.Scattermapbox(
        mode = "markers+lines",
        lon = [-50, -60,40],
        lat = [30, 10, -20],
        marker = {'size': 10}))
    '''
    fig4.update_layout(
        margin ={'l':0,'t':0,'b':5,'r':0},
        mapbox = {
            'style': "mapbox://styles/s213535/ckvjeiz2d8yho15o2euqwbt9z",
            'center': {'lon': df.longitude.mean(), 'lat': df.latitude.mean()}, 
            'zoom': 4,
            'accesstoken':token},
        
        paper_bgcolor=colors['lightblue'],
        plot_bgcolor=colors['lightblue'])
    return fig4

def alarm(df):
    alarmlist=[]
    for col in df.columns:
        if 'alarm' in str(col):
            if str(df[col].iloc[-1]) == 'True':
                alarmlist.append(col) 
    return alarmlist

def active(df):
    lastupdate=str(df['timestamp'].iloc[-1])  
    current_time = datetime.now(timezone.utc)
    lookback = timedelta(hours=1)
     
    datestr = (current_time-lookback).strftime("%Y-%m-%d %H:%M:%S%z") # "%Y-%m-%dT%H:%M:%S%z"
    print(f"lastupdate: {lastupdate} < datestring {datestr}")
    print(datetime.strptime(lastupdate, "%Y-%m-%d %H:%M:%S%z"))
    
    if datetime.strptime(lastupdate, "%Y-%m-%d %H:%M:%S%z")<datetime.strptime(datestr, "%Y-%m-%d %H:%M:%S%z"):
        return False
    else:
        return True 

def current_situation_table(df):
    if {'latitude'}.issubset(df.columns) and {'longitude'}.issubset(df.columns) and {'water_speed'}.issubset(df.columns):
        #create table with current location and speed
        columns=['Latitude', 'Longitude', 'Speed' ]
        data=[{'Latitude':round(df['latitude'].iloc[-1],2),'Longitude':round(df['longitude'].iloc[-1],2),'Speed':round(df['water_speed'].iloc[-1],2)}]
        table=[columns,data]
        return table, False
    else:
        return None, True

def current_scientificdata_table(df):
    if {'temperature'}.issubset(df.columns) and {'co2_concentration'}.issubset(df.columns) and {'o2_concentration'}.issubset(df.columns):
        #create table with current location and speed
        columns=['Temperature [°C]', 'CO2 concentration [mg/l]', 'O2 concentration [mg/l]' ]
        data=[{'Temperature [°C]':round(df['temperature'].iloc[-1],2),'CO2 concentration [mg/l]':round(df['co2_concentration'].iloc[-1],2),'O2 concentration [mg/l]':round(df['o2_concentration'].iloc[-1],2)}]
        table=[columns,data]
        return table, False 
    else: 
        return None, True

def current_engsit_table(df):
    if {'solar_power_generated'}.issubset(df.columns) and {'battery_charging_power'}.issubset(df.columns) and {'total_battery_power'}.issubset(df.columns):
        #create table with current location and speed
        columns=['Solar generated power [MW]', 'Battery charging power [MW]', 'Battery power [Wh]' ]
        if df['solar_power_generated'].iloc[-1] is None:
            solar=0
        else:
            solar=round(df['solar_power_generated'].iloc[-1],2)
        if df['battery_charging_power'].iloc[-1] is None:
            battery_charge=0
        else:
            battery_charge=round(df['battery_charging_power'].iloc[-1],2)
        if df['total_battery_power'].iloc[-1] is None: 
            battery_power=0
        else:
            battery_power=round(df['total_battery_power'].iloc[-1],2)

        data=[{'Solar generated power [MW]':solar,'Battery charging power [MW]':battery_charge,'Battery power [Wh]':battery_power}]
        table=[columns,data]
        return table
    else:
        raise PreventUpdate

def weather_table(df):
    if {'avg_wind_dir'}.issubset(df.columns):
        winddirection={'N':[348.75,11.25],
                       'NNE':[11.25,33.75],
                       'NE':[33.75,56.25],
                       'ENE':[56.25,78.75],
                       'E':[78.75,101.25],
                       'ESE':[101.25,123.75],
                       'SE':[123.75,146.25],
                       'SSE':[146.25,168.75],
                       'S':[168.75,191.25],
                       'SSW':[191.25,213.75],
                       'SW':[213.75,236.25],
                       'WSW':[236.25,258.75],
                       'W':[258.75,281.25], 
                       'WNW':[281.25,303.75],
                       'NW':[303.75,326.25],
                       'NNW':[326.25,348.75]}
        df_wind=pd.DataFrame(winddirection)
        print(df['avg_wind_dir'])
        for w in winddirection:
            if df['avg_wind_dir'].iloc[-1]>= df_wind[w][0] and df['avg_wind_dir'].iloc[-1]<= df_wind[w][1]:
                winddir=w
        
        imgname=str(winddir)+'.png'
        print(imgname)
        img=html.Img(src = app.get_asset_url(imgname),
                     height = '30 px',
                     width = 'auto')
        
        columns=['Wind direction', 'Wind speed', 'Temperature' ]
        data=[{'Wind direction':winddir,'Wind speed':round(df['avg_wind_speed'].iloc[-1],2),'Temperature':round(df['temperature'].iloc[-1],2)}]
        table=[columns,data]
        return table, img
    else:
        raise PreventUpdate


app = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])
server=app.server

#Style settings
colors = {
    'yellow': '#FFFFE0', ##111111',
    'text': '#7FDBFF',
    'darkblue': '#2f577d',
    'white': '#FFFFFF',
    'lightblue': '#d4ebf2'
}


#Defining the Layout. Split up into header, left side and right side
header= html.Div([
            dbc.Row(
                [
                    dbc.Col(
                #first column of first row - logo
                        html.Div(children=[
                            html.A(
                            
                                html.Img(
                                        src = app.get_asset_url('logo.png'),
                                        height = '70 px',
                                        width = 'auto'),
                                href="https://missionatlantic.eu/",
                                ),
                            ],
                            style = {
                                "float": "left",
                                'padding-top' : '1.1%',
                                'height' : 'auto'}
                            )),
                    dbc.Col(
                        html.Div(children=[
                            html.H1(children='WAVE GLIDER DATA VISUALIZATION',
                                    style = {'textAlign' : 'center', 'color':'white','font':'2.2em "Fira Sans", sans-serif'}
                            ),
                            html.H3(children='Keeping track of wave glider data output and location.',
                                    style = {'padding-top' : '-10%','textAlign' : 'center', 'color':'white','font':'1.2em "Fira Sans", sans-serif'}
                            )
                            ],
                            style = {
                                     'padding-top' : '1%'}
                            ))
        
                ],className="g-0"
            )],style={
                    'background-color' : colors['darkblue'],
                    }
            )

#dbc.Col(
#[
##html.H5("Weather"),
#html.Div(id='weather_tab'),
#],width={"size": 3}), #, "offset": 9,className='col-sm-3'
                                                       
  
                
second_row=dbc.Card([
                dbc.CardBody([
                html.Div([
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                        dcc.Graph(id='gps_figure',
                                                  style={'width': '100%', 'height': '64vh'})
                                ],width={"size": 12},style={
                                    'background-color':colors['lightblue'],}
                            )
                            
                        ],),
                    
                    dbc.Row(
                        [
                            #html.H4("LOCATION", className="card-title",style={'font':'1.8em "Fira Sans", sans-serif'}),
                            dbc.Col(
                                [ 
                                dbc.Alert(
                                        "No recent Weather Data is provided",
                                        id="weather_alert",
                                        dismissable=False,
                                        fade=False,
                                        is_open=False,
                                    ),
                                html.Div(id='temp'),
                                html.Div(id='wind'),
                                ],width={"size": 2}),
                            dbc.Col(
                                [ 
                                html.Div(id='winddir'),
                                html.Div(id='wind_arrow'),
                                ],width={"size": 2}),
                            dbc.Col(
                                [
                                dbc.Alert(
                                        "No data about current location is provided.",
                                        id='sit_alert',
                                        dismissable=False,
                                        fade=False,
                                        is_open=False,
                                    ),
                                html.Div(id='current_sit_tab'),
                                ],width={"size": 3}), #, "offset": 9,className='col-sm-3'
                            dbc.Col(
                                [
                                html.H5("Map shows:"),
                                html.Div([
                                    dcc.Dropdown( 
                                        id='gps_dropdown',
                                        options=[{'label': 'Path and heading of Waveglider', 'value': 'Normal Path'},
                                                 {'label': 'Temperature', 'value': 'Temperature'},
                                                 {'label': 'Oxygen concentration', 'value': 'Oxygen concentration'},
                                                 {'label': 'Carbondioxide concentration', 'value': 'Carbondioxide concentration'}],
                                        value='Normal Path',style={'background-color':colors['white']})]),
                                ],width={"size": 2}),
                            dbc.Col(
                                [
                                html.H5("Wave Forecast"),
                                dcc.Dropdown( 
                                            id='forecast_dropdown',
                                            options=[{'label': 'Waveheight Forecast', 'value': 'Waveheight Forecast'},
                                                     {'label': 'Wavedirection Forecast', 'value': 'Wavedirection Forecast'},
                                                     {'label': 'Surface Current East Direction Forecast', 'value': 'Surface Current East Direction Forecast'},
                                                     {'label': 'Surface Current North Direction Forecast', 'value': 'Surface Current North Direction Forecast'},
                                                     {'label': 'No Forecast', 'value': 'No Forecast'}],
                                            
                                            value='No Forecast',style={'background-color':colors['white']}),
                                ],width={"size": 3})
                            ],justify="around",),
                    ])
            
            ]
        )],color=colors['lightblue']
    )


third_row=html.Div(id='active_bar' 
                )

forth_row=dbc.Card([
                dbc.CardBody([
                    html.Div([
                            dbc.Row([
                                html.H4("DATA", className="card-title",style={'font':'1.8em "Fira Sans", sans-serif'}),
                                ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Alert(
                                        "No recent Power Status Data is provided",
                                        id="alert_engdata",
                                        dismissable=False,
                                        fade=False,
                                        is_open=False,
                                    ),
                                    html.H5("Power Status", style={'font':'1.4em "Fira Sans", sans-serif'}),
                                    html.Div(id='current_engsit_tab'),
                                    dcc.Graph(id="eng_figure", style={'display': 'inline-block', 'width': '100%'}),
                                    ],width=6),
                                
                                dbc.Col([
                                    html.H5("Water Observation", style={'font':'1.4em "Fira Sans", sans-serif'}),
                                    dbc.Alert(
                                        "No recent Temperature Data is provided",
                                        id="temp_alert",
                                        dismissable=False,
                                        fade=False,
                                        is_open=False,
                                    ),
                                    dbc.Alert(
                                        "No recent O2 Data is provided",
                                        id="o2_alert",
                                        dismissable=False,
                                        fade=False,
                                        is_open=False,
                                    ),
                                    dbc.Alert(
                                        "No recent CO2 Data is provided",
                                        id="co2_alert",
                                        dismissable=False,
                                        fade=False,
                                        is_open=False,
                                    ),
                                    dbc.Alert(
                                        "No recent Scientific Data is provided",
                                        id="scifi_alert",
                                        dismissable=False,
                                        fade=False,
                                        is_open=True,
                                    ),
                                    html.Div(id='current_scifisit_tab'),
                                    dcc.Graph(id="sci_figure", style={'display': 'inline-block', 'width': '100%'}),
                                    ],width=6)
                            ],className="gx-5"),
                    dcc.Interval(
                        id='interval-component',
                        interval=1*900000, # in milliseconds
                        n_intervals=0
                    ),
                    dcc.Store(id='df'),
                    ],
                )])],color=colors['white']
    )

'''
Option for Accustic mapping

                            
    dbc.Row( 
        [ 
            html.H5("Accustic Mapping (Example)", style={'font':'1.4em "Fira Sans", sans-serif'}),
            ]),
    dbc.Row(
    [
        dbc.Col([ 
            html.P(""),
            html.Img(
                src = app.get_asset_url('pic.png'),
                height = '510 px',
                width = 'auto'),
            ],width=6),
    ],className="g-0"),
    
'''

app.layout = dbc.Container(children=[ #alternative: dbc.Container(),html.Div()
    dbc.Row([header]),
    dbc.Row([second_row],className="h-75"),
    dbc.Row([third_row]),
    dbc.Row([forth_row]),
    #dbc.Row([testrow]),
    ],  
    style = {'background-color' : colors['white'],
             "height": "100vh"},
    fluid=True
)


## Callbacks

## Data collection - every nth intervall
@app.callback(Output('df','data'),
              Input('interval-component', 'n_intervals'))#eig. input:df
def get_data(interv):
    df,df_wvgl,df_power_status,df_weather=datacollection()
    datasets = {
         'df': df.to_json(orient='split', date_format='iso'),
         'df_wvgl': df_wvgl.to_json(orient='split', date_format='iso'),
         'df_power_status': df_power_status.to_json(orient='split', date_format='iso'),
         'df_weather': df_weather.to_json(orient='split', date_format='iso'),
    
    } 

    return json.dumps(datasets)
    
#TODO! Check if data has changed - then update "active" bar
# check by comparing current time+date with last time+date in df - if bigger than 1h: change to not active!  


#set colouring of GPS tracking
@app.callback(Output('gps_figure', 'figure'),
              Input('gps_dropdown', 'value'),
              Input('df','data'),
              Input('forecast_dropdown', 'value'))
def gps_colourscale(value,dataset,forecast):
    df_datasets = json.loads(dataset)
    df = pd.read_json(df_datasets['df'], orient='split')
    df_wvgl = pd.read_json(df_datasets['df_wvgl'], orient='split')
    
    if {'longitude'}.issubset(df.columns) and {'latitude'}.issubset(df.columns):
        lon=df['longitude'].iloc[-1]
        lat=df['latitude'].iloc[-1]
    else:
        lon=0
        lat=0

    if forecast == "Waveheight Forecast":
        predict_data=access_oceanographic_prediction(1,lonmin=lon-70,lonmax=lon+70,latmin=lat-10,latmax=lat+10)
        fig_fore=create_figure_VHMO(predict_data,lon,lat)
        return fig_fore
    elif forecast == "Wavedirection Forecast":
        predict_data=access_oceanographic_prediction(1,lonmin=lon-70,lonmax=lon+70,latmin=lat-10,latmax=lat+10)
        fig_fore=create_figure_VPED(predict_data,lon,lat)
        return fig_fore
    elif forecast == "Surface Current North Direction Forecast":
        predict_data=access_oceanographic_prediction(2,lonmin=lon-70,lonmax=lon+70,latmin=lat-10,latmax=lat+10)
        fig_fore=create_figure_north_current(predict_data,lon,lat)
        return fig_fore
    elif forecast == "Surface Current East Direction Forecast":
        predict_data=access_oceanographic_prediction(2,lonmin=lon-70,lonmax=lon+70,latmin=lat-10,latmax=lat+10)
        fig_fore=create_figure_east_current(predict_data,lon,lat)
        return fig_fore
        
    elif forecast == "No Forecast":
    
        if str(value) == 'Normal Path':
            gps_fig=gps_track(df) #df_wvgl, when I include a heading?
            return gps_fig
        if str(value) == 'Temperature':
            gps_fig=gps_track_temp(df)
            return gps_fig
        if str(value) == 'Oxygen concentration':
            gps_fig=gps_track_o2(df)
            return gps_fig
        if str(value) == 'Carbondioxide concentration':
            gps_fig=gps_track_co2(df)
            return gps_fig
        
        
        else:
            print("haha, I don't wanna work")
            raise PreventUpdate  
    
        
@app.callback(Output('active_bar','children'),
              Input('df','data'))#eig. input:df
def alarm_bar(dataset):
    df_datasets = json.loads(dataset)
    df_wvgl = pd.read_json(df_datasets['df_wvgl'], orient='split')
    df = pd.read_json(df_datasets['df'], orient='split')
    #TODO mabe this is not sufficient?
    if df_wvgl is not None and {'timestamp'}.issubset(df_wvgl.columns):
            alarms=alarm(df_wvgl)
            active_=active(df_wvgl) 
            print(active_) 
            if len(alarms)==0 and str(active_)=='True': ## implement: and time since last update <XX
                return dbc.Row([
                    html.H5("Glider status: Active , No Alarms")], 
                    style={'background-color': 'rgb(0, 204, 0)','text-align':'center'},align="center",justify="center")
            if len(alarms)>0 and str(active_)=='True':
                alarmstring=''
                for a in alarms:
                    alarmstring=alarmstring+' '+str(a)
                return dbc.Row([
                    html.H5(f"Glider status: Active , Alarms : {alarmstring} ")], 
                    style={'background-color': 'rgb(255, 255, 0)','text-align':'center'},align="center",justify="center")
            if len(alarms)>0 and str(active_)=='False':
                alarmstring=''
                for a in alarms:
                    alarmstring=alarmstring+' '+str(a)
                return dbc.Row([
                    html.H5(f"Glider status: Not active , Alarms : {alarmstring} ")], 
                    style={'background-color': 'rgb( 199, 0, 57)','text-align':'center'},align="center",justify="center")
            if len(alarms)==0 and str(active_)=='False':
                return dbc.Row([
                    html.H5(f"Glider status: Not active , No Alarms")], 
                    style={'background-color': 'rgb( 199, 0, 57)','text-align':'center'},align="center",justify="center")
            else:
                return dbc.Row([
                    html.H5(f"Glider status: Not active , No Alarms")], 
                    style={'background-color': 'rgb( 199, 0, 57)','text-align':'center'},align="center",justify="center")
    else:
        return dbc.Row([
                html.H5(f"Glider status: Not known , No alarm data available")], 
                style={'background-color': 'rgb( 199, 0, 100)','text-align':'center'},align="center",justify="center")
    
@app.callback(Output('sit_alert','is_open'),
              Input('df','data'))
def alert1(datasets):
    df_datasets = json.loads(datasets)
    df = pd.read_json(df_datasets['df_wvgl'], orient='split')
    
    table_data, alert= current_situation_table(df)
    return alert

@app.callback(Output('current_sit_tab','children'),
              Input('df','data'),
              Input('sit_alert','is_open'))
def current_sit_tab1(dataset,alert):
    df_datasets = json.loads(dataset)
    if alert:# or pd.read_json(df_datasets['df_wvgl'], orient='split')==None:
        raise PreventUpdate
    else:
        df_wvgl = pd.read_json(df_datasets['df_wvgl'], orient='split')
        
        table_data,alert= current_situation_table(df_wvgl)
        print(f"table_data : {table_data}")
        table=dt.DataTable(
            id='tbl', data=table_data[1],
            columns=[{"name": i, "id": i} for i in table_data[0]],
            style_cell={'textAlign': 'center','font':'1.4em "Fira Sans", sans-serif'},
            style_header={
            #'backgroundColor': 'rgb(210, 210, 210)',
            'color': 'black',
            'fontWeight': 'bold'}
        )
        return table

@app.callback(Output('scifi_alert','is_open'),
              Input('df','data'))
def alert2(datasets):
    if datasets:
        df_datasets = json.loads(datasets)
        df = pd.read_json(df_datasets['df'], orient='split')
        
        table_data, alert= current_scientificdata_table(df)
        return alert
    else:
        return True
    

@app.callback(Output('current_scifisit_tab','children'),
              Input('df','data'),
              Input('scifi_alert','is_open'))
def current_sit_tab2(dataset,alert):
    if alert:
        raise PreventUpdate
    else:
        df_datasets = json.loads(dataset)
        df = pd.read_json(df_datasets['df'], orient='split')
        
        table_data, alert= current_scientificdata_table(df)
        
        table=dt.DataTable(
            id='scifitbl', data=table_data[1],
            columns=[{"name": i, "id": i} for i in table_data[0]],
            style_cell={'textAlign': 'center','font':'1.2em "Fira Sans", sans-serif'},
            style_header={
            #'backgroundColor': 'rgb(210, 210, 210)',
            'color': 'black',
            'fontWeight': 'bold'}
        )
        return table

@app.callback(Output('current_engsit_tab','children'),
              Input('df','data'))
def current_sit_tab3(dataset):
    df_datasets = json.loads(dataset)
    df_power_status = pd.read_json(df_datasets['df_power_status'], orient='split')
    
    table_data= current_engsit_table(df_power_status)
    print(f"table_data : {table_data}")
    table=dt.DataTable(
        id='engsittbl', data=table_data[1],
        columns=[{"name": i, "id": i} for i in table_data[0]],
        style_cell={'textAlign': 'center','font':'1.2em "Fira Sans", sans-serif'},
        style_header={
        'color': 'black',
        'fontWeight': 'bold'}
    )
    return table

@app.callback(Output('temp','children'),
              Output('wind_arrow','children'),
              Output('wind','children'),
              Output('winddir','children'),
              Output('weather_alert','is_open'),
              Input('df','data'))
def weather_tab(dataset):
    df_datasets = json.loads(dataset)
    df_weather = pd.read_json(df_datasets['df_weather'], orient='split')
    
    if df_weather is not None:
        table_data,img= weather_table(df_weather)
        print(f"table_data : {table_data}")
        table=dt.DataTable(
            id='tbl_weather', data=table_data[1],
            columns=[{"name": i, "id": i} for i in table_data[0]],
            style_cell={'textAlign': 'center','font':'1.4em "Fira Sans", sans-serif'},
            style_header={
            #'backgroundColor': 'rgb(210, 210, 210)',
            'color': 'black',
            'fontWeight': 'bold'}
        )
        windtitle="Wind speed: "+str(table_data[1][0]['Wind speed'])+" m/s"
        temptitle="Temperature: " + str(table_data[1][0]['Temperature'])+" °C"
        winddir="Wind direction: " + str(table_data[1][0]['Wind direction'])
        
        
        wind=html.H5(windtitle, style={'font':'1.2em "Fira Sans", sans-serif','color':colors['darkblue']}),
        temp=html.H5(temptitle, style={'font':'1.2em "Fira Sans", sans-serif','color':colors['darkblue']}),
        windd=html.H5(winddir, style={'font':'1.2em "Fira Sans", sans-serif','color':colors['darkblue']}),
        
        
        return temp,img,wind,windd,False #table,
    #Output('weather_tab','children'),
    else:
        return None,None,None,None,True

@app.callback(Output('alert_engdata', 'is_open'),
              Input('df','data'))
def alert3(dataset):
    df_datasets = json.loads(dataset)
    df_power_status = pd.read_json(df_datasets['df_power_status'], orient='split')
    
    fig,alert=draw_engplots(df_power_status)
    return alert


@app.callback(Output('eng_figure', 'figure'),
              Input('alert_engdata', 'is_open'),
              Input('df','data'))
def eng_figure(alert,dataset):
    if alert:
        raise PreventUpdate
    else:
        df_datasets = json.loads(dataset)
        df_power_status = pd.read_json(df_datasets['df_power_status'], orient='split')
        
        fig,alert=draw_engplots(df_power_status)
        return fig

@app.callback(Output('sci_figure', 'figure'),
              Output('temp_alert', 'is_open'),
              Output('co2_alert', 'is_open'),
              Output('o2_alert', 'is_open'),
              
              Input('df','data'))
def figure(dataset):
    df_datasets = json.loads(dataset)
    df = pd.read_json(df_datasets['df'], orient='split')
    
    fig2,temp_alert,co2_alert,o2_alert=draw_plots(df)
    return fig2,temp_alert,co2_alert,o2_alert

if __name__ == '__main__':
    app.run_server(debug=True)