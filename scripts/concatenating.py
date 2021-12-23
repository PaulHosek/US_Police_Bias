

def concat_gender_pop(male_female_df, transgender_df):
    """
    Concatenate the male_female data with the transgender dataset.
    Transgender, Male and Female data is adjusted equally.
    :param male_female_df: preprocessing.male_female()
    :param transgender_df: preprocessing.transgender
    :return: Adjusted population data for all genders in the fatal encounter dataset.
    """
    from pandas import merge
    mft_pop = merge(male_female_df, transgender_df, on='State', how='inner')
    # transgender values are in percent (e.g. 0.005%)
    mft_pop['Transgender'] = mft_pop['Transgender'] / 100
    mft_pop['Total'] = mft_pop['Male'] + mft_pop['Female'] + mft_pop['Transgender']
    # adjusted for the transgender data
    mft_pop['Male'] = mft_pop['Male'] / mft_pop['Total']
    mft_pop['Female'] = mft_pop['Female'] / mft_pop['Total']
    mft_pop['Transgender'] = mft_pop['Transgender'] / mft_pop['Total']
    mft_pop = mft_pop.drop(columns=['Population', 'Total'])

    # transform into unique rows for state, gender and proportion of population in that state
    mft_pop_stacked = mft_pop.set_index('State').stack().reset_index()
    mft_pop_stacked.rename(columns={0: 'Proportion_pop', 'level_1': 'Gender'}, inplace=True)
    mft_pop_stacked['Proportion_pop'] = mft_pop_stacked['Proportion_pop'] * 100

    return mft_pop_stacked


def bias_per_state(fatal_encounters_df, population_percentage_df, filter_var: str):
    """
    Calculate bias in percent deviation from expected value.
    Specifically, Bias =
    expected FE proportion based on population characteristics per state - actual FE proportion.
    :param fatal_encounters_df: takes in DF returned by preprocessing.fatal_encounters()
    :param population_percentage_df: takes in DF returned by preprocessing.population_percentage()
    :param filter_var: either gender or race
    :rtype: pandas.Dataframe
    :return: DF with columns: State, Abbrv, Race, Percent_FE, Proportion_pop, bias, Abbr
    """
    from pandas import merge
    # merge data on percentages of FE per state with percentages of population per state
    bias = merge(fatal_encounters_df, population_percentage_df, on=['State', filter_var], how='inner')
    # calculate bias in % deviation of FE frequency per race from expected value based on population
    bias['Bias'] = bias['Percent_FE'] - bias['Proportion_pop']
    return bias