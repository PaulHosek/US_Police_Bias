# 
from scripts import preprocessing as pp, concatenating as cc
from scripts.detail_plots import detail_plot

from os.path import join
import geopandas as gpd

from bokeh.events import Tap
from bokeh.plotting import figure
from bokeh.layouts import column, row
from bokeh.models import (HoverTool, TapTool, Select, Spinner,
                          ColorBar, GeoJSONDataSource, LinearColorMapper)
from json import loads

def load_geometry():
    """
    Load the shapefile to be able to plot a map of the U.S.
    :return: GeoDataFrame
    """
    pop_path = join('Data', 'Geometry', 'cb_2018_us_state_20m.shp')
    us_coor = gpd.read_file(pop_path)
    return us_coor


def merge_map(maptype_df, filter_var, your_filter_var):
    """
    Create source data for the map.
    This function first merges the geometry data from the shapefile
    with a selected characteristic (Race, Gender or Age).
     Then it selects the user's characteristic (e.g. Black).
    :type maptype_df: geopandas DF / output of load_geometry()  (e.g. Race, Gender or Age)
    :param your_filter_var: Own characteristic (e.g. Black, Female, 25 )
    :return: Geopandas dataframe of the map to be plotted.
    """
    if filter_var == 'Race':
        bias = cc.bias_per_state(pp.fatal_encounters('Race'), pp.race_pop(), filter_var='Race')

    elif filter_var == 'Gender':
        gender_pop = cc.concat_gender_pop(pp.load_male_female(), pp.load_transgender())
        bias = cc.bias_per_state(pp.fatal_encounters('Gender'), gender_pop, filter_var='Gender')
    else:
        bias = cc.bias_per_state(pp.fatal_encounters('Age'), pp.load_ages_pop(include_total=False), filter_var='Age')
    # e.g. select only 'Female' for Gender
    bias = bias[bias[filter_var] == your_filter_var]
    return maptype_df.merge(bias, left_on='NAME', right_on='State', how='inner')


def map_plotting(doc):
    """
    Main plotting function. Plots map of the United States, adds interactive features,
    integrates detail bar-plots.
    :param doc: allows to be shown in ipynb with show()
    """

    # COLOUR MAPPING
    red_white_green = ['#006d2c', '#31a354', '#74c476', '#bae4b3', '#edf8e9', '#fee5d9', '#fcae91', '#fb6a4a',
                       '#de2d26', '#a50f15']
    geometry = load_geometry()
    palette = red_white_green
    colour_mapping = LinearColorMapper(palette=palette, nan_color='gray')
    color_bar = ColorBar(color_mapper=colour_mapping, title='Police Bias')

    # WIDGETS
    select2_fc = Select(title='Fill colour based on:', value='Race', options=['Race', 'Gender', 'Age'], width=150)
    select3_yg = Select(title='Your Gender', value='Female', options=['Female', 'Male', 'Transgender'], width=150)
    select4_yr = Select(title='Your Race', value='Black', options=['Black', 'White', 'Other'], width=150)
    spinner1_ya = Spinner(title='Your Age', low=1, high=85, step=1, value=21, width=150)
    your_data = {'Gender': select3_yg, 'Race': select4_yr, 'Age': spinner1_ya}

    # DATA LOADING
    geosource = GeoJSONDataSource(geojson=
                                  merge_map(maptype_df=geometry, filter_var=select2_fc.value,
                                            your_filter_var=your_data[select2_fc.value].value).to_json())
    some_new_map = GeoJSONDataSource(geojson=
                                     merge_map(maptype_df=geometry, filter_var=select2_fc.value,
                                               your_filter_var=your_data[select2_fc.value].value).to_json())

    # TITLE MODIFICATION
    def update_title():
        geosource.selected.indices = []
        p.title.text = f'How much more likely does being {your_data[select2_fc.value].value} make you to be kiled by the police, compared with any other {select2_fc.value}? '
        p.x_range.bounds = (-180, -60)

    # COLOURING YOUR CHARACTERISTIC (e.g. Black)
    def update_fillcol_you(attrname, old, new):
        remove_details()
        geosource.selected.indices = []
        update_title()
        your_data = {'Gender': select3_yg, 'Race': select4_yr, 'Age': spinner1_ya}
        geosource.geojson = merge_map(maptype_df=geometry,
                                      filter_var=select2_fc.value,
                                      your_filter_var=your_data[select2_fc.value].value).to_json()

    select3_yg.on_change('value', update_fillcol_you)
    select4_yr.on_change('value', update_fillcol_you)
    spinner1_ya.on_change('value', update_fillcol_you)

    # COLOURING MAP CHARACTERISTIC (RACE, AGE or Gender)
    def update_fillcol(attrname, old, new):
        update_title()
        remove_details()
        geosource.selected.indices = []
        geosource.geojson = merge_map(maptype_df=geometry,
                                      filter_var=select2_fc.value,
                                      your_filter_var=your_data[select2_fc.value].value).to_json()

    select2_fc.on_change('value', update_fillcol)

    # FIGURE
    p = figure(
        title=f'How much more likely does being {your_data[select2_fc.value].value} make you to be kiled by the police, compared with any other {select2_fc.value}? ',
        x_range=(-180, -60), y_range=(0, 75), plot_width=800, plot_height=500, toolbar_location=None)
    states_v2 = p.patches('xs', 'ys', source=geosource, line_color='grey',
                          fill_color={'field': 'Bias', 'transform': colour_mapping})
    p.add_tools(HoverTool(renderers=[states_v2], tooltips=[('State', '@State'), ('Bias', '@Bias')]))
    p.add_tools(TapTool(behavior='select'))

    # SHOW/ HIDE BAR-PLOTS
    def append_details(layout_detailed):
        column2.children.append(layout_detailed)

    def remove_details():
        # if there is already a state selected, remove old one
        if len(column2.children) > 1:
            column2.children.remove(column2.children[-1])

    # CLICK ON STATE
    def update_detail(event):
        selected_indx = geosource.selected.indices
        remove_details()
        if selected_indx != []:
            reverse_json = loads(geosource.geojson)['features']
            state = reverse_json[selected_indx[0]]['properties']['NAME']
            layout_detailed = detail_plot(state)
            append_details(layout_detailed)

    # if click, then add/remove bar-chart
    p.on_event(Tap, update_detail)

    # LAYOUT
    p.add_layout(color_bar, 'right')
    column1 = column(select2_fc, select3_yg, select4_yr, spinner1_ya)
    column2 = column(row(p))  # insert detail plots here!
    layout2 = row(column1, column2)
    doc.add_root(row(layout2))