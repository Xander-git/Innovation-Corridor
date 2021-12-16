# -*- coding: utf-8 -*-
import os
from collections import Sequence
from typing import Tuple

import numpy as np
import pandas as pd
from pandas import DataFrame
from playsound import playsound


def nLoop(x):
    return range(len(x))


def tab(x: str, n_times=1, tab_length=4):
    tab = ''
    for i in range(tab_length):
        tab = tab + ' '
    for i in range(n_times):
        x = tab + x
    return x


def df_x2i(df: DataFrame, x):
    if type(x) is int:
        return x
    elif type(x) is str:
        names = list(df.columns)
        x = names.index(x)
        return x
    else:
        raise ValueError('Unsupported type for indexing')


def df_multix2i(df: DataFrame, x) -> Tuple:
    if isinstance(x, Sequence):
        y = []
        for i in nLoop(x):
            y.append(df_x2i(df, x))
        return tuple(y)
    else:
        y = df_x2i(df, x)
        return tuple(y)


def enforceSeq(x) -> Sequence:
    if isinstance(x, Sequence):
        return x
    else:
        return [x]


def csv_folder2table(folder_path, **kwargs):
    file_list = os.listdir(folder_path)
    if not file_list:
        raise ValueError("Folder is empty")
    else:
        table = pd.read_csv(os.path.join(folder_path, file_list[0]), **kwargs)
        if len(file_list) == 1:
            return table
        else:
            for i in range(1, len(file_list)):
                new_table = pd.read_csv(os.path.join(folder_path, file_list[i]), **kwargs)
                table = pd.concat([table, new_table], axis=0, ignore_index=True)
            return table


def excel_folder2table(folder_path, sheet_name, axis=0, header=0, index_col=None, usecols=None, ignore_index=False):
    file_list = os.listdir(folder_path)
    if not file_list:
        raise ValueError("Folder is empty")
    else:
        table = pd.read_excel(os.path.join(folder_path, file_list[0]), sheet_name=sheet_name, header=header,
                              index_col=index_col, usecols=usecols)
        if len(file_list) == 1:
            return table
        else:
            for i in range(1, len(file_list)):
                new_table = pd.read_excel(os.path.join(folder_path, file_list[i]), sheet_name=sheet_name, header=header,
                                          index_col=index_col, usecols=usecols)
                table = pd.concat([table, new_table], axis=axis, ignore_index=ignore_index)
            return table


def play_alertTone():
    playsound('./resources/sfx/alert_tone_1.mp3')
