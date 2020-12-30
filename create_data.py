import pandas as pd
import numpy as np
import pickle
import os
from class_fig import get_input
from os import path


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


def make_df_ready(file_name, dir_name_files, dir_name):
    data = pd.read_excel(file_name, index_col=False)
    col_to_plot_by = 'Distance moved.1'
    name_col = 'Unnamed: 0'
    row = list(data[1:2].values[0])
    if len(row) > 8:  # the special case of sleeping files
        cols = list(data.columns)
        choices = row[-3:]
        m = '\nin this type of file you need to choose variable to plot by!!\nchoose variable to plot by:\n' +\
            '\n'.join(["{0:<5}{1}".format(i+1, choices[i]) for i in range(len(choices))])
        inp = choices[get_input(len(choices), m)]
        # inp = "Total"
        var_choice = inp
        col_to_plot_by = cols[row.index(inp)]
        name_col = 'Independent Variable'
        home_dir = dir_name_files[:-7]
        i = 0
        while True:
            try:
                dir_name = home_dir + ' by {0}{1}'.format(var_choice, i)
                dir_name_files = dir_name + "/excel"
                os.rename(home_dir, dir_name)
                dir_name += "/"
                break
            except:
                i += 1

    data = data.loc[data.index.difference([0, 1, 2])]
    data = data.rename(columns={name_col: 'treatment', 'Unnamed: 2': 'col', 'Unnamed: 3': 'time',
                                col_to_plot_by: 'total distance'})
    data = data.reset_index()
    treatments = data.treatment.unique()
    cols = data.col.unique()
    cols_letters = []
    for c in cols:
        letter = c[0]
        if letter not in cols_letters:
            cols_letters.append(letter)

    results = pd.DataFrame()
    treatment_letter = {}
    for c in cols:
        temp = data.loc[data['col'] == c]
        treatment_letter[treatments[cols_letters.index(c[0])]] = c[0]
        results[c] = temp['total distance'].values
    results = results.apply(pd.to_numeric, errors='coerce')
    results = results.replace('-', np.NaN)
    return results, treatment_letter, dir_name_files, dir_name


def check_dir_n_df(file_name):
    exist = True
    home_dir = 'results from script'
    if not path.exists(home_dir):
        os.mkdir(home_dir)
        exist = False
    dir_name = home_dir + "/" + file_name
    if not exist or not path.exists(dir_name):
        os.mkdir(dir_name)
        os.mkdir(dir_name + "/images")
        os.mkdir(dir_name + "/stats")
        os.mkdir(dir_name + "/excel")
    return dir_name + '/'


def check_file_type(file_name):
    data = pd.read_excel(file_name, index_col=False)
    return data, len(list(data.columns)) == 8


def create_df(file_name, dir_name_files, dir_name):
    data, reg_file = check_file_type(file_name)
    print(reg_file)
    x = 1
    while True:
        x += 1
    check_dir_n_df(file_name)
    pickle_name = "_treatment_letter.pk1"
    file_name_read = file_name[:len(file_name)-5]
    try:
        results = pd.read_excel(dir_name_files + file_name_read + '_df.xlsx', index_col=0)
        with open(dir_name_files + file_name_read + pickle_name, 'rb') as f:
            treatment_letter = pickle.load(f)
        return results, treatment_letter, dir_name
    except:
        print('\n\nprocessing...')
    results, treatment_letter, dir_name_files, new_dir_name = make_df_ready(file_name, dir_name_files, dir_name)
    results = results[:len(results)-1]
    print('removed the last second!!')
    file_name_write = file_name[:len(file_name)-5]
    results.to_excel(dir_name_files + file_name_write + '_df.xlsx')
    with open(dir_name_files + file_name_write + pickle_name, 'wb') as f:
        pickle.dump(treatment_letter, f)
    return results, treatment_letter, new_dir_name



