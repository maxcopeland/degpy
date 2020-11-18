import os

import pandas as pd
from degpy.session import Session


recordings = [
        {
            'sess_num': 'ps17',
            'path': '/Volumes/Backup Plus/data/080602/080602_ps17_160704/2016-07-04_13-22-47'
        },
        # {
        #     'sess_num': 'ps19',
        #     'path': '/Volumes/Backup Plus/data/080602/080602_ps19_160706/2016-07-06_13-38-43'
        # },
]



# def get_dataframe():
#
#     dfs = []
#
#     for rec in recordings:
#         sess = Session(rec['path'])
#         for file in os.listdir(rec['path']):
#             if 'LFP' in file:
#                 term = sess.get_terminal(file)
#                 data = term.get_dataframe()
#                 data['LFP'] = [file.split('.')[0]] * len(data)
#                 data['sess'] = [rec['sess_num']] * len(data)
#                 # if not df:
#                 #     df = data
#                 # else:
#                 dfs.append(data)
#
#     df = pd.concat(dfs)
#
#     return df


def write_data_to_csv():

    for rec in recordings:
        sess = Session(rec['path'])
        data = {}
        for file in os.listdir(rec['path']):
            if 'LFP' in file:
                term = sess.get_terminal(file)
                signal = term.data
                lfp_name = file.split('.')[0]
                data[lfp_name] = signal

        data['target'] = term.target

    df = pd.DataFrame(data)

    df.to_csv('{}_data.csv'.format(rec['sess_num']))

    return df


def main():

    write_data_to_csv()



if __name__ == "__main__":
    main()
