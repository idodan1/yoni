import pandas as pd
import os
import numpy as np
import traceback
from os import path


def report_outliers(df, treatment_name, dir_name):
    dir_name = dir_name + 'outliers_data'
    if not path.exists(dir_name):
        os.mkdir(dir_name)
    create_excel_outliers(df, treatment_name, dir_name)


def remove_outliers(arr):
    lst = np.copy(arr)
    sd = np.std(lst)
    mean = np.mean(lst)
    outliers_history = []
    for i in range(len(lst)):
        val = lst[i]
        if (val - 2*sd) > mean or (val + 2*sd) < mean or val < 0:
            outliers_history.append(i)
    lst = np.delete(lst, outliers_history)
    return lst


def create_excel_outliers(df, treatment_name, dir_name):
    index = list(df.index)
    values = [[v for v in df[col].values if v >= 0] for col in df.columns]
    columns = df.columns
    new_row = pd.DataFrame({columns[i]: np.std(values[i]) for i in range(len(columns))}, index=[1])
    df = pd.concat([new_row, df[:]]).reset_index(drop=True)
    new_row = pd.DataFrame({columns[i]: np.mean(values[i]) for i in range(len(columns))}, index=[0])
    df = pd.concat([new_row, df[:]]).reset_index(drop=True)
    df.rename(index={0: 'mean', 1: 'std'}, inplace=True)
    df.index = ['mean', 'std'] + index

    df = df.style.apply(highlight_outliers)
    treatment_name = treatment_name.replace('/', '.')
    df.to_excel(dir_name + "/" + treatment_name + '_outliers data frame.xlsx', engine='openpyxl')


def highlight_outliers(s):
    values = [v for v in s.values if v >= 0]
    mean = np.mean(values)
    sd = np.std(values)
    is_minus = s < 0
    is_outlier_high = s > mean+2*sd
    is_outlier_low = s < mean-2*sd
    return ['background-color: yellow' if v else '' for v in is_minus | is_outlier_high | is_outlier_low]


def create_df(file_name, dir_name):
    check_file_exist = file_name[:len(file_name)-5] + '_df'
    try:
        results_without = pd.read_excel(dir_name + check_file_exist + '.xlsx', index_col=False)
        results_without = results_without.drop(['Unnamed: 0'], axis=1)
        results_with = pd.read_excel(dir_name + check_file_exist + '_outliers.xlsx', index_col=False)
        results_with = results_with.drop(['Unnamed: 0'], axis=1)
        return results_without, results_with
    except:
        print('\n\nprocessing...')
    data = pd.read_excel(file_name, index_col=False)
    data = data.loc[data.index.difference([0, 1, 2])]
    data = data.rename(columns={'Unnamed: 0': 'treatment', 'Unnamed: 2': 'col', 'Unnamed: 3': 'time',
                                'Distance moved.1': 'total distance'})
    data = data.reset_index()
    treatments = data.treatment.unique()
    cols = data.col.unique()
    cols_letters = []
    for c in cols:
        letter = c[0]
        if letter not in cols_letters:
            cols_letters.append(letter)

    results = pd.DataFrame()
    for c in cols:
        temp = data.loc[data['col'] == c]
        treatment = treatments[cols_letters.index(c[0])]
        col_name = treatment + "_" + c
        results[col_name] = temp['total distance'].values

    results = results.replace('-', -1)

    results_without = pd.DataFrame()
    results_with = pd.DataFrame()
    print(results.columns)
    for t in treatments:
        all_t = [c for c in results.columns if c.split('_')[0] == t]
        t_df = results[all_t]
        print(t_df)
        report_outliers(t_df.T, t, dir_name)
        without_outliers = []
        with_outliers = []
        for i in range(len(t_df)):
            values = [v for v in t_df[i:i+1].values[0] if v >= 0]
            with_outliers.append(np.mean(values))
            values_without = remove_outliers(values)
            without_outliers.append(np.mean(values_without))
        results_with[t] = with_outliers
        results_without[t] = without_outliers

    results_without = results_without[:len(results_without)-1]
    results_with = results_with[:len(results_with)-1]
    print('removed the last second!!')
    file_name = file_name[:len(file_name)-5]
    results_with.to_excel(dir_name + file_name + '_df_outliers.xlsx')
    results_without.to_excel(dir_name + file_name + '_df.xlsx')
    return results_without, results_with




