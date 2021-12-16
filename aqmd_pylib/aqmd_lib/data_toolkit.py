# -*- coding: utf-8 -*-
import os
from typing import Iterable

import pandas as pd
from pandas import DataFrame

from aqmd_lib import util


def list_getMaxLength(x):
    if not x:
        raise ValueError('List is empty')
    max_length = len(x[0])
    if len(x) > 1:
        for i in range(1, len(x)):
            max_length = max(max_length, len(x[i]))
    return max_length


def df_summarize(df):
    cols = list(df.columns)
    amt_idx = len(df.index.values)
    print('\nDataframe Summary:')
    print(util.tab(f'Amount of Columns:{len(cols)}'))
    print(util.tab(f'Amount of Rows:{amt_idx}'))
    print(util.tab('Column Labels:'))
    pad_amt = list_getMaxLength(cols)
    for i in cols:
        status = df[i].isnull().any()
        padded_i = i.ljust(pad_amt, ' ')
        print(util.tab(padded_i + f'  |=> Contains Null:{status}', 2))


def df_getColNames(df: DataFrame):
    return list(df.columns)


def df_i2label(df, idx):
    x = list(df.columns)
    return x[idx]


def df_str2dt(df: DataFrame, idx, strFormat, curr_tz=None,
              overwrite: bool = False, ambiguous='NaT', nonexistent='NaT') -> DataFrame:
    cpy = df.copy()
    idx = util.df_x2i(cpy, idx)
    newDT = pd.to_datetime(cpy.iloc[:, idx].copy(), errors='raise', format=strFormat)
    if '%z' not in strFormat:
        newDT = newDT.dt.tz_localize(
                tz=curr_tz, ambiguous=ambiguous, nonexistent=nonexistent
        )
    if overwrite:
        cpy.iloc[:, idx] = newDT
        cpy = cpy.rename(columns={str(df_i2label(cpy, idx)): f'datetime-{curr_tz}'})
    else:
        cpy.insert(idx + 1, f'datetime-{curr_tz}', newDT, allow_duplicates=True)
    return cpy


def df_switchCol(df: DataFrame, i, j):
    i = util.df_x2i(df, i)
    j = util.df_x2i(df, j)
    if i < j:
        x = i
        y = j
    else:
        x = j
        y = i
    names = df_getColNames(df)
    name_x = names[x]
    name_y = names[y]
    col_x = df.iloc[:, x]
    col_y = df.iloc[:, y]
    newDF = df.copy()

    newDF = newDF.drop(str(name_x))
    newDF = newDF.drop(str(name_y))
    newDF = newDF.insert(x, name_y, col_y)
    newDF = newDF.insert(y, name_x, col_x)
    return newDF


def df_decomposeDT(df: DataFrame, dtIdx, drop=False):
    i = util.df_x2i(df, dtIdx)
    DT = df.iloc[:, i]

    timezone = DT.dt.tz
    dayofweek = DT.dt.day_name()
    dayofyear = DT.dt.day
    week = DT.dt.isocalendar().week
    year = DT.dt.year
    month = DT.dt.month
    hour = DT.dt.hour
    minute = DT.dt.minute
    sec = DT.dt.second

    cpy = df.copy()
    if drop is True:
        cpy.drop(df_i2label(cpy, i), axis=1)
    cpy.insert(i + 1, 'week of year', week)
    cpy.insert(i + 1, 'dayofweek', dayofweek)
    if (sec != 0).all():
        cpy.insert(i + 1, 'seconds', sec)
    if (minute != 0).all():
        cpy.insert(i + 1, 'minute', minute)
    if (hour != 0).all():
        cpy.insert(i + 1, 'hour', hour)
    cpy.insert(i + 1, 'day', dayofyear)
    cpy.insert(i + 1, 'month', month)
    cpy.insert(i + 1, 'year', year)
    cpy.insert(i + 1, 'timezone', timezone)

    return cpy


def df_convertTZ(df: DataFrame, idx, new_tz='None', overwrite: bool = False,
                 ambiguous='NaT', nonexistent='NaT', newColName=None):
    cpy = df.copy()
    idx = util.df_x2i(df, idx)
    if newColName is None:
        newColName = f'datetime-{new_tz}'
    i = idx
    target = cpy.iloc[:, i].copy()
    if target.dt.tz is None:
        target = target.tz_localize(tz=new_tz, ambiguous=ambiguous, nonexistent=nonexistent)
    else:
        target = target.dt.tz_convert(new_tz)
    if overwrite:
        cpy.iloc[:, i] = target
        old_name = df_getColNames(cpy)[i]
        cpy.rename(columns={str(old_name): str(newColName)}, inplace=True)
    else:
        cpy.insert(i + 1, newColName, target, allow_duplicates=True)
    return cpy


def df_rename(df: DataFrame, idx, new_names):
    cpy = df.copy()
    idx = util.df_multix2i(df, idx)
    names = df_getColNames(cpy)
    new_names = util.enforceSeq(new_names)
    for i in nLoop(idx):
        x = names[i]
        y = new_names[i]
        cpy = cpy.rename(columns={
            str(x): str(y)
        })
    return cpy


def df_matchByIndex(df1: DataFrame, df2: DataFrame):
    mask = df1.index.intersection(df2.index)
    cpy1, cpy2 = df1[mask], df2[mask]
    return cpy1, cpy2


def df_mergeByCol(df1: DataFrame, df2: DataFrame, col1_idx, col2_idx, new_col_idx='left'):
    n1 = util.df_x2i(df1, col1_idx)
    n2 = util.df_x2i(df2, col2_idx)
    idx1 = df_i2label(df1, n1)
    idx2 = df_i2label(df2, n2)

    df1 = df1.set_label(str(idx1))
    df2 = df2.set_label(str(idx2))
    new_df = pd.merge(df1, df2, left_index=True, right_index=True)
    new_idx = new_df.index.values
    if new_col_idx == 'left':
        new_i = n1
        name = df_i2label(df1, n1)
        return new_df.insert(new_i, name, new_idx)
    elif new_col_idx == 'right':
        new_i = n2
        name = df_i2label(df2, n2)
        return new_df.insert(new_i, name, new_idx)
    elif new_col_idx == True:
        return new_df
    elif new_col_idx == None:
        return new_df.reset_index(drop=True)
    elif new_col_idx == False:
        return new_df.reset_index(drop=False)
    else:
        raise ValueError('incorrect value for new_col_idx')
