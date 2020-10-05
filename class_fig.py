import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.cm as cm
plt.rcParams['axes.grid'] = True

colors = {'p': 'purple', 'b': 'blue', 'c': 'cyan', 'g': 'green', 'y': 'yellow', 'o': 'orange', 'r': 'red'}


def get_input(end, message):
    print(message)
    val = input()
    if val.isdigit():
        val = int(val)
        if 1 <= val <= end:
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


class Fig:
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
        self.dir_name = dir_name + 'images/'
        self.time_jump = 1
        self.treatment = treatment
        self.colors = cm.rainbow(np.linspace(0, 1, len(self.treatments_to_plot)))

    def show_save(self, save=False):
        if self.time_jump > 1:
            data = [define_time_jump(self.data, self.time_jump), define_time_jump(self.data_outliers, self.time_jump)]
        else:
            data = [self.data, self.data_outliers]
        fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(15, 6))
        for i in range(len(data)):
            lst = [data[i][col].values[self.start//self.time_jump:self.end//self.time_jump]
                   for col in self.treatments_to_plot]
            axes[i].tick_params(labelsize=6)
            if self.type == 'plot':
                for j in range(len(self.treatments_to_plot)):
                    axes[i].plot(range(self.start, self.end-(self.time_jump if self.time_jump != 1 else 0),
                                       self.time_jump), lst[j], label=self.treatments_to_plot[j], linewidth=1,
                                 color=self.colors[j])
                    leg = axes[i].legend()
                    leg_lines = leg.get_lines()
                    leg_texts = leg.get_texts()
                    plt.setp(leg_lines, linewidth=2)
                    plt.setp(leg_texts, fontsize='medium')
            elif self.type == 'box':
                axes[i].boxplot(lst, labels=self.treatments_to_plot)
            elif self.type == 'bar':
                means = [np.mean(arr) for arr in lst]
                axes[i].bar(self.treatments_to_plot, means)
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
            axes[i].set_title(self.title + (' with outliers' if i == 1 else '') + ('\ntime jump = {0}'.format
                                                                                   (self.time_jump) if self.time_jump
                                                                                   != 1 else ''))
            axes[i].set_xlabel(self.x_label)
            axes[i].set_ylabel(self.y_label)

        if save:
            plt.savefig(self.dir_name + input('enter fig name: '))
        else:
            plt.show()

    def edit(self):
        self.show_save()
        choices_val = ['change title', 'change x label', 'change y label', 'change start time', 'change end time',
                       'change time jump']
        choices_multiple_val = ['choose treatments and order']
        special_val = ['change line color', 'change treatment name', 'show fig', 'save fig', 'finish edit']
        choices = choices_val + choices_multiple_val + special_val
        attribute = ['title', 'x_label', 'y_label', 'start', 'end', 'time_jump']
        actions = '\n'.join(['{0:<5}{1}'.format(i + 1, choices[i]) for i in range(len(choices))])
        while True:
            m = '\nchoose action (enter number):\n' + actions + "\n"
            inp = get_input(len(actions), m)
            if inp < len(choices_val):
                new_val = input('enter new {0}: '.format(attribute[inp]))
                if new_val.isdigit():
                    new_val = int(new_val)
                setattr(self, attribute[inp], new_val)
            elif inp < len(choices_val) + len(choices_multiple_val):
                print('\n'.join(['{0:<5} {1}'.format(i + 1, self.treatments_to_plot[i])
                                 for i in range(len(self.treatments_to_plot))]))
                try:
                    new_val = input('enter treatments you want to plot in order')
                    new_val = [int(v) for v in new_val.split()]
                    self.treatments_to_plot = [self.treatments_to_plot[v - 1] for v in new_val]
                except:
                    print('bad input try again...')
            elif inp == len(choices)-4:
                m = 'choose name to change:\n' + '\n'.join(['{0:<5} {1}'.format(i + 1, self.treatments_to_plot[i])
                                                            for i in range(len(self.treatments_to_plot))])
                to_change = self.treatments_to_plot[get_input(len(self.treatments_to_plot), m)]
                new_name = input('enter new name: ')
                self.data = self.data.rename(columns={to_change: new_name})
                self.data_outliers = self.data.rename(columns={to_change: new_name})
                self.treatments_to_plot = list(self.treatments_to_plot)
                self.treatments_to_plot[self.treatments_to_plot.index(to_change)] = new_name
            elif inp == len(choices)-3:
                self.show_save()
            elif inp == len(choices)-2:
                self.show_save(save=True)
            elif inp == len(choices)-1:
                break









