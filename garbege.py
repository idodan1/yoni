def get_treatments_to_plot(treatments):
    print("\n\nlet's plot the movement over time, choose treatments you would like to plot:")
    print("(if you want treatments 1,2 and 3 enter 1 2 3")
    print("\n".join([str(i+1)+" : " + treatments[i] for i in range(len(treatments))]))
    wrong = True
    treatments_to_plot = None
    while wrong:
        wrong = False
        treatments_to_plot = "1 2 3 4 5 6 7 8".split()
        # treatments_to_plot = input("enter one or more numbers in the range 1-{0}: ".format(len(treatments))).split()
        treatments_to_plot = [int(t) for t in treatments_to_plot]
        for t in treatments_to_plot:
            if t < 1 or t > len(treatments):
                print("input not in range, type again....\n")
                wrong = True
                break
    return treatments_to_plot


def plot_treatments(results, treatments_to_plot, treatments, start_time, end_time, dir_name):
    fig = plt.figure(figsize=(7, 5))
    for t in treatments_to_plot:
        treatment = treatments[t-1]
        plt.plot(range(start_time, end_time), results[treatment].values[start_time:end_time], label=treatment,
                 linewidth=1)
    plt.xticks(list(range(start_time, end_time, (end_time-start_time)//10)))
    plt.legend()
    plt.xlabel('times(sec)')
    plt.ylabel('total distance(mm)')
    leg = plt.legend()
    plt.title('distance moved over time')
    # get the lines and texts inside legend box
    leg_lines = leg.get_lines()
    leg_texts = leg.get_texts()
    # bulk-set the properties of all lines and texts
    plt.setp(leg_lines, linewidth=2)
    plt.setp(leg_texts, fontsize='medium')
    plt.show_save()


def get_times(times):
    start_time = 500
    # start_time = int(input("choose start time (a number between 0 to {0}): ".format(len(times))))
    end_time = 800
    # end_time = int(input("choose end time (a number between 0 to {0}): ".format(len(times))))
    return start_time, end_time


def plot_box_plot(results, start_time, end_time, dir_name):
    """add option to choose specific times"""
    lst = [results[col].values for col in results.columns]
    lst_without_outliers = []
    history = []
    for l in lst:
        l_without, outliers_history = remove_outliers(l)
        lst_without_outliers.append(l_without)
        history.append(outliers_history)
    report_outliers(results, history, results.columns, dir_name)
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(15, 6))
    axes[0].tick_params(labelsize=6)
    axes[0].boxplot(lst, labels=results.columns)
    axes[0].set_title("with outliers")
    axes[1].tick_params(labelsize=6)
    axes[1].boxplot(lst_without_outliers, labels=results.columns)
    axes[1].set_title("without outliers")
    kruskal_wallis(lst_without_outliers, dir_name)
    kruskal_wallis(lst, dir_name, with_outliers='with_outliers')
    plt.show_save()





# def save_fig(fig, dir_name):
#     des = input('\n\nwould you like to save this figure? press y for yes, any button for no: ')
#     if des == 'y':
#         fig.savefig(dir_name + 'fig'+str(fig_num))
#         print("fig saved in the name fig"+str(fig_num))