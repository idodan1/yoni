from class_fig import *
from create_data import *

import glob
import xlrd
import warnings
import jinja2
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.simplefilter("ignore")


def get_files():
    files = glob.glob("./*.xlsx")
    if len(files) == 0:
        print("can't find excel files in this dir, close window and run from another dir")
        i = 1
        while True:
            i += 1
    files = [f for f in files if 'df' not in f]
    return files


def choose_file(files):
    print("files in this dir:")
    for i in range(len(files)):
        print("{0:<5} {1}".format(i+1, files[i]))
    m = 'which file do you want to examine? enter num: '
    # return files[get_input(len(files), m)]
    return files[9]


def choose_action():
    print("\n\nwhat do you want to do with this file?")
    options = ['plot', 'box plot', 'bar plot', 'z standard', 'go back to files']
    m = '\n'.join(['{0:<5}{1}'.format(i+1, options[i]) for i in range(len(options))])
    op = get_input(len(options), m)
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
    elif op == 'z standard':
        z_standard(results_without, results_with, dir_name)
    else:
        return 'y'


def create_results_dir(file_name):
    home_dir = 'results from script'
    if not path.exists(home_dir):
        os.mkdir(home_dir)
    file_name = file_name[2:]
    dir_name = home_dir + "/" + file_name
    if not path.exists(dir_name):
        os.mkdir(dir_name)
        os.mkdir(dir_name + "/images")
        os.mkdir(dir_name + "/stats")
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
    m = '\n\nwant to see results in:\n1\tbox plot\n2\tbar plot'
    inp = get_input(2, m)
    if inp == 0:
        box_fig = Fig(results_standard_without, results_standard_with, 'groups', 'mean', 'distance moved z-standard', 'box'
                      , 0, len(results_standard_without), dir_name)
        box_fig.edit()

    else:
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
    try:
        while True:
            files = get_files()
            file_name = choose_file(files)
            dir_name = create_results_dir(file_name)
            good_file = True
            try:
                results_without, results_with = create_df(file_name, dir_name)
            except:
                print('file is not in the right format choose another file')
                good_file = False
            while good_file:
                inp = activate_func(results_without, results_with, dir_name)
                if inp == 'y':
                    break

    except Exception as e:
        traceback.print_exc()
        print(e)
        print('\n\nencountered a problem restarting....\n\n')
        main()


if __name__ == "__main__":
    main()


