import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.cm as cm
from scipy import stats
import scikit_posthocs as sp
import os
from os import path
import copy


def highlight_outliers(s):
    values = [v for v in s.values]
    mean = np.nanmean(values)
    sd = np.nanstd(values)
    is_outlier_high = s > mean+2*sd
    is_outlier_low = s < mean-2*sd
    return ['background-color: yellow' if v else '' for v in is_outlier_high | is_outlier_low]


def get_input(end, message, start=1):
    print(message)
    val = input()
    if val.isdigit():
        val = int(val)
        if start <= val <= end:
            return val-1
    print('wrong input try again...')
    return get_input(end, message, start)


def report_outliers(df, treatment_name, dir_name, type_plot):
    dir_name = dir_name + 'outliers data ' + type_plot
    if not path.exists(dir_name):
        os.mkdir(dir_name)
    create_excel_outliers(df, treatment_name, dir_name)


def create_excel_outliers(df, treatment_name, dir_name):
    try:
        return pd.read_excel(dir_name + "/" + treatment_name + '_outliers data frame.xlsx', engine='openpyxl',
                             index_col=0)
    except:
        index = list(df.index)
    values = [[v for v in df[col].values if v >= 0] for col in df.columns]
    columns = df.columns
    new_row = pd.DataFrame({columns[i]: np.nanstd(values[i]) for i in range(len(columns))}, index=[1])
    df = pd.concat([new_row, df[:]]).reset_index(drop=True)
    new_row = pd.DataFrame({columns[i]: np.nanmean(values[i]) for i in range(len(columns))}, index=[0])
    df = pd.concat([new_row, df[:]]).reset_index(drop=True)
    df.rename(index={0: 'mean', 1: 'std'}, inplace=True)
    df.index = ['mean', 'std'] + index

    df = df.style.apply(highlight_outliers)
    treatment_name = treatment_name.replace('/', '.')
    df.to_excel(dir_name + "/" + treatment_name + '_outliers data frame.xlsx', engine='openpyxl')


def define_time_jump(results, time_jump, how_to_plot):
    results_jump = pd.DataFrame(columns=results.columns)
    for i in range(0, len(results)//time_jump):
        if how_to_plot == 'mean':
            results_jump = results_jump.append(pd.Series(list(results[i*time_jump:(i+1)*time_jump].mean().values),
                                                         index=results_jump.columns), ignore_index=True)
        else:
            results_jump = results_jump.append(pd.Series(list(results[i * time_jump:(i + 1) * time_jump].median().values),
                                                     index=results_jump.columns), ignore_index=True)
    if len(results)//time_jump != len(results)/time_jump:
        if how_to_plot == 'mean':
            results_jump = results_jump.append(pd.Series(list(results[len(results)//time_jump * time_jump:
                                                                      (len(results)//time_jump + 1) * time_jump]
                                                              .mean().values), index=results_jump.columns),
                                               ignore_index=True)
        else:
            results_jump = results_jump.append(pd.Series(list(results[len(results) // time_jump * time_jump:
                                                                      (len(results) // time_jump + 1) * time_jump]
                                                              .median().values), index=results_jump.columns),
                                               ignore_index=True)
    return results_jump


def already_exist(g1, g2, dic):
    for val in dic.values():
        if g1 in val and g2 in val:
            return True
    return False


def remove_outliers(arr):
    lst = np.copy(arr)
    sd = np.nanstd(lst)
    mean = np.nanmean(lst)
    outliers_history = []
    for i in range(len(lst)):
        val = lst[i]
        if (val - 2*sd) > mean or (val + 2*sd) < mean:
            outliers_history.append(i)
    lst = np.delete(lst, outliers_history)
    return lst


def already_contained(lst, dic):
    for key in dic:
        if set(lst) < set(dic[key]):
            return True
    return False


class Fig:
    colors = {'p': 'purple', 'b': 'blue', 'c': 'cyan', 'bg': 'blue-green', 'g': 'green', 'y': 'yellow', 'o': 'orange',
              'r': 'red'}
    col_val = list(cm.rainbow(np.linspace(0, 1, 8)))
    colors_letter = list(colors.keys())
    color_values = {}
    for i in range(len(col_val)):
        color_values[colors_letter[i]] = col_val[i]

    def __init__(self, data, treatment_letter, x_label, y_label, title, g_type, start, end, dir_name, how_to_plot,
                 treatment="", standard_type="", remove_liars=False):
        self.data = data[start:end]
        self.treatment_letter = copy.deepcopy(treatment_letter)
        self.treatments_to_plot = copy.deepcopy(list(treatment_letter.keys()))
        self.x_label = x_label
        self.y_label = y_label
        self.title = title + " by {0}".format(how_to_plot)
        self.type = g_type
        self.start = start
        self.end = end
        self.dir_name_images = dir_name + 'images/'
        self.dir_name_stats = dir_name + 'stats/'
        self.dir_name_df = dir_name + 'excel/'
        self.time_jump = 1
        self.treatment = treatment
        self.colors = {self.treatments_to_plot[i]: Fig.col_val[i] for i in range(len(self.treatments_to_plot))}
        self.kruskal = False
        self.groups_letter_without = []
        self.groups_letter_with = []
        self.signature = self.get_signature()
        self.grid = True
        self.how_to_plot = how_to_plot
        self.standard_type = standard_type
        self.remove_liars = remove_liars
        self.title_size = 12
        self.xlabel_size = 10
        self.ylabel_size = 10
        self.legend_size = 10
        self.time_size = 8
        self.groups_label_size = 8
        self.groups_letter_size = 10
        self.remove_liars_over_time = False
        if self.type == 'bar' or self.type == 'bar_st':
            self.std = True
        if self.type != 'plot':
            self.dir_name_stats = self.dir_name_stats + 'start time={0}, end time={1}'.format(self.start, self.end)
            if not path.exists(self.dir_name_stats):
                os.mkdir(self.dir_name_stats)
            self.dir_name_stats += '/'

    def create_df_for_plot(self, data):
        df_name = "df for plot by {0}.xlsx".format(self.how_to_plot)
        try:
            return pd.read_excel(self.dir_name_df + df_name, index_col=0)
        except:
            print('\n\nit will take a few seconds :)')
        res_df = pd.DataFrame()
        letter_treatment = {v: k for k, v in self.treatment_letter.items()}
        for treatment in self.treatments_to_plot:
            letter = self.treatment_letter[treatment]
            col_df = data[[col for col in data.columns if letter in col]]
            if self.how_to_plot == 'median':
                res_df[letter_treatment[letter]] = col_df.median(axis=1)
            elif self.how_to_plot == 'mean':
                report_outliers(col_df.T, letter_treatment[letter], self.dir_name_stats, 'plot')
                col_df = col_df.T
                lst = [list(col_df[col].values) for col in col_df.columns]
                lst_without = [remove_outliers(arr) for arr in lst]
                res_df[letter_treatment[letter]] = [np.nanmean(l) for l in lst_without]
        if self.how_to_plot == 'mean':
            print('\n\nremoved outliers from data frame')
            print('you can find outliers data in stats')
        res_df.to_excel(self.dir_name_df + df_name)
        print('you can find df for plot in excel dir')
        return res_df

    def create_df_for_box(self, ouliers_title):
        if self.how_to_plot == 'mean':
            self.remove_liars_over_time = input("\n\nremove outliers values in this time period? (y/n)") == 'y'
            if self.remove_liars_over_time:
                print('\n\nyou can find outliers data in stats')
        print('\n\nit will take a few seconds :)')
        letter_treatment = {v: k for k, v in self.treatment_letter.items()}
        res = pd.DataFrame()
        for treatment in self.treatments_to_plot:
            letter = self.treatment_letter[treatment]
            cols = [col for col in self.data.columns if letter in col]
            col_df = self.data[cols]
            lst = [list(col_df[col].values) for col in col_df.columns]
            if self.how_to_plot == 'mean':
                lst_without = lst
                if self.remove_liars_over_time:
                    report_outliers(col_df, letter_treatment[letter], self.dir_name_stats, ouliers_title)
                    lst_without = [remove_outliers(arr) for arr in lst]
                res[letter_treatment[letter]] = [np.nanmean(l) for l in lst_without]
            elif self.how_to_plot == 'median':
                res[letter_treatment[letter]] = [np.nanmedian(l) for l in lst]
            elif self.how_to_plot == 'sum':
                res[letter_treatment[letter]] = [np.nansum(l) for l in lst]
        return res

    def show_save(self, save=False):
        fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(15, 6))
        axes.tick_params(labelsize=6)
        if self.type == 'plot':
            if self.time_jump > 1:
                data = define_time_jump(self.data, self.time_jump, self.how_to_plot)
            else:
                data = self.data
            if not hasattr(self, "df_by_treatment"):
                self.df_by_treatment = self.create_df_for_plot(data)
            lst = [self.df_by_treatment[col].values[self.start // self.time_jump:self.end // self.time_jump] for col
                   in self.treatments_to_plot]
            for j in range(len(self.treatments_to_plot)):
                try:
                    axes.plot(range(self.start, self.end-self.time_jump, self.time_jump), lst[j],
                                 label=self.treatments_to_plot[j], linewidth=1,
                                 color=self.colors[self.treatments_to_plot[j]])
                except:
                    axes.plot(range(self.start, self.end, self.time_jump), lst[j],
                                 label=self.treatments_to_plot[j], linewidth=1,
                                 color=self.colors[self.treatments_to_plot[j]])
                axes.tick_params(labelsize=self.time_size)
                leg = axes.legend(loc='upper right')
                leg_lines = leg.get_lines()
                leg_texts = leg.get_texts()
                plt.setp(leg_lines, linewidth=2)
                plt.setp(leg_texts, fontsize=self.legend_size)
        elif self.type == 'box':
            if not hasattr(self, "df_for_box"):
                self.df_for_box = self.create_df_for_box('bar and box')
            lst = self.output_df_box_n_create_lst('bar and box')
            lst = [[x for x in l if str(x) != 'nan'] for l in lst]
            axes.boxplot(lst, labels=self.treatments_to_plot)
            if self.kruskal and self.signature == self.get_signature():
                index = 1
                max_val = max([max(l) for l in lst])*0.9
                for t in self.treatments_to_plot:
                    axes.text(index, max_val, ''.join(self.groups_letter_without[t]), fontsize=self.groups_letter_size)
                    index += 1
        elif self.type == 'bar':
            if not hasattr(self, "df_for_box"):
                self.df_for_box = self.create_df_for_box('bar and box')
            lst = self.output_df_box_n_create_lst('bar and box')
            lst = [[x for x in l if str(x) != 'nan'] for l in lst]
            means = [np.nanmean(arr) for arr in lst]
            if self.std:
                std = [np.nanstd(arr) for arr in lst]
            else:
                std = [np.nanstd(arr)/(len(arr))**0.5 for arr in lst]
            axes.bar(self.treatments_to_plot, means, align='center', capsize=10, alpha=0.5)
            plotline, caplines, barlinecols = axes.errorbar(self.treatments_to_plot, means, yerr=std,
                                                               lolims=True, capsize=0, ls='None', color='k')
            caplines[0].set_marker('_')
            caplines[0].set_markersize(20)
            if self.kruskal and self.signature == self.get_signature():
                index = 0
                max_val = max([means[i]+std[i] for i in range(len(std))])*1.005
                for t in self.treatments_to_plot:
                    axes.text(index, max_val, ''.join(self.groups_letter_without[t]), fontsize=self.groups_letter_size)
                    index += 1
        elif self.type == 'bar_st':
            if not hasattr(self, "df_for_box"):
                self.df_for_box = self.create_df_for_box('z standard')
            if not hasattr(self, 'mean_t_first'):
                self.mean_t_first = np.nanmean(self.df_for_box[self.treatment])
                self.std_t_first = np.nanstd(self.df_for_box[self.treatment])
                self.df_for_box = self.df_for_box.drop([self.treatment], axis=1)
                self.df_for_box = (self.df_for_box - self.mean_t_first) / self.std_t_first
            if self.treatment in self.treatments_to_plot:
                self.treatments_to_plot.remove(self.treatment)
            lst = self.output_df_box_n_create_lst('z standard')
            lst = [[x for x in l if str(x) != 'nan'] for l in lst]
            means = [np.nanmean(arr) for arr in lst]
            if self.std:
                std = [np.nanstd(arr) for arr in lst]
            else:
                std = [np.nanstd(arr) / (len(arr))**0.5 for arr in lst]
            treatments = list(self.treatments_to_plot)
            if self.standard_type == 'bar':
                axes.bar(treatments, means, align='center', capsize=10, alpha=0.5)
                plotline, caplines, barlinecols = axes.errorbar(treatments, means, yerr=std, lolims=True, capsize=0,
                                                                ls='None', color='k')
                caplines[0].set_marker('_')
                caplines[0].set_markersize(20)
            else:
                axes.boxplot(lst, labels=self.treatments_to_plot)
        elif self.type == 'bar_st_percent' or self.type == 'bar_st_percent_reduction':
            if not hasattr(self, 't_mean_second'):
                self.t_mean_second = np.nanmean(self.df_for_box[self.treatment].values)
            if self.type == 'bar_st_percent_reduction':
                if self.treatment in self.df_for_box.columns:
                    self.df_for_box = self.df_for_box.drop(self.treatment, axis=1)
            df_name = "z standard(%)" + (' reduction' if self.type == 'bar_st_percent_reduction' else '')
            lst = self.output_df_box_n_create_lst(df_name)
            lst = [[x for x in l if str(x) != 'nan'] for l in lst]
            means = [np.nanmean(arr) / self.t_mean_second * 100 for arr in lst]
            if self.type == 'bar_st_percent_reduction':
                means = [100 - m for m in means]
            treatments = list(self.treatments_to_plot)
            axes.bar(treatments, means, align='center', capsize=10, alpha=0.5)

        if self.type != 'plot':
            for tick in axes.xaxis.get_major_ticks():
                tick.label.set_fontsize(self.groups_label_size)
        axes.set_title(self.title + ('\ntime jump = {0}'.format(self.time_jump) if
                                     (self.time_jump != 1 and self.type == 'plot') else ''), fontsize=self.title_size)
        axes.set_xlabel(self.x_label, fontsize=self.xlabel_size)
        axes.set_ylabel(self.y_label, fontsize=self.ylabel_size)
        if self.grid:
            axes.grid()

        if save:
            img_name = input('enter fig name: ')
            plt.savefig(self.dir_name_images + img_name + ".png")
        else:
            plt.show()
            # pass

    def change_title(self):
        self.title = input('enter new title: ')

    def change_x_label(self):
        self.x_label = input('enter new x label: ')

    def change_y_label(self):
        self.y_label = input('enter new y label: ')

    def change_start_time(self):
        m = '\n\nenter start time in the range 0 - {0}: '.format(self.end)
        self.start = get_input(self.end, m, -1) + 1

    def change_end_time(self):
        m = '\n\nenter end time in the range {0} - {1}: '.format(self.start, len(self.data))
        self.end = get_input(len(self.data), m, self.start) + 1

    def change_time_jump(self):
        max_time_jump = 200
        m = 'enter new time jump: '
        self.time_jump = get_input(max_time_jump, m) + 1

    def choose_treatments_and_order(self):
        print('\n'.join(['{0:<5} {1}'.format(i + 1, self.treatments_to_plot[i])
                         for i in range(len(self.treatments_to_plot))]))
        try:
            new_val = input('enter treatments you want to plot in order: ')
            new_val = [int(v)-1 for v in new_val.split()]
            self.treatments_to_plot = [self.treatments_to_plot[v] for v in new_val]
        except:
            print('bad input try again...')

    def change_treatment_name(self):
        while True:
            names = list(self.treatments_to_plot) + ['go back']
            m = '\nchoose name to change:\n' + '\n'.join(['{0:<5} {1}'.format(i + 1, names[i])
                                                        for i in range(len(names))])
            to_change = names[get_input(len(names), m)]
            if to_change == 'go back':
                break
            new_name = input('enter new name: ')
            self.data = self.data.rename(columns={to_change: new_name})
            self.treatments_to_plot = list(self.treatments_to_plot)
            self.treatments_to_plot[self.treatments_to_plot.index(to_change)] = new_name
            color = self.colors.pop(to_change)
            self.colors[new_name] = color
            self.treatment_letter[new_name] = self.treatment_letter[to_change]
            del self.treatment_letter[to_change]
            if hasattr(self, "df_by_treatment"):
               self.df_by_treatment = self.df_by_treatment.rename(columns={to_change: new_name})
            if hasattr(self, 'df_for_box'):
               self.df_for_box = self.df_for_box.rename(columns={to_change: new_name})

    def show_fig(self):
        self.show_save()

    def save_fig(self):
        self.show_save(save=True)

    def do_kruskal_wallis(self):
        self.kruskal_wallis()

    def change_line_color(self):
        self.choose_colors()

    def change_grid(self):
        self.grid = not self.grid

    def switch_between_standard_error_and_standard_deviation(self):
        inp = input('graph is currently with {0} want to switch?(y/n)'.format('standard deviation'
                                                                              if self.std else 'standrd error'))
        if inp == 'y':
            self.std = not self.std

    def edit(self):
        self.show_save()
        choices = ['change title', 'change x label', 'change y label', 'choose treatments and order',
                   'change treatment name', 'change font size']
        if self.type == 'plot':
            choices += ['change start time', 'change end time', 'change time jump']
        if self.type == "bar" or (self.type == "bar_st" and self.standard_type == 'bar'):
            choices += ['switch between standard error and standard deviation']
        choices += (['do kruskal wallis'] if (self.type == 'box' or self.type == 'bar') else []) +\
                   (['change line color'] if self.type == 'plot' else [])
        choices += ['change grid']
        choices += ['show fig', 'save fig']
        choices += ['finish edit']
        actions = '\n'.join(['{0:<5}{1}'.format(i + 1, choices[i]) for i in range(len(choices))])
        while True:
            m = '\nchoose action (enter number):\n' + actions + "\n"
            inp = get_input(len(choices), m)
            if inp == len(choices) - 1:
                break
            action = choices[inp].replace(' ', '_')
            getattr(self, action)()

    def choose_colors(self):
        print('\n\ncolors code\n' + str(Fig.colors))
        available = list(Fig.colors.keys())
        for t in self.treatments_to_plot:
            while True:
                inp = input(str(t) + ': ')
                if inp not in available:
                    print('wrong input or already picked color try again')
                else:
                    self.colors[t] = Fig.color_values[inp]
                    available.remove(inp)
                    break

    def kruskal_wallis(self):
        dir_name = self.dir_name_stats
        file_name = dir_name + 'kruskal wallis results 0'
        i = 0
        while True:
            if not (os.path.isfile(file_name)):
                f = open(file_name, 'w')
                break
            else:
                i += 1
                file_name = file_name[:-1] + str(i)
        lst_groups = [self.df_for_box[col].dropna().values for col in self.treatments_to_plot]
        k_w_res = stats.kruskal(*lst_groups)
        h_val, p_val = k_w_res
        f.write('h value = {0}\n'.format(h_val))
        f.write('p value = {0}\n'.format(p_val))
        print("\npreformed kruskal wallis test, results in stats -> kruskal_wallis_results " + str(i))
        self.signature = self.get_signature()
        if p_val < 0.05:
            print('the results are significant, preform post hoc tests? (y for yes)')
            # inp_krus = 'y'
            inp_krus = input()
            if inp_krus == 'y':
                post_hoc_df = sp.posthoc_dunn(lst_groups, p_adjust='holm')
                cols = post_hoc_df.columns
                post_hoc_df = post_hoc_df.rename(columns={cols[i]: self.treatments_to_plot[i]
                                                          for i in range(len(cols))})
                post_hoc_df = post_hoc_df.rename(index={cols[i]: self.treatments_to_plot[i]
                                                        for i in range(len(cols))})
                post_hoc_df.to_excel(dir_name + "post hoc res " + str(i) + '.xlsx')
                groups = {}
                critical_val = 0.05
                means = [np.nanmean(l) for l in lst_groups]
                keys = list(self.treatments_to_plot)
                keys_sorted = [x for _, x in sorted(zip(means, keys), reverse=True)]
                seen_groups = []
                for i in range(len(keys_sorted)):
                    g = keys_sorted[i]
                    seen_groups.append(g)
                    groups[g] = []
                    groups_to_check = list(set(keys_sorted)-set(seen_groups))
                    values = post_hoc_df[g][groups_to_check]
                    for col in values.index:
                        if values[col] > critical_val and col not in seen_groups:
                            groups[g].append(col)
                letters = {}
                c = 'a'
                seen_groups = []
                for k in keys_sorted:
                    if (len(groups[k]) > 0 and not already_contained(groups[k], letters)) or\
                            (len(groups[k]) == 0 and k not in seen_groups):
                        letters[c] = [k] + groups[k]
                        c = chr(ord(c)+1)
                        seen_groups += groups[k]
                groups_letter = {}
                for t in self.treatments_to_plot:
                    groups_letter[t] = [c for c in letters if t in letters[c]]

                print("\npreformed dunn test, results in stats -> post hoc res")
                print('treatments are in the same group if they are not statistically different (p val is more than 0.05)')
                print('\nshow results from post hoc test on graph? (y for yes)')

                f.write("results are significant!!\n\n")
                f.write('post hoc results (treatments are in the same group are not statistically different):\n')
                f.write("\n".join(["{0:<5s}:{1}".format(key, str(val)) for key, val in letters.items()]))
                inp = input()
                # inp = 'y'
                if inp == 'y':
                    self.groups_letter_without = groups_letter
                    self.kruskal = True

        else:
            print('results are not significant')
        f.close()

    def get_signature(self):
        return [self.treatments_to_plot, self.start, self.end]

    def output_df_box_n_create_lst(self, type_df):
        data_names = ['N', 'mean', 'median', 'std']
        data_for_col = []
        lst_for_graph = []
        for col in self.treatments_to_plot:
            vals = list(self.df_for_box[col].values)
            if self.remove_liars:
                mean, std = np.nanmean(vals), np.nanstd(vals)
                high, low = mean + 2*std, mean - 2*std
                vals = [v for v in vals if low <= v <= high]
            lst_for_graph.append(vals)
            data_for_col.append([len(vals), np.nanmean(vals), np.nanmedian(vals), np.nanstd(vals)])
        df_for_name = self.dir_name_stats + "df for {0} by {1}{2}{3}.xlsx".format(type_df, self.how_to_plot,
                                                                               ("" if self.remove_liars else
                                                                                ' with outliers'),
                                                                                ("" if self.remove_liars_over_time else
                                                                                 " with outliers in this time period"))
        if not os.path.isfile(df_for_name):
            df_to_output = self.df_for_box
            for i in range(len(data_for_col[0])):
                lst = [v[i] for v in data_for_col]
                df_to_output = df_to_output.append(pd.Series(lst, index=self.treatments_to_plot,
                                                                     name=data_names[i]))

            if self.remove_liars:
                df_to_output = df_to_output.style.apply(highlight_outliers,
                                                        subset=(df_to_output.index[0:len(df_to_output)-len(data_names)],
                                                                df_to_output.select_dtypes(float).columns))
            df_to_output.to_excel(df_for_name, engine='openpyxl')
            print('\n\ndf for {0} by {1} was saved in stats'.format(type_df, self.how_to_plot))
        return lst_for_graph

    def bar_by_percent(self, treatment):
        self.type = 'bar_st_percent'
        self.treatment = treatment
        self.title = 'Distance moved (%)'
        self.edit()

    def bar_percent_reduction(self, treatment):
        self.treatments_to_plot.remove(treatment)
        self.type = 'bar_st_percent_reduction'
        self.title = 'Distance moved reduction (%)'
        self.edit()

    def change_font_size(self):
        max_font_size = 40
        options = ['title', 'xlabel', 'ylabel'] + (['time', 'legend'] if self.type == 'plot' else ['groups label'])
        if self.kruskal:
            options += ['groups letter']
        options += ['go back']
        template = 'current size is {0} enter new size: '
        while True:
            m = 'which size you wish to change:\n' + '\n'.join(['{0:<5}{1}'.format(i+1, options[i]) for i in
                                                                range(len(options))])
            inp = options[get_input(len(options), m)]
            if inp == 'go back':
                return
            elif inp == 'title':
                self.title_size = get_input(max_font_size, template.format(self.title_size))+1
            elif inp == 'xlabel':
                self.xlabel_size = get_input(max_font_size, template.format(self.xlabel_size))+1
            elif inp == 'ylabel':
                self.ylabel_size = get_input(max_font_size, template.format(self.ylabel_size))+1
            elif inp == 'time':
                self.time_size = get_input(max_font_size, template.format(self.time_size))+1
            elif inp == 'groups label':
                self.groups_label_size = get_input(max_font_size, template.format(self.groups_label_size))+1
            elif inp == 'legend':
                self.legend_size = get_input(max_font_size, template.format(self.legend_size))+1
            elif inp == 'groups letter':
                self.groups_letter_size = get_input(max_font_size, template.format(self.groups_letter_size))+1








