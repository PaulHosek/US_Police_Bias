
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.layouts import row
from scripts import preprocessing as pp, concatenating as cc
from bokeh.models import Title


def detail_plot(my_state: str):
    """
    Generating the "detail plots" for a selected state.
    Plotting race, gender and age bias in separate bar charts.
    Returning a row layout item for bokeh.
    :param my_state: Name of selected state
    :return: Bokeh row object of three bar chars.
    """
    # 'Race'
    bias_df_race = cc.bias_per_state(pp.fatal_encounters('Race'), pp.race_pop(), filter_var='Race')
    state_only_r = bias_df_race[bias_df_race['State'] == my_state]
    source_r = ColumnDataSource(state_only_r)
    p1 = figure(x_range=state_only_r['Race'], y_range=(-53, 53), toolbar_location=None, tools='zoom_in',
                title=f'Racial bias in {my_state}', plot_width=300, plot_height=300)
    p1.vbar(source=source_r, x='Race', top='Bias', width=0.8)


    p1.add_layout(Title(text="Bias (% deviation from expected value)", align="center"), "left")
    # 'Gender'
    gender = cc.concat_gender_pop(pp.load_male_female(), pp.load_transgender())
    bias_df_gender = cc.bias_per_state(pp.fatal_encounters('Gender'), gender, filter_var='Gender')
    state_only_g = bias_df_gender[bias_df_gender['State'] == my_state]
    source_g = ColumnDataSource(state_only_g)
    p2 = figure(x_range=state_only_g['Gender'], y_range=(-53, 53), toolbar_location=None, tools='',
                title=f'Gender bias in {my_state}', plot_width=300, plot_height=300)
    p2.vbar(source=source_g, x='Gender', top='Bias')

    # 'Age'
    bias_df_age = cc.bias_per_state(pp.fatal_encounters(filter_var='Age'), pp.load_ages_pop(include_total=False),
                                    filter_var='Age')
    state_only_a = bias_df_age[bias_df_age['State'] == my_state]
    source_a = ColumnDataSource(state_only_a)
    p3 = figure(y_range=(-53, 53), toolbar_location=None,
                title=f'Age bias in {my_state}', plot_width=300, plot_height=300)
    p3.vbar(source=source_a, x='Age', top='Bias', width=0.8)

    return row(p1, p2, p3)

