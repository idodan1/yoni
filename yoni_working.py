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
    return files


def choose_file(files):
    print("files in this dir:")
    for i in range(len(files)):
        print("{0:<5} {1}".format(i+1, files[i]))
    # m = 'which file do you want to examine? enter num: '
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


def report_outliers(results, history, treatments, dir_name):
    dir_name = dir_name + 'outliers_data'
    if not path.exists(dir_name):
        os.mkdir(dir_name)
    create_excel_outliers(results, dir_name)
    print("\n\nfound and removed {0} outliers, check outliers_data dir to see them".format(sum([len(l) for l in history])))
    f = open(dir_name+'/outliers by treatment', 'w')
    for i in range(len(treatments)):
        f.write("{0}: {1}\n\n".format(treatments[i], list(history[i])))
    f.close()


def remove_outliers(arr):
    lst = np.copy(arr)
    sd = np.std(lst)
    mean = np.mean(lst)
    outliers_history = []
    for i in range(len(lst)):
        val = lst[i]
        if (val - 2*sd) > mean or (val + 2*sd) < mean:
            outliers_history.append(i)
    lst = np.delete(lst, outliers_history)
    return lst, outliers_history


def create_excel_outliers(df, dir_name):
    new_row = pd.DataFrame({col: np.std(df[col].values) for col in df.columns}, index=[1])
    df = pd.concat([new_row, df[:]]).reset_index(drop=True)
    new_row = pd.DataFrame({col: np.mean(df[col].values) for col in df.columns}, index=[0])
    df = pd.concat([new_row, df[:]]).reset_index(drop=True)
    df.rename(index={0: 'mean', 1: 'std'}, inplace=True)
    df.index = ['mean', 'std'] + list(range(0, len(df)-2))

    df = df.style.apply(highlight_outliers)
    df.to_excel(dir_name+'/outliers data frame.xlsx', engine='openpyxl')


def highlight_outliers(s):
    mean = s['mean']
    sd = s['std']
    is_outlier_high = s > mean+2*sd
    is_outlier_low = s < mean-2*sd
    return ['background-color: yellow' if v else '' for v in is_outlier_high | is_outlier_low]


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
    options = ['plot', 'box plot', 'bar plot']
    m = '\n'.join(['{0:<5}{1}'.format(i+1, options[i]) for i in range(len(options))])
    # op = get_input(len(options), m)
    # op = options[op]
    op = 'plot'
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


def z_standard(results, dir_name):
    treatments = results.columns
    m = '\n\nchoose treatment to correct by:\n' + '\n'.join(['{0:<5}{1}'.format(i+1, treatments[i]) for i
                                                             in range(len(treatments))])
    # treatment = treatments[get_input(len(treatments), m)]
    treatment = treatments[0]

    t_mean = results[treatment].mean()
    t_std = results[treatment].std()
    '''
    t_mean = results[treatment][6:90].mean()  # to compare with ram
    t_std = results[treatment][6:90].std()
    '''
    results_standard = results.drop([treatment], axis=1)
    results_standard = (results_standard - t_mean)/t_std
    box_fig = Fig(results_standard, results_standard, 'groups', 'mean', 'distance moved z-standard', 'box', 0,
                  len(results_standard), dir_name)
    # box_fig.edit()
    bar_fig = Fig(results_standard, results_standard, 'groups', 'mean', 'distance moved z-standard', 'bar', 0,
                  len(results_standard), dir_name)
    # bar_fig.edit()
    treatments = results_standard.columns
    m = '\n\nchoose reference treatment:\n' + '\n'.join(['{0:<5}{1}'.format(i + 1, treatments[i]) for i
                                                         in range(len(treatments))])
    # treatment = treatments[get_input(len(treatments), m)]
    treatment = treatments[0]
    bar_fig = Fig(results_standard, results_standard, 'groups', 'mean', 'distance moved (%)', 'bar_st', 0,
                  len(results_standard), dir_name, treatment)
    bar_fig.edit()

    bar_fig = Fig(results_standard, results_standard, 'groups', 'mean', 'distance moved reduction(%)', 'bar_st_red', 0,
                  len(results_standard), dir_name, treatment)
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
        # results, treatments, times = create_df(file_name)
        results_without, results_with = create_dfs(file_name, dir_name)
        # z_standard(results, dir_name)
        while True:
            activate_func(results_without, results_with, dir_name)
            inp = input('\n\nwant to continue to explore this file? press y for yes or any other button for no')
            if inp != 'y':
                break
        inp = input('want to quit? press q. if not press any button and it will start again: ')
        # inp = 'q'
        if inp == 'q':
            break


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        traceback.print_exc()
        print(e)
        print('\n\nencountered a problem restarting....\n\n')
        # main()


