from class_fig import *
from create_data import *

import traceback
import glob
import xlrd
import warnings
import jinja2
import os
from datetime import datetime
# import scikit_posthocs as sp
from scipy import stats
from os import path
warnings.filterwarnings("ignore", category=DeprecationWarning)


def get_files():
    files = glob.glob("./*.xlsx")
    if len(files) == 0:
        print("can't find excel files in this dir, run from another dir")
        exit(1)
    files = [f for f in files if 'df' not in f]
    return files


def choose_file(files):
    print("files in this dir:")

    for i in range(len(files)):
        print("{0:<5} {1}".format(i+1, files[i]))
    m = 'which file do you want to examine? enter num: '
    # return files[get_input(len(files), m)]
    return files[2]


def create_df(file_name):
    data = pd.read_excel(file_name, index_col=False)
    data = data.loc[data.index.difference([0, 1, 2, 3])]
    data = data.rename(columns={'Unnamed: 0': 'treatment', 'Unnamed: 1': 'time', 'Distance moved.1': 'mean'})
    data = data.reset_index()
    treatments = list(data.treatment.unique())
    times = list(data.time.unique())
    results = pd.DataFrame()
    for t in treatments:
        temp = data.loc[data['treatment'] == t]
        results[t] = temp['mean'].values
    results = results[:len(results)-1]
    times = times[:len(times)]
    print('removed the last second!!')
    results = results[~results.isin(["?"])]
    return results, treatments, times


def kruskal_wallis(lst_groups, dir_name, with_outliers=''):
    f = open(dir_name + 'kruskal_wallis_results '+with_outliers, 'w')
    k_w_res = stats.kruskal(*lst_groups)
    h_val, p_val = k_w_res
    f.write('h value = {0}\n'.format(h_val))
    f.write('p value = {0}\n'.format(p_val))
    print("\n\npreformed kruskal wallis test, results in kruskal_wallis_results")
    # post_hoc_df = sp.posthoc_dunn(lst_groups, p_adjust='holm')
    # post_hoc_df.to_excel(dir_name + "post_hoc_res "+with_outliers+'.xlsx')
    f.close()
    print("\n\npreformed dunn test, results in post_hoc_res")


def choose_action():
    print("\n\nwhat do you want to do with this file?")
    options = ['plot', 'box plot', 'bar plot', 'z standard', 'go back to files']
    m = '\n'.join(['{0:<5}{1}'.format(i+1, options[i]) for i in range(len(options))])
    op = get_input(len(options), m)
    op = options[op]
    # op = 'plot'
    return op


def activate_func(results_without, results_with, dir_name):
    op = choose_action()
    if op == 'plot':
        fig = Fig(results_without, results_with, 'time(sec)', 'distance(mm)', 'movement over time', 'plot', 0, len(results_without),
                  dir_name)
        fig.edit()
    elif op == 'box plot':
        fig = Fig(results_without, results_with, 'groups', 'mean', 'box plot', 'box', 0, len(results_without), dir_name)
        fig.edit()
    elif op == 'bar plot':
        fig = Fig(results_without, results_with, 'groups', 'mean', 'bar plot', 'bar', 0, len(results_without), dir_name)
        fig.edit()
    elif op == 'z standard':
        z_standard(results_without, results_with, dir_name)
    else:
        return 'y'


def create_results_dir(file_name):
    home_dir = 'results from script'
    if not path.exists(home_dir):
        os.mkdir(home_dir)
    t = str(datetime.now())
    file_name = file_name[2:]
    today = '{0}-{1}-{2} {3}-{4}-{5}'.format(t[:4], t[5:7], t[8:10], t[11:13], t[14:16], t[17:19])
    dir_name = home_dir + "/" + file_name + " " + today
    os.mkdir(dir_name)
    os.mkdir(dir_name + "/images")
    return dir_name + '/'


def z_standard(results_without, results_with, dir_name):
    treatments = results_without.columns
    m = '\n\nchoose treatment to correct by:\n' + '\n'.join(['{0:<5}{1}'.format(i+1, treatments[i]) for i
                                                             in range(len(treatments))])
    treatment = treatments[get_input(len(treatments), m)]

    t_mean_without, t_mean_with = results_with[treatment].mean(), results_with[treatment].mean()
    t_std_without, t_std_with = results_without[treatment].std(), results_with[treatment].std()
    '''
    t_mean = results[treatment][6:90].mean()  # to compare with ram
    t_std = results[treatment][6:90].std()
    '''
    results_standard_without, results_standard_with = results_without.drop([treatment], axis=1),\
                                                      results_with.drop([treatment], axis=1)
    results_standard_without = (results_standard_without - t_mean_without)/t_std_without
    results_standard_with = (results_standard_with - t_mean_with)/t_std_with
    box_fig = Fig(results_standard_without, results_standard_with, 'groups', 'mean', 'distance moved z-standard', 'box'
                  , 0, len(results_standard_without), dir_name)
    box_fig.edit()

    bar_fig = Fig(results_standard_without, results_standard_with, 'groups', 'mean', 'distance moved z-standard', 'bar', 0,
                  len(results_standard_without), dir_name)
    bar_fig.edit()

    treatments = results_standard_without.columns
    m = '\n\nchoose reference treatment:\n' + '\n'.join(['{0:<5}{1}'.format(i + 1, treatments[i]) for i
                                                         in range(len(treatments))])
    treatment = treatments[get_input(len(treatments), m)]
    bar_fig = Fig(results_standard_without, results_standard_with, 'groups', 'mean', 'distance moved (%)', 'bar_st', 0,
                  len(results_standard_without), dir_name, treatment)
    bar_fig.edit()

    bar_fig = Fig(results_standard_without, results_standard_with, 'groups', 'mean', 'distance moved reduction(%)',
                  'bar_st_red', 0, len(results_standard_without), dir_name, treatment)
    bar_fig.edit()
    """ for compering with ram
    bar_fig = Fig(results_standard, results_standard, 'groups', 'mean', 'distance moved (%)', 'bar_st', 1,
                  90, dir_name, treatment)
    bar_fig.edit()

    bar_fig = Fig(results_standard, results_standard, 'groups', 'mean', 'distance moved reduction(%)', 'bar_st_red', 1,
                  90, dir_name, treatment)
    bar_fig.edit()
    """


def main():
    while True:
        files = get_files()
        file_name = choose_file(files)
        dir_name = create_results_dir(file_name)
        results_without, results_with = create_dfs(file_name, dir_name)
        while True:
            inp = activate_func(results_without, results_with, dir_name)
            if inp == 'y':
                break


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        traceback.print_exc()
        print(e)
        print('\n\nencountered a problem restarting....\n\n')
        main()


