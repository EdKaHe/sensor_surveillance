# -*- coding: utf-8 -*-
"""
Created on Sun Nov 12 16:59:59 2017

@author: Ediz
"""

from bokeh.io import curdoc
from bokeh.models import PanTool, ResetTool, WheelZoomTool, SaveTool, HoverTool, ColumnDataSource
from bokeh.models.widgets import Button
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
f_photo.output_backend = 'svg'

f_laser = figure(tools=[PanTool(), WheelZoomTool(), ResetTool(), SaveTool()],output_backend='webgl')
hover=HoverTool(tooltips=[('Date', '@date')])
f_laser.add_tools(hover)
f_laser.toolbar.logo = None
f_laser.output_backend = 'svg'

#initialize port and read the photocurrent
def read_csv(filename=filename_all_data):
    data_csv = pd.read_csv(filename, sep=';')
    return data_csv
   
#create periodic function
def update():
    source_df = read_csv(filename_new_data) #pandas dataframe
#    new_data=dict(time=list(df['time'].values), photo_current=list(df['photo_current'].values), laser_current=list(df['laser_current'].values), date=list(df['date'].values))
    source.stream(ColumnDataSource.from_df(source_df))#,rollover=600) #how many glyphs/circles are kept in plot

#create columndatasource
source_df = read_csv(filename_all_data)
source = ColumnDataSource(source_df)
    
#create glyphs
#f_photo.circle(x='time', y='photo_current', color='firebrick', line_color=None, size=8, fill_alpha=0.4, source=source)
f_photo.line(x='time', y='photo_current', line_color='gray', line_width=5, line_alpha=0.5, source=source)

f_laser.line(x='time', y='laser_current', line_color='firebrick', line_width=5, line_alpha=0.5, source=source)

#Style the plot area
f_photo.plot_width = 900
f_photo.plot_height = 400
f_photo.background_fill_color=None
f_photo.border_fill_color=None

f_laser.plot_width = 900
f_laser.plot_height = 200
f_laser.background_fill_color=None
f_laser.border_fill_color=None


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

f_laser.axis.minor_tick_line_color='black'
f_laser.axis.minor_tick_in=-6
f_laser.xaxis.axis_label='Time in (s)'
f_laser.yaxis.axis_label='Laser Current'
f_laser.axis.axis_label_text_color=(0.7,0.7,0.7)
f_laser.axis.major_label_text_color=(0.7,0.7,0.7)
f_laser.axis.axis_label_text_font = 'helvetica'
f_laser.axis.axis_label_text_font_size = '16pt'
f_laser.axis.axis_label_text_font_style = 'normal'
f_laser.axis.major_label_text_font = 'helvetica'
f_laser.axis.major_label_text_font_size = '10pt'
f_laser.axis.major_label_text_font_style = 'normal'

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

f_laser.grid.grid_line_color=(1,1,1)
f_laser.grid.grid_line_alpha=0.3
f_laser.grid.grid_line_dash=[5,3]

#add widgets (dropdown button) to save data as csv. CustomJS required to download data in browser
button = Button(label='Export data', button_type='danger')
js_download = """
var csv = source.get('data');
var filetext = 'time;photo_current;laser_current;date\\n';
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

#add figure to curdoc and configure callback
lay_out=layout([[f_photo],[f_laser],[button]])
curdoc().add_root(lay_out)
curdoc().add_periodic_callback(update,2000) #updates each 2000ms