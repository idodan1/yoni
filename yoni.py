from class_fig import *
from create_data import *
import traceback
import glob
import xlrd
import warnings
import jinja2
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.simplefilter("ignore")


def get_start_end(len_time):
    m = '\n\nenter {0} time (a number between {1} to {2}): '
    start = get_input(len_time, m.format('start', 0, len_time), 0)
    end = get_input(len_time, m.format('end', start+1, len_time), start+1)
    return start, end


def choose_action_for_graph():
    options = ['mean', 'median', 'sum', 'go back']
    actions = '\n'.join(['{0:<5}{1}'.format(i + 1, options[i]) for i in range(len(options))])
    m = "\nfor every fish calculate by:\n" + actions + "\n"
    # inp = get_input(len(options), m)
    inp = 0  ##########
    return options[inp]


def get_files():
    files = glob.glob("./*.xlsx")
    if len(files) == 0:
        print("can't find excel files in this dir, close window and run from another dir")
        i = 1
        while True:
            i += 1
    files = [f[2:] for f in files]
    return files


def choose_file(files):
    print("files in this dir:")
    for i in range(len(files)):
        print("{0:<5} {1}".format(i+1, files[i]))
    m = '\n\nwhich file do you want to examine? enter num: '
    # return files[get_input(len(files), m)]
    return files[9]  


def choose_action():
    print("\n\nwhat do you want to do with this file?")
    options = ['plot', 'box plot', 'bar plot', 'z standard', 'go back to files']
    m = '\n'.join(['{0:<5}{1}'.format(i+1, options[i]) for i in range(len(options))])
    # op = get_input(len(options), m)
    # op = options[op]
    op = 'z standard'
    return op


def activate_func(results, treatment_letter, dir_name):
    op = choose_action()
    if op == 'plot':
        options = ['mean', 'median', 'go back']
        actions = '\n'.join(['{0:<5}{1}'.format(i + 1, options[i]) for i in range(len(options))])
        m = "\nplot by:\n" + actions + "\n"
        inp = get_input(len(options), m)
        # inp = 0 ##########
        if inp == len(options) - 1:
            return 'y'
        fig = Fig(data=results, treatment_letter=treatment_letter, x_label='time(sec)', y_label='distance(mm)', title='movement over time', g_type='plot',
                  start=0, end=len(results), dir_name=dir_name, how_to_plot=options[inp])
        fig.edit()
    elif op == 'box plot':
        start, end = get_start_end(len(results))
        # start = 0
        # end = 500

        action = choose_action_for_graph()
        if action == 'go back':
            return 'y'

        fig = Fig(data=results, treatment_letter=treatment_letter, x_label='groups', y_label=action,
                  title='box plot', g_type='box', start=start, end=end, dir_name=dir_name,
                  how_to_plot=action)
        fig.edit()
    elif op == 'bar plot':
        start, end = get_start_end(len(results))
        # start = 0
        # end = 500

        action = choose_action_for_graph()
        if action == 'go back':
            return 'y'

        fig = Fig(data=results, treatment_letter=treatment_letter, x_label='groups', y_label=action,
                      title='bar plot', g_type='bar', start=start, end=end, dir_name=dir_name,
                      how_to_plot=action)
        fig.edit()
    elif op == 'z standard':
        z_standard(results, treatment_letter, dir_name)
    else:
        return 'y'


def z_standard(results, treatment_letter, dir_name):
    # start, end = get_start_end(len(results))
    start = 0
    end = 500

    action = choose_action_for_graph()
    if action == 'go back':
        return

    treatments = list(treatment_letter.keys())
    treatment_message = treatments + ['quit and go back']
    m = '\n\nchoose treatment to correct by:\n' + '\n'.join(
        ['{0:<5}{1}'.format(i + 1, treatment_message[i]) for i
         in range(len(treatment_message))])
    # treatment = treatment_message[get_input(len(treatment_message), m)]  ##########
    treatment = treatment_message[0]
    if treatment == 'quit and go back':
        return
    res_options = ['box', 'bar', 'quit and go back']
    m = '\n\nwant to see results in:\n' + '\n'.join(
        ['{0:<5}{1}'.format(i + 1, res_options[i]) for i
         in range(len(res_options))])
    # inp = res_options[get_input(3, m)]
    inp = 'bar'
    if inp == 'quit and go back':
        return
    fig = Fig(data=results, treatment_letter=treatment_letter, x_label='groups', y_label=action,
              title=inp + 'plot', g_type='bar_st', start=start, end=end, dir_name=dir_name,
              how_to_plot=action, treatment=treatment, standard_type=inp)
    fig.edit()

    treatments = fig.treatments_to_plot
    treatment_message = list(treatments) + ['quit and go back']
    m = '\n\nchoose reference treatment:\n' + '\n'.join(['{0:<5}{1}'.format(i + 1, treatment_message[i]) for i
                                                         in range(len(treatment_message))])
    treatment = treatment_message[get_input(len(treatment_message), m)]
    # treatment = treatment_message[0]
    if treatment == 'quit and go back':
        return
    inp = input('want to see bar graph of distance moved (%)?(y/n)')
    if inp == 'y':
        fig.bar_by_percent(treatment)
        inp = input('want to see bar graph of distance moved reduction(%)?(y/n)')
        if inp == 'y':
            fig.bar_percent_reduction(treatment)


def create_results_dir(file_name):
    home_dir = 'results from script'
    if not path.exists(home_dir):
        os.mkdir(home_dir)
    file_name = file_name
    dir_name = home_dir + "/" + file_name
    if not path.exists(dir_name):
        os.mkdir(dir_name)
        os.mkdir(dir_name + "/images")
        os.mkdir(dir_name + "/stats")
        os.mkdir(dir_name + "/excel")
    return dir_name + '/'


def main():
    try:
        while True:
            files = get_files()
            file_name = choose_file(files)
            dir_name = create_results_dir(file_name)
            dir_name_df = dir_name + "/excel"
            good_file = True
            try:
                results, treatment_letter, dir_name = create_df(file_name, dir_name_df, dir_name)
            except Exception as e:
                traceback.print_exc()
                print(e)
            # except:
            #     print('\n\nfile is not in the right format choose another file\n\n')
            #     good_file = False
            while good_file:
                inp = activate_func(results, treatment_letter, dir_name)
                if inp == 'y':
                    break

    except Exception as e:
        traceback.print_exc()
        print(e)
        print('\n\nencountered a problem restarting....\n\n')
        main()


if __name__ == "__main__":
    main()


