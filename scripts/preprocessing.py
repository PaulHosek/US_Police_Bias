
from scripts.utensils import load_json
from os.path import dirname, join
import pandas as pd


def fatal_encounters(filter_var: str):
    """
    Preprocessing of the Fatal Encounters (FE) Dataset.
    Source: https://www.kaggle.com/konradb/fatal-encounters-database
    This takes the dataset from csv to percentages of FE per race in each state.
    Steps include:
        1. Loading of CSV
        2. Cleaning Data of irregularities
        3. Adding a column of state abbreviations
        4. Converting absolute number of FE to percentages, split by filter_var and state
    :param filter_var: additional Column that is used to group data besides state (e.g. Gender, Race, Age)
    :rtype: pandas Dataframe
    :return: Percentages of Fatal encounters split by race and state
    """

    # load csv into dataframe
    script_dir = dirname(__file__)
    fe_path = join(script_dir, '../Data', 'fatal_encounter.csv')
    fe_path = join(script_dir, '../Data', 'fatal_encounter.csv')
    with open(fe_path) as file:
        fatal_encounter = pd.read_csv(file, sep=';', usecols=['State', 'Race', 'Age', 'Gender', 'Unique ID'])

    # clean irregularities in naming conventions
    fatal_encounter['Race'].replace(
        {'African-American/Black': 'Black', 'European-American/White': 'White', 'european-American/White': 'White',
         'Asian/Pacific Islander': 'Asian'},
        inplace=True)
    fatal_encounter['Race'].replace(
        dict.fromkeys(['Hispanic/Latino', 'Native American/Alaskan', 'Race unspecified', 'Middle Eastern'], 'Other'),
        inplace=True)

    # add column of abbreviations for each state
    state_dict = load_json('Abbrv_to_State')
    fatal_encounter['Abbrv'] = fatal_encounter['State']
    fatal_encounter['State'] = fatal_encounter['State'].replace(state_dict)
    # drop rows with NaN values
    fatal_encounter.dropna(axis='index', how='any', inplace=True)

    # reduce dataset to absolute nr of FE and filter_var (e.g. Gender)
    grouped = fatal_encounter.groupby(['State', 'Abbrv', filter_var]).count()['Unique ID']

    # convert absolute number to percentages
    fe_percentages = grouped.groupby(level=0).apply(lambda x: 100 * x / float(x.sum()))
    fe_percentages = pd.DataFrame(fe_percentages).reset_index()
    fe_percentages.rename(columns={'Unique ID': 'Percent_FE'}, inplace=True)
    # no recorded FE for Wyoming if race black
    if filter_var == 'Race':
        fe_percentages = fe_percentages.append({'State': 'Wyoming', 'Abbrv': 'WY', 'Race': 'Black', 'Percent_FE': 0},
                                               ignore_index=True, )

    return fe_percentages


def race_pop():
    """
    Preprocessing of the race population dataset.
    Loading and transforming the Dataset into that describe
    the percentage of the population for a specific race and state.
    Source: https://www.census.gov/data/datasets/time-series/demo/popest/2010s-national-detail.html
    :rtype: Pd Dataframe
    :return: DF with columns: State, Race, Proportion_pop
    """
    # load csv into dataframe
    script_dir = dirname(__file__)
    pop_path = join(script_dir, '../Data', 'Racebystateperc.csv')
    with open(pop_path) as file:
        population_df = pd.read_csv(file, sep=',', usecols=['State', 'WhiteTotalPerc', 'BlackTotalPerc'])

    population_df['OtherTotalPerc'] = 1 - (population_df['WhiteTotalPerc'] + population_df['BlackTotalPerc'])

    # transform into unique rows for state, race and proportion of population in that state
    population_stacked = population_df.set_index('State').stack().reset_index()
    population_stacked.rename(columns={0: 'Proportion_pop', 'level_1': 'Race'}, inplace=True)
    population_stacked.replace({'WhiteTotalPerc': 'White', 'BlackTotalPerc': 'Black', 'OtherTotalPerc': 'Other'},
                               inplace=True)
    population_stacked['Proportion_pop'] = population_stacked['Proportion_pop'] * 100

    return population_stacked


def load_male_female():
    """
    load the dataset on state-wise male female gender distribution
    Source: https://www.kff.org/other/state-indicator/distribution-by-sex/?currentTimeframe=0&sortModel=%7B%22colId%22:%22Location%22,%22sort%22:%22asc%22%7D
    :return: dataset with the male_female percentages per state
    """
    # load csv into dataframe
    script_dir = dirname(__file__)
    pop_path = join(script_dir, '../Data', 'Gender_distribution.csv')
    with open(pop_path) as file:
        gender_1 = pd.read_csv(file, delimiter=';', usecols=['Location', 'Male', 'Female'])

    gender_1.rename(columns={'Location': 'State'}, inplace=True)
    return gender_1[:52]


def load_transgender():
    """
    load the dataset on state-wise transgender distribution
    Source: https://williamsinstitute.law.ucla.edu/wp-content/uploads/Trans-Adults-US-Aug-2016.pdf
    :rtype: dataset with the transgender percentages per state
    """
    script_dir = dirname(__file__)
    pop_path = join(script_dir, '../Data', 'Transgender_per_state.csv')
    with open(pop_path) as file:
        transgender = pd.read_csv(file, delimiter=';', usecols=['State', 'Population', 'Percent'])

    transgender.rename(columns={'Percent': 'Transgender'}, inplace=True)
    return transgender


def load_ages_pop(include_total: bool):
    """
    Loading and transforming the state-wise age distribution dataset.
    Calculating percentages per age in every state.
    Source:https://www.census.gov/data/tables/time-series/demo/popest/2010s-state-detail.html
    :param include_total: If True the datset will include state-wise totals: age == 999
    :return: transformed pandas dataframe stacked by state.
    """
    script_dir = dirname(__file__)
    pop_path = join(script_dir, '../Data', 'Age_distribution.csv')
    with open(pop_path) as file:
        ages_df = pd.read_csv(file, delimiter=',', usecols=['AGE', 'SEX', 'NAME', 'POPEST2019_CIV'])
    ages_df.rename(columns={'AGE': 'Age', 'NAME': 'State', 'SEX': 'Sex', 'POPEST2019_CIV': 'total_pop'}, inplace=True)
    ages_selected = ages_df[ages_df['Sex'] == 0].drop(columns=['Sex'])
    # calculating percentages of the different ages per state
    statewise_totals = ages_selected[ages_selected['Age'] == 999].drop(columns=['Age'])
    age_perc = ages_selected.merge(statewise_totals, on=['State'], how='inner')
    age_perc.rename(columns={'total_pop_x': 'agewise_total', 'total_pop_y': 'statewise_total'}, inplace=True)
    age_perc['Proportion_pop'] = age_perc['agewise_total'] / age_perc['statewise_total'] * 100
    return age_perc if include_total == True else age_perc[age_perc['Age'] != 999]
