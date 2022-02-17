from flask import Flask,redirect,render_template,url_for

import numpy as np

from bokeh.models import ColumnDataSource, BoxSelectTool
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.layouts import layout
from bokeh.models import CustomJS

import pandas as pd

#instantiate the flask app
app = Flask(__name__)

df = pd.read_csv('AirQualityUCI.csv',delimiter=";")
data = df['PT08.S1(CO)'].dropna().to_frame()
data = data.rename({'PT08.S1(CO)':'values'}, axis="columns")

data = data.loc[:2000]

nan_list = [np.nan for x in data.iterrows()]
nan_df = pd.DataFrame(nan_list)
data['pattern'] = nan_df
source = ColumnDataSource(data)

global_plot = figure(plot_width=1200, plot_height=250, title='Initial Time Series',background_fill_color="#efefef", tools="xpan,reset")
global_plot.add_tools(BoxSelectTool( dimensions="width"))
g_line = global_plot.line(x='index', y='values',source=source)
g_circle = global_plot.circle(x='index', y='values',source=source, alpha=0)
    
similar_plot = figure(plot_width=1200, plot_height=250, title='Similar Time Series',background_fill_color="#efefef", tools="xpan,reset")

grid = layout([global_plot,similar_plot],sizing_mode="stretch_width")

#create index page function
@app.route('/')
def bokeh():
    callback = CustomJS(args=dict(p=global_plot), code="""
        var inds = cb_obj.indices;
        var start, end = inds[0], inds[inds.length-1]

        console.log("start:",inds[0]," end: ",inds[inds.length-1]);
        """)

    source.selected.js_on_change('indices', callback)

    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    # render template
    script, div = components(grid)
    html = render_template(
        'index.html',
        plot_script=script,
        plot_div=div,
        js_resources=js_resources,
        css_resources=css_resources,
    )
    return html

@app.route("/<start>:<end>")
def mp(start,end):

    source_tmp = ColumnDataSource(data.iloc[int(start):int(end)])
    s_line = similar_plot.line(x='index', y='values',source=source_tmp)
    s_circle = similar_plot.circle(x='index', y='values',source=source_tmp, alpha=0)
    return redirect(url_for("bokeh"))

@app.route("/foobar")
def foo():
    print("request successful")

if __name__ == "__main__":
	app.run(debug=True)