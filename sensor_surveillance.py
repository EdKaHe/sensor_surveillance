# -*- coding: utf-8 -*-
"""
Created on Sun Nov 12 16:59:59 2017

@author: Ediz
"""

from bokeh.io import curdoc
from bokeh.models import PanTool, ResetTool, WheelZoomTool, SaveTool, HoverTool, ColumnDataSource
from bokeh.models.widgets import Button, Dropdown
from bokeh.models.callbacks import CustomJS
from bokeh.layouts import layout
from bokeh.plotting import figure
from time import time
from datetime import datetime
import pandas as pd

#bokeh serve --allow-websocket-origin=localhost:5000 sensor_control.py

#get start time of script
start_time = time()

#connect to server and generate csv file
filename_all_data=r'/opt/webapps/sensor_surveillance/data/sc_all_data.csv' #this file contains all data
filename_new_data=r'/opt/webapps/sensor_surveillance/data/sc_new_data.csv' #this file contains newest data for streaming it

#create figure
f_photo = figure(tools=[PanTool(), WheelZoomTool(), ResetTool(), SaveTool()],output_backend='webgl')
hover=HoverTool(tooltips=[('Date', '@date')])
f_photo.add_tools(hover)
f_photo.toolbar.logo = None

f_aux = figure(tools=[PanTool(), WheelZoomTool(), ResetTool(), SaveTool()],output_backend='webgl')
hover=HoverTool(tooltips=[('Date', '@date')])
f_aux.add_tools(hover)
f_aux.toolbar.logo = None

#initialize port and read the photocurrent
def read_csv(filename=filename_all_data):
    data_csv = pd.read_csv(filename, sep=';')
    return data_csv
   
#create periodic function
def update():
    source_df = read_csv(filename_new_data) #pandas dataframe
    if dropdown.value=='laser_current':
        source_df['selected_data']= source_df['laser_current']
    elif dropdown.value=='temperature':
        source_df['selected_data']= source_df['temperature']
#    new_data=dict(time=list(df['time'].values), photo_current=list(df['photo_current'].values), laser_current=list(df['laser_current'].values), date=list(df['date'].values))
    source.stream(ColumnDataSource.from_df(source_df))#,rollover=600) #how many glyphs/circles are kept in plot

def update_plot(attr, old, new): 
    #change yaxis label and reset data
    if dropdown.value=='laser_current':
        f_aux.yaxis.axis_label='Laser Current'
        source.data['selected_data']= source.data['laser_current'][:-1]
    elif dropdown.value=='temperature':
        f_aux.yaxis.axis_label=u'Temp. in (\u2103)'
        source.data['selected_data']= source.data['temperature'][:-1]  
    
#create columndatasource
source_df = read_csv(filename_all_data)
source_df['selected_data']=source_df['temperature'][:]
source = ColumnDataSource(source_df)
    
#create glyphs
#f_photo.circle(x='time', y='photo_current', color='firebrick', line_color=None, size=8, fill_alpha=0.4, source=source)
f_photo.circle(x='time', y='photo_current', size=10, line_color='gray', fill_color='gray', line_alpha=0.8, fill_alpha=0.3, source=source)

f_aux.circle(x='time', y='selected_data', size=10, line_color='firebrick', fill_color='firebrick', line_alpha=0.8, fill_alpha=0.3, source=source)

#Style the plot area
f_photo.plot_width = 900
f_photo.plot_height = 400
f_photo.background_fill_color=None
f_photo.border_fill_color=None

f_aux.plot_width = 900
f_aux.plot_height = 200
f_aux.background_fill_color=None
f_aux.border_fill_color=None


#Style the axes
f_photo.axis.minor_tick_line_color='black'
f_photo.axis.minor_tick_in=-6
f_photo.yaxis.axis_label='Signal Current (arb. units)'
f_photo.axis.axis_label_text_color=(0.7,0.7,0.7)
f_photo.axis.major_label_text_color=(0.7,0.7,0.7)
f_photo.axis.axis_label_text_font = 'helvetica'
f_photo.yaxis.axis_label_text_font_size = '16pt'
f_photo.axis.axis_label_text_font_style = 'normal'
f_photo.axis.major_label_text_font = 'helvetica'
f_photo.axis.major_label_text_font_size = '10pt'
f_photo.axis.major_label_text_font_style = 'normal'

f_aux.axis.minor_tick_line_color='black'
f_aux.axis.minor_tick_in=-6
f_aux.xaxis.axis_label='Time in (s)'
f_aux.yaxis.axis_label=u'Temp. in (\u2103)'
f_aux.axis.axis_label_text_color=(0.7,0.7,0.7)
f_aux.axis.major_label_text_color=(0.7,0.7,0.7)
f_aux.axis.axis_label_text_font = 'helvetica'
f_aux.axis.axis_label_text_font_size = '16pt'
f_aux.axis.axis_label_text_font_style = 'normal'
f_aux.axis.major_label_text_font = 'helvetica'
f_aux.axis.major_label_text_font_size = '10pt'
f_aux.axis.major_label_text_font_style = 'normal'

#Style the title
f_photo.title.text='Hydrogen Control'
f_photo.title.text_color=(0.7,0.7,0.7)
f_photo.title.text_font='helvetica'
f_photo.title.text_font_size='20pt'
f_photo.title.align='left'

#Style the grid
f_photo.grid.grid_line_color=(1,1,1)
f_photo.grid.grid_line_alpha=0.3
f_photo.grid.grid_line_dash=[5,3]

f_aux.grid.grid_line_color=(1,1,1)
f_aux.grid.grid_line_alpha=0.3
f_aux.grid.grid_line_dash=[5,3]

#add widgets (dropdown button) to save data as csv. CustomJS required to download data in browser
button = Button(label='Export data', button_type='danger')
js_download = """
var csv = source.get('data');
var filetext = 'time;photo_current;laser_current;temperature;date\\n';
for (i=0; i < csv['date'].length; i++) {
    var currRow = [csv['time'][i].toString(),
                   csv['photo_current'][i].toString(),
                   csv['laser_current'][i].toString(),
                   csv['date'][i].toString().concat('\\n')];

    var joined = currRow.join(';');
    filetext = filetext.concat(joined);
}

var filename = 'sensor_data.csv';
var blob = new Blob([filetext], { type: 'text/csv;charset=utf-8;' });
if (navigator.msSaveBlob) { // IE 10+
navigator.msSaveBlob(blob, filename);
} else {
var link = document.createElement("a");
if (link.download !== undefined) { // feature detection
    // Browsers that support HTML5 download attribute
    var url = URL.createObjectURL(blob);
    link.setAttribute("href", url);
    link.setAttribute("download", filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}
}"""
button.callback = CustomJS(args=dict(source=source), code=js_download)

#Create dropdown button for auxilary data
menu = [("Temperature", "temperature"), ("Laser current", "laser_current")]
dropdown = Dropdown(label="Select data", button_type="danger", menu=menu, value='temperature')
dropdown.on_change('value',update_plot)

#add figure to curdoc and configure callback
lay_out=layout([[f_photo], [f_aux], [button, dropdown]])
curdoc().add_root(lay_out)
curdoc().add_periodic_callback(update,2000) #updates each 2000ms