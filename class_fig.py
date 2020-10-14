import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.cm as cm
from scipy import stats
import scikit_posthocs as sp
import os
from os import path


def get_input(end, message, start=1):
    print(message)
    val = input()
    if val.isdigit():
        val = int(val)
        if start <= val <= end:
            return val-1
    print('wrong input try again...\n')
    return get_input(end, message)


def define_time_jump(results, time_jump):
    results_jump = pd.DataFrame(columns=results.columns)
    for i in range(0, len(results)//time_jump):
        results_jump = results_jump.append(pd.Series(list(results[i*time_jump:(i+1)*time_jump].mean().values),
                                                     index=results_jump.columns), ignore_index=True)
    if len(results)//time_jump != len(results)/time_jump:
        results_jump = results_jump.append(pd.Series(list(results[len(results)//time_jump * time_jump:
                                                                  (len(results)//time_jump + 1) * time_jump]
                                                          .mean().values), index=results_jump.columns),
                                           ignore_index=True)
    return results_jump


def already_exist(g1, g2, dic):
    for val in dic.values():
        if g1 in val and g2 in val:
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

    def __init__(self, data, data_outliers, x_label, y_label, title, g_type, start, end, dir_name, treatment=""):
        self.data = data
        self.data_outliers = data_outliers
        self.treatments_to_plot = data.columns
        self.x_label = x_label
        self.y_label = y_label
        self.title = title
        self.type = g_type
        self.start = start
        self.end = end
        self.dir_name_images = dir_name + 'images/'
        self.dir_name_stats = dir_name + 'stats/'
        self.time_jump = 1
        self.treatment = treatment
        self.colors = {self.treatments_to_plot[i]: Fig.col_val[i] for i in range(len(self.treatments_to_plot))}
        self.kruskal = False
        self.groups_letter_without = []
        self.groups_letter_with = []
        self.signature = self.get_signature()
        self.grid = True

    def show_save(self, save=False):
        if self.time_jump > 1:
            data = [define_time_jump(self.data, self.time_jump), define_time_jump(self.data_outliers, self.time_jump)]
        else:
            data = [self.data, self.data_outliers]
        fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(15, 6))
        for i in range(len(data)):
            lst = [data[i][col].values[self.start//self.time_jump:self.end//self.time_jump]
                   for col in self.treatments_to_plot]
            max_val = max([max(l) for l in lst]) * 0.9
            axes[i].tick_params(labelsize=6)
            if self.type == 'plot':
                for j in range(len(self.treatments_to_plot)):
                    try:
                        axes[i].plot(range(self.start, self.end-self.time_jump, self.time_jump), lst[j],
                                     label=self.treatments_to_plot[j], linewidth=1,
                                     color=self.colors[self.treatments_to_plot[j]])
                    except:
                        axes[i].plot(range(self.start, self.end, self.time_jump), lst[j],
                                     label=self.treatments_to_plot[j], linewidth=1,
                                     color=self.colors[self.treatments_to_plot[j]])
                    leg = axes[i].legend()
                    leg_lines = leg.get_lines()
                    leg_texts = leg.get_texts()
                    plt.setp(leg_lines, linewidth=2)
                    plt.setp(leg_texts, fontsize='medium')
            elif self.type == 'box':
                axes[i].boxplot(lst, labels=self.treatments_to_plot)
                if self.kruskal and self.signature == self.get_signature():
                    index = 1
                    for t in self.treatments_to_plot:
                        if i == 0:
                            axes[i].text(index, max_val, ''.join(self.groups_letter_without[t]))
                        else:
                            axes[i].text(index, max_val, ''.join(self.groups_letter_with[t]))
                        index += 1
            elif self.type == 'bar':
                means = [np.mean(arr) for arr in lst]
                std = [np.std(arr) for arr in lst]
                # std = [tuple([0]*len(std)), std]
                axes[i].bar(self.treatments_to_plot, means, align='center', capsize=10, alpha=0.5)
                plotline, caplines, barlinecols = axes[i].errorbar(self.treatments_to_plot, means, yerr=std,
                                                                   lolims=True, capsize=0, ls='None', color='k')
                caplines[0].set_marker('_')
                caplines[0].set_markersize(20)
            elif self.type == 'bar_st':
                t_mean = data[i][self.treatment].values[self.start:self.end].mean()
                means = [np.mean(arr)/t_mean * 100 for arr in lst]
                axes[i].bar(self.treatments_to_plot, means)
            elif self.type == 'bar_st_red':
                t_mean = data[i][self.treatment].values[self.start:self.end].mean()
                means = [np.mean(arr)/t_mean * 100 for arr in lst if np.mean(arr) != t_mean]
                means = [100-m for m in means]
                self.treatments_to_plot = [s for s in self.treatments_to_plot if s != self.treatment]
                axes[i].bar(self.treatments_to_plot, means)
            times = ''
            if self.type != 'plot' and self.end - self.start != len(data[i]):
                times = '\nstart time = {0}, end time = {1}'.format(self.start, self.end)
            axes[i].set_title(self.title + (' with outliers' if i == 1 else '') + ('\ntime jump = {0}'.format
                                                                                   (self.time_jump) if self.time_jump
                                                                                   != 1 else '') + (times if self.type
                                                                                   != 'plot' else ''))
            axes[i].set_xlabel(self.x_label)
            axes[i].set_ylabel(self.y_label)
            if self.grid:
                axes[i].grid()

        if save:
            plt.savefig(self.dir_name_images + input('enter fig name: '))
        else:
            plt.show()

    def change_title(self):
        self.title = input('enter new title: ')

    def change_x_label(self):
        self.x_label = input('enter new x label: ')

    def change_y_label(self):
        self.y_label = input('enter new y label: ')

    def change_start_time(self):
        m = 'enter new start time in the range 0 - {0}: '.format(self.end)
        self.start = get_input(self.end, m) + 1

    def change_end_time(self):
        m = 'enter new end time in the range {0} - {1}: '.format(self.start, len(self.data))
        self.end = get_input(self.end, m, self.start) + 1

    def change_time_jump(self):
        m = 'enter new time jump'
        self.time_jump = get_input(200, m) + 1

    def choose_treatments_and_order(self):
        print('\n'.join(['{0:<5} {1}'.format(i + 1, self.treatments_to_plot[i])
                         for i in range(len(self.treatments_to_plot))]))
        try:
            new_val = input('enter treatments you want to plot in order')
            new_val = [int(v) for v in new_val.split()]
            self.treatments_to_plot = [self.treatments_to_plot[v - 1] for v in new_val]
        except:
            print('bad input try again...')

    def change_treatment_name(self):
        m = 'choose name to change:\n' + '\n'.join(['{0:<5} {1}'.format(i + 1, self.treatments_to_plot[i])
                                                    for i in range(len(self.treatments_to_plot))])
        to_change = self.treatments_to_plot[get_input(len(self.treatments_to_plot), m)]
        new_name = input('enter new name: ')
        self.data = self.data.rename(columns={to_change: new_name})
        self.data_outliers = self.data_outliers.rename(columns={to_change: new_name})
        self.treatments_to_plot = list(self.treatments_to_plot)
        self.treatments_to_plot[self.treatments_to_plot.index(to_change)] = new_name
        color = self.colors.pop(to_change)
        self.colors[new_name] = color

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

    def edit(self):
        self.show_save()
        choices = ['change title', 'change x label', 'change y label', 'change start time', 'change end time',
                   'change time jump', 'choose treatments and order', 'change treatment name']
        choices += (['do kruskal wallis'] if self.type == 'box' else []) + (['change line color'] if self.type == 'plot'
                                                                            else [])
        choices += ['change grid']
        choices += ['show fig', 'save fig']
        choices += ['finish edit']
        actions = '\n'.join(['{0:<5}{1}'.format(i + 1, choices[i]) for i in range(len(choices))])
        while True:
            m = '\nchoose action (enter number):\n' + actions + "\n"
            inp = get_input(len(actions), m)
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
        if self.time_jump > 1:
            data = [define_time_jump(self.data, self.time_jump), define_time_jump(self.data_outliers, self.time_jump)]
        else:
            data = [self.data, self.data_outliers]
        for i in range(len(data)):
            dir_name = self.dir_name_stats + '/' + ' '.join([t for t in self.treatments_to_plot]) +\
                       ' time jump={0}'.format(self.time_jump)
            if not path.exists(dir_name):
                os.mkdir(dir_name)
            dir_name += '/'
            with_outliers = '' if i == 0 else ' with outliers'
            f = open(dir_name + 'kruskal_wallis_results' + with_outliers, 'w')
            lst_groups = [data[i][col].values[self.start // self.time_jump:self.end // self.time_jump]
                          for col in self.treatments_to_plot]
            k_w_res = stats.kruskal(*lst_groups)
            h_val, p_val = k_w_res
            f.write('h value = {0}\n'.format(h_val))
            f.write('p value = {0}\n'.format(p_val))
            f.write('post hoc results:\n')
            if i == 0:
                print("\npreformed kruskal wallis test, results in kruskal_wallis_results")
            if p_val < 0.05:
                if i == 0:
                    print('the results are significant, preform post hoc tests? (y for yes)')
                    inp_krus = input()
                if inp_krus == 'y':
                    post_hoc_df = sp.posthoc_dunn(lst_groups, p_adjust='holm')
                    cols = post_hoc_df.columns
                    post_hoc_df = post_hoc_df.rename(columns={cols[i]: self.treatments_to_plot[i]
                                                              for i in range(len(cols))})
                    post_hoc_df = post_hoc_df.rename(index={cols[i]: self.treatments_to_plot[i]
                                                              for i in range(len(cols))})
                    post_hoc_df.to_excel(dir_name + "post_hoc_res"+with_outliers+'.xlsx')
                    groups = {}
                    critical_val = 0.05
                    for k in range(len(self.treatments_to_plot)):
                        t = self.treatments_to_plot[k]
                        groups[t] = []
                        values = post_hoc_df[t].values[k+1:]
                        for j in range(len(values)):
                            if values[j] > critical_val and not already_exist(t, self.treatments_to_plot[k+1+j], groups):
                                groups[t].append(self.treatments_to_plot[k+1+j])
                    letters = {}
                    means = [np.mean(l) for l in lst_groups]
                    keys = list(groups.keys())
                    keys_sorted = [x for _, x in sorted(zip(means, keys), reverse=True)]
                    c = 'a'
                    seen_groups = []
                    for k in keys_sorted:
                        if len(groups[k]) > 0 or k not in seen_groups:
                            letters[c] = [k] + groups[k]
                            c = chr(ord(c)+1)
                            seen_groups += groups[k]
                    groups_letter = {}
                    for t in self.treatments_to_plot:
                        groups_letter[t] = [c for c in letters if t in letters[c]]
                    self.signature = self.get_signature()
                    if i == 0:
                        print("\npreformed dunn test, results in post_hoc_res")
                        print('treatments are in the same group if they had significant correlation (less than 0.05)')
                        print('show results from post hoc test on graph? (y for yes)')
                        inp = input()
                    if inp == 'y':
                        if i == 0:
                            self.groups_letter_without = groups_letter
                            self.kruskal = True
                        else:
                            self.groups_letter_with = groups_letter
                            self.show_save()

            else:
                print('results are not significant')
            f.close()

    def get_signature(self):
        return [self.treatments_to_plot, self.start, self.end, self.time_jump]







