from create_data import *
from yoni import *


def create_zeros_dir():
    home_dir = 'results from script'
    if not path.exists(home_dir):
        os.mkdir(home_dir)
    home_dir += '/zeros_data'
    if not path.exists(home_dir):
        os.mkdir(home_dir)
        os.mkdir(home_dir + '/files')
    return home_dir


def get_zeros_data(df):
    res_df = pd.DataFrame(columns=['longest in a row', 'start index', 'total zeros', 'percent zeros'])
    for col in df.columns:
        total_zeros = len(df[df[col] == 0])
        num_zeros_in_a_row = 0
        i = -1
        index = 0
        index_longest = 0
        longest_in_a_row = 0
        for val in df[col].values:
            i += 1
            if val == 0:
                if num_zeros_in_a_row == 0:
                    index = i
                num_zeros_in_a_row += 1
                if num_zeros_in_a_row > longest_in_a_row:
                    longest_in_a_row = num_zeros_in_a_row
                    index_longest = index
            elif val > 0:
                num_zeros_in_a_row = 0
        res_df = res_df.append(pd.Series([longest_in_a_row, index_longest, total_zeros, total_zeros/len(df)*100], index=res_df.columns),
                               ignore_index=True)
    res_df.index = df.columns
    return res_df


def create_zeros_data(file_name, dir_name):
    dir_name_files = dir_name + '/files'
    check_file_exist = file_name[:len(file_name)-5]
    try:
        results = pd.read_excel(dir_name_files + check_file_exist + '_all_fish.xlsx', index_col=False)
        results = results.drop(['Unnamed: 0'], axis=1)
    except:
        print('\n\nprocessing...')
        results, treatment_letter, treatments = make_df_ready(file_name)
        results.to_excel(dir_name_files + check_file_exist + '_all_fish.xlsx')
        with open(dir_name_files + check_file_exist + '_treatment_letter.pickle', 'wb') as handle:
            pickle.dump(treatment_letter, handle, protocol=pickle.HIGHEST_PROTOCOL)

    results = results[:len(results)-1]
    print('removed the last second!!')
    plt.hist([v for col in results.columns for v in results[col].values if v >= 0])
    plt.savefig(dir_name_files + check_file_exist + "_fig.png")
    return get_zeros_data(results)


def main():
    files = get_files()
    dir_name = create_zeros_dir()
    all_files = pd.DataFrame(columns=['file name', 'mean zeros in a row per fish', 'mean total zeros per fish',
                                      'mean percent zeros'])
    for file_name in files:
        df = create_zeros_data(file_name, dir_name)
        df.to_excel(dir_name + '/' + file_name + '.xlsx')
        all_files = all_files.append(pd.Series([file_name, df['longest in a row'].mean(), df['total zeros'].mean(),
                                                df['percent zeros'].mean()], index=all_files.columns),
                                     ignore_index=True)
    all_files.to_excel(dir_name + '/' + 'all files' + '.xlsx')


main()



