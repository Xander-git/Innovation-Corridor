# -*- coding: utf-8 -*-
#############################################
import pandas as pd

#############################################
def check_lengths(x: pd.DataFrame, y: pd.DataFrame, parent_function: str):
    if len(x) != len(y):
        raise ValueError(f"For {parent_function} x and y must be equal lengths")
    return


def enforce_y(y: pd.DataFrame, parent_function):
    if len(list(y.columns)) != 1:
        raise ValueError(f"For {parent_function} y must contain one and only one column")
    return


def enforce_xsingle(x: pd.DataFrame, parent_function):
    if len(x.columns) != 1:
        raise ValueError(f"For {parent_function} x may only contain a single column")
    return


def checkBasic_xy(x: pd.DataFrame, y: pd.DataFrame, parent_function: str):
    check_lengths(x, y, parent_function)
    enforce_y(y, parent_function)
    return


def check_2d(x: pd.DataFrame, y: pd.DataFrame, parent_function):
    check_lengths(x, y, parent_function)
    enforce_y(y, parent_function)
    enforce_xsingle(x, parent_function)
    return
