import os

import pandas as pd
from IPython.display import display

sys.path.append(r'C:\Users\Alex\Sync\dev\python\aqmd_module')
import aqmd.data_toolkit as dtk

import InnovCorridor_CodeKit as ic

##################################################
fpath_travelTime_csv = r'..\data\~originals\travel_time_csv'
tt_file_list = os.listdir(fpath_travelTime_csv)
for i in dtk.nLoop(tt_file_list):
    tt_file_list[i] = fpath_travelTime_csv + "\\" + tt_file_list[i]
test=ic.readTravelTimeCSV(tt_file_list[1])
data=pd.read_table(tt_file_list[1])
table_str = pd.read_table(tt_file_list[1], header=None)
data=table_str.copy()
data[0] = data[0].str.replace("  ", " ")
data[0] = data[0].str.replace(': ', ' ')
data = data[0].str.split(pat=' ', expand=True)
