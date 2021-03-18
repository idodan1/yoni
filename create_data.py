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


def make_df_ready(file_name, dir_name_files, dir_name, col_choice):
    data = pd.read_excel(file_name, index_col=False)
    col_to_plot_by = 'Distance moved.1'
    name_col = 'Unnamed: 0'
    row = list(data[1:2].values[0])
    if len(row) > 8:  # the special case of sleeping files
        name_col = 'Independent Variable'
        if col_choice == "":
            choices = ['Total', 'Frequency', 'Cumulative Duration']
            m = '\n\nin this type of file you need to choose variable to plot by!!\nchoose variable to plot by:\n' +\
                '\n'.join(["{0:<5}{1}".format(i+1, choices[i]) for i in range(len(choices))])
            col_choice = choices[get_input(len(choices), m)]
            # col_choice = "Total"
            home_dir = dir_name[:-1]
            dir_name = home_dir + ' by {0}'.format(col_choice)
            dir_name_files = dir_name + "/excel/"
            os.rename(home_dir, dir_name)
            dir_name += "/"
            col_to_plot_by = list(data.columns)[row.index(col_choice)]

    data = data.loc[data.index.difference([0, 1, 2])]
    data = data.rename(columns={name_col: 'treatment', 'Unnamed: 2': 'col', 'Unnamed: 3': 'time',
                                col_to_plot_by: 'total distance'})
    data = data.reset_index()
    treatments = data.treatment.unique()
    treatments = ["".join([c if c.isalnum() else '_' for c in treatment_name]) for treatment_name in treatments]
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


def create_dir(file_name, col_choice):
    home_dir = 'results from script/'
    if col_choice != "":
        file_name += ' by {0}'.format(col_choice)
    dir_name = home_dir + file_name
    if not path.exists(dir_name):
        os.mkdir(dir_name)
        os.mkdir(dir_name + "/images")
        os.mkdir(dir_name + "/stats")
        os.mkdir(dir_name + "/excel")
    dir_name += '/'
    return dir_name, col_choice


def check_dir_exist(file_name):
    home_dir = 'results from script/'
    dir_list = [f.path for f in os.scandir(home_dir) if f.is_dir()]
    dir_list = [d.split('/')[1] for d in dir_list]
    choices = ['Total', 'Frequency', 'Cumulative Duration']
    for d in dir_list:
        if file_name in d and file_name != d:
            m = '\nin this type of file you need to choose variable to plot by!!\nchoose variable to plot by:\n' + \
                '\n'.join(["{0:<5}{1}".format(i + 1, choices[i]) for i in range(len(choices))])
            col_choice = choices[get_input(len(choices), m)]
            return col_choice
    return ""


def create_df(file_name):
    col_choice = check_dir_exist(file_name)
    dir_name, col_choice = create_dir(file_name, col_choice)
    dir_name_files = dir_name + "/excel/"
    pickle_name = "_treatment_letter.pk1"
    file_name_read = file_name[:len(file_name)-5]
    try:
        results = pd.read_excel(dir_name_files + file_name_read + '_df.xlsx', index_col=0)
        with open(dir_name_files + file_name_read + pickle_name, 'rb') as f:
            treatment_letter = pickle.load(f)
        return results, treatment_letter, dir_name
    except:
        print('\n\nprocessing...')
    results, treatment_letter, dir_name_files, new_dir_name = make_df_ready(file_name, dir_name_files, dir_name,
                                                                            col_choice)
    results = results[:len(results)-1]
    print('\nremoved the last second!!')
    file_name_write = file_name[:len(file_name)-5]
    results.to_excel(dir_name_files + file_name_write + '_df.xlsx')
    with open(dir_name_files + file_name_write + pickle_name, 'wb') as f:
        pickle.dump(treatment_letter, f)
    return results, treatment_letter, new_dir_name



