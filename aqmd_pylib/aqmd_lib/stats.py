# -*- coding: utf-8 -*-
import numpy as np


####################################

def get_residuals(y_observed, y_predicted):
    if len(y_observed) != len(y_predicted):
        raise ValueError('Mismatched length for y_observed and y_predicted')
    y_o = np.asarray(y_observed)
    y_p = np.asarray(y_predicted)
    return y_o - y_p
