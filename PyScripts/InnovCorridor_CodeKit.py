# -*- coding: utf-8 -*-
##########################
import sys
import os

import pandas as pd
from pandas import DataFrame

from aqmd_lib.util import nLoop
from aqmd_lib import data_toolkit as dtk, util
from aqmd_lib.sub_modules import test_settings as ts, error_code

##########################
datapath_main = '../data/'
datapath_gridsmart_excel = datapath_main + 'GridsmartNew\\codeFriendlyGridSmartData.xlsx'
datapath_clarity_excel = datapath_main + 'SensorDataNew\\HighRes\\IC-HighRes-2020-12-09-to-2021-06-05.xlsx'
datapath_meteorology_csv = datapath_main + 'WeatherData\\HighRes_WeatherData.csv'
datapath_travelTime_csv = datapath_main + 'TravelTimeNew\\TraveltimeDataCollectedZW - Copy.csv\\'
datapath_db = datapath_main + 'innov_corridor.db'
datapath_metadata = datapath_main + 'metadata\\metadata.xlsx'


##########################
class carb:
    def __init__(self, data: DataFrame, value_name: str):
        self._value_name = value_name
        self._rawData = data
        self._data = self._rawData[['date', 'start_hour', 'value']].dropna()
        self._data['datetime'] = self._data['date'].astype(str) + ' ' + \
                                 self._data['start_hour'].astype(int).astype(str).str.pad(2, fillchar='0')
        self._data = dtk.df_str2dt(self._data, 'datetime', '%Y-%m-%d %H', curr_tz='America/Los_Angeles', overwrite=True)
        self._data.rename(columns={'value': str(self._value_name)}, inplace=True)
        self._data.dropna(inplace=True)
        self._data.set_index('datetime-America/Los_Angeles', inplace=True, drop=True)
        self._data = self._data[[str(self._value_name)]]
        self._data = self._data.sort_index()

    def get_data(self):
        return self._data

    def get_rawData(self):
        return self._rawData


class carb_PM25(carb):
    def __init__(self, data: DataFrame):
        super().__init__(data, 'Background PM2.5 [ug/m3]')


class carb_NO2(carb):
    def __init__(self, data: DataFrame):
        super().__init__(data,'Background NO2 [ppm]')
        self._data['Background NO2 [ppm]']=self._data['Background NO2 [ppm]']*1000
        self._data.rename(columns={'Background NO2 [ppm]':'Background NO2 [ppb]'},inplace=True)


class clarity_historical:
    _metadata = pd.read_excel(io=datapath_metadata,
                              sheet_name='ClaritySensors',
                              header=0)
    _cols = dtk.df_getColNames(_metadata)
    _nodes = list(_metadata['sensorID'])

    def __init__(self, df: DataFrame):
        self._rawData = df
        self._data = None
        self._process()

    def _nodeMapper(self, x, output):
        i = self._nodes.index(str(x))
        j = self._cols.index(str(output))
        return self._metadata.iloc[i, j]

    def _process(self):
        self._data = self._rawData.copy()
        self._data = self._data[self._data['Site ID'] != 'AQ7GDKW8']
        self._data = self._data[self._data['Site ID'] != 'AXD4VGR2']
        self._data.rename(columns={
            'Site ID'                                                 : "Device ID",
            "Particulate Matter (2.5) Mass Concentration - Calibrated": "PM2.5 Highest Resolution Mass Concentration "
                                                                        "Calibrated [ug/m3]",
            'Relative Humidity'                                       : 'Rel. Humidity '
                                                                        'Internal Highest '
                                                                        'Resolution [%]',
            'Temperature'                                             : 'Temperature Internal '
                                                                        'Highest Resolution ['
                                                                        'degC]'
        },
            inplace=True)
        self._data = self._data[['Device ID',
                                 'Date',
                                 'PM2.5 Highest Resolution Mass Concentration Calibrated [ug/m3]',
                                 'Rel. Humidity Internal Highest Resolution [%]',
                                 'Temperature Internal Highest Resolution [degC]']]
        self._data = dtk.df_str2dt(self._data, 'Date', '%m/%d/%Y %H:%M', curr_tz='America/Los_Angeles',
                                   ambiguous='infer', nonexistent='NaT')
        self._data = self._data[pd.notnull(self._data['datetime-America/Los_Angeles'])]
        self._data.set_index('datetime-America/Los_Angeles', drop=True, inplace=True)
        self._data.sort_index(inplace=True)
        sensor_name = self._data['Device ID'].apply(lambda x: self._nodeMapper(x, 'nickname'))
        cross_streets = self._data['Device ID'].apply(lambda x: self._nodeMapper(x, 'Cross Streets'))
        self._data.insert(0, 'Sensor Name', sensor_name)
        self._data.insert(1, 'Intersection', cross_streets)
        self._data['Latitude'] = self._data['Device ID'].apply(lambda x: self._nodeMapper(x, 'Latitude'))
        self._data['Longitude'] = self._data['Device ID'].apply(lambda x: self._nodeMapper(x, 'Longitude'))

    def get_data(self):
        return self._data.copy()

    def get_PM25(self):
        data = self._data[['Sensor Name',
                           'Intersection',
                           'Device ID',
                           'PM2.5 Highest Resolution Mass Concentration Calibrated [ug/m3]',
                           'Temperature Internal Highest Resolution [degC]',
                           'Rel. Humidity Internal Highest Resolution [%]', 'Latitude', 'Longitude']].copy()
        data.dropna(inplace=True)
        return data

    def get_rawData(self):
        return self._rawData.copy()


class clarity_original:
    _metadata = pd.read_excel(io=datapath_metadata,
                              sheet_name='ClaritySensors',
                              header=0)
    _cols = dtk.df_getColNames(_metadata)
    _nodes = list(_metadata['sensorID'])

    def __init__(self, df: DataFrame):
        self._rawData = df
        self._data = None
        self._process()

    def _process(self):
        self._data = self._rawData.copy()
        self._data = self._data[[
            'Device ID',
            'Time [UTC+00:00]',
            'PM2.5 Highest Resolution Mass Concentration Calibrated [ug/m3]',
            'NO2 Highest Resolution Concentration Calibrated [ppb]',
            'Temperature Internal Highest Resolution [degC]',
            'Rel. Humidity Internal Highest Resolution [%]'
        ]]
        label_nodeID = dtk.df_i2label(self._rawData, 0)
        self._data = dtk.df_str2dt(self._data, 'Time [UTC+00:00]', '%Y-%m-%dT%H:%M:%S.%fZ', 'UTC', overwrite=True)
        self._data = dtk.df_convertTZ(self._data, 'datetime-UTC', new_tz='America/Los_Angeles')
        self._data = self._data.set_index('datetime-America/Los_Angeles', drop=True)
        self._data = self._data.sort_index()
        nodeID = self._data[label_nodeID]
        sensor_name = nodeID.apply(lambda x: self._nodeMapper(x, 'nickname'))
        cross_streets = nodeID.apply(lambda x: self._nodeMapper(x, 'Cross Streets'))
        lat = nodeID.apply(lambda x: self._nodeMapper(x, 'Latitude'))
        long = nodeID.apply(lambda x: self._nodeMapper(x, 'Longitude'))
        self._data.insert(0, 'Sensor Name', sensor_name)
        self._data.insert(1, 'Intersection', cross_streets)
        self._data['Latitude'] = lat
        self._data['Longitude'] = long
        return

    def _nodeMapper(self, x, output):
        i = self._nodes.index(str(x))
        j = self._cols.index(str(output))
        return self._metadata.iloc[i, j]

    def get_PM25(self):
        data = self._data
        extract = data[[
            'Sensor Name',
            'Intersection',
            'Device ID',
            'PM2.5 Highest Resolution Mass Concentration Calibrated [ug/m3]',
            'Temperature Internal Highest Resolution [degC]',
            'Rel. Humidity Internal Highest Resolution [%]',
            'Latitude',
            'Longitude'
        ]].copy()
        extract.dropna(inplace=True)
        return extract

    def get_data(self):
        return self._data.copy()

    def get_rawData(self):
        return self._rawData.copy()


class travel_time:
    _metadata = pd.read_excel(io=datapath_metadata,
                              sheet_name='TravelPaths',
                              header=0)

    def __init__(self, df: DataFrame, str_format="%Y-%m-%d %H:%M"):
        if ts.print_data:
            print(df)
        self._str_format = str_format
        self._rawData = df
        self._rawData = self._rawData.dropna(axis=1)
        self._data = dtk.df_str2dt(self._rawData, 'DT', self._str_format, curr_tz='America/Los_Angeles', overwrite=True)
        if ts.print_data:
            print(self._data)
        self._data = self._data.set_index('datetime-America/Los_Angeles')
        self._data = self._data.astype(int)

        if ts.print_data:
            print(self._data)
            print(self._metadata)
        cols = dtk.df_getColNames(self._data)
        for i in nLoop(cols):
            j = self._metadata.set_index('Name').index.get_loc(cols[i])
            dist = self._metadata.loc[j, 'Distance(m)']
            dist = dist/1609.344
            self._data.iloc[:, i] = self._data.iloc[:, i]/60  # sec to min
            self._data.iloc[:, i] = self._data.iloc[:, i]/60  # min to hr
            self._data.iloc[:, i] = dist/self._data.iloc[:, i]
        self._data = self._data.rename(columns=lambda x: x + ' (mph)')
        self._data.dropna(axis=1, inplace=True)
        return

    def get_data(self):
        return self._data.copy()


class OpenWeather:
    def __init__(self, df: DataFrame):
        self._rawData = df
        self._data = None
        self._process()

    def _process(self):
        self._data = self._rawData
        self._data['dt'] = pd.to_datetime(arg=self._data['dt'], utc=True, unit='s')
        self._data.rename(columns={
            'dt': 'datetime-UTC'
        }, inplace=True)
        self._data = dtk.df_convertTZ(self._data, 'datetime-UTC', new_tz='America/Los_Angeles')
        self._data.set_index('datetime-America/Los_Angeles', drop=True, inplace=True)

    def get_fullData(self):
        return self._data

    def get_rawData(self):
        return self._rawData

    def get_data(self):
        extract = self._data[
            ['temp',
             'pressure',
             'humidity',
             'wind_speed',
             'wind_deg', ]]
        return extract


class GridSmart_csv:
    def __init__(self, data: DataFrame):
        self._rawData = data
        self._data = self._processor(self._rawData)

    def _processor(self, data: DataFrame):
        date = data.iloc[3, 3]
        newData = data.iloc[14:, :]
        newData = newData.iloc[:-1, :]
        newData.dropna(axis=1, how='all', inplace=True)
        cols = ['time', 'Northbound', 'Eastbound', 'Southbound', 'Westbound', 'Total']
        newData.columns = cols
        newData.insert(0, 'date', date)
        dt = newData.loc[:, 'date'] + ' ' + newData.loc[:, 'time']
        newData.insert(0, 'datetime', dt)
        newData = dtk.df_str2dt(newData, 'datetime', '%m/%d/%Y %H:%M', curr_tz='America/Los_Angeles', overwrite=True)
        newData.drop(columns=['date', 'time', 'Northbound', 'Southbound', 'Total'], inplace=True)
        newData.dropna(inplace=True)
        newData.set_index('datetime-America/Los_Angeles', inplace=True)
        newData = newData.astype(int)
        return newData

    def add_data(self, data: DataFrame):
        table = self._processor(data)
        self._data = pd.concat([self._data, table])

    def get_data(self):
        return self._data.copy()


class historical_no2:
    _metadata = pd.read_excel(io=datapath_metadata,
                              sheet_name='ClaritySensors',
                              header=0)
    _cols = dtk.df_getColNames(_metadata)
    _nodes = list(_metadata['sensorID'])

    def _nodeMapper(self, x, output):
        i = self._nodes.index(str(x))
        j = self._cols.index(str(output))
        return self._metadata.iloc[i, j]

    def __init__(self, data: DataFrame):
        self._rawData = data
        self._data = self._rawData.copy()
        self._data = self._data[self._data['Site ID'] != 'AQ7GDKW8']
        self._data = self._data[self._data['Site ID'] != 'AXD4VGR2']
        self._data = self._data.loc[:, ['Date', 'Site ID', 'Nitrogen Dioxide']]
        self._data.rename(columns={'Nitrogen Dioxide':'Nitrogen Dioxide [ppb]'},inplace=True)
        self._data = dtk.df_str2dt(self._data, 'Date', '%Y-%m-%d %H:%M:%S', curr_tz='UTC', overwrite=True)
        self._data = dtk.df_convertTZ(self._data, 'datetime-UTC', new_tz='America/Los_Angeles', overwrite=True,
                                      newColName='datetime-America/Los_Angeles')
        sensor_name = self._data.loc[:, 'Site ID'].apply(lambda x: self._nodeMapper(x, 'nickname'))
        self._data.insert(1, 'Sensor Name', sensor_name)
        self._data.set_index('datetime-America/Los_Angeles', inplace=True)

    def get_data(self):
        return self._data.copy()


class GridSmart:
    def __init__(self, data: DataFrame):
        self._rawData = data
        self._data = data.copy()
        timeStr = self._data['Date'] + ' ' + self._data['Time']
        self._data.drop(columns=['Date', 'Time'], inplace=True)
        self._data.insert(1, 'datetime', timeStr)
        self._data = dtk.df_str2dt(self._data, 'datetime', '%Y-%m-%d', curr_tz='America/Los_Angeles', overwrite=True)
        self._data.drop(columns=['Unassigned'], inplace=True)
        self._data.set_index('datetime-America/Los_Angeles', inplace=True)

    def get_data(self):
        return self._data


def readTravelTimeCSV(filepath: str):
    metadata = pd.read_excel(datapath_metadata, sheet_name='TravelPaths', header=0)
    pathID = list(metadata['pathID'].values)
    data = pd.read_table(filepath, header=None)
    data[0] = data[0].str.replace("  ", " ")
    data[0] = data[0].str.replace(': ', ' ')
    data = data[0].str.split(pat=' ', expand=True)
    dt_str = data.iloc[:, 1] + ' ' + data.iloc[:, 2]
    dt_str = dt_str.apply(lambda x: x[0:x.find('.') - 3])
    data = data.iloc[:, 3:]
    labels = list(data.columns)
    exist = []
    for n in range(0, len(labels), 2):
        key = data.iloc[0, n]
        if 'Tra' in key:
            cut_key = key.replace('Tra', '')
            if cut_key in pathID:
                i = list(metadata['pathID'].values).index(cut_key)
                data.rename(columns={labels[n + 1]: str(metadata.iloc[i, 1])}, inplace=True)
                exist.append(str(metadata.iloc[i, 1]))
    data = data[exist]
    data.insert(0, 'DT', dt_str)
    return data


class PEMS:
    def __init__(self, northbound: DataFrame, southbound: DataFrame, sort=True):
        self._northbound = northbound.drop(columns=['# Lane Points', '% Observed'])
        self._southbound = southbound.drop(columns=['# Lane Points', '% Observed'])
        nMelt = self._northbound.melt(id_vars=['Time'], var_name='Date',
                                      value_name='Northbound (VMT)')
        sMelt = self._southbound.melt(id_vars=['Time'], var_name='Date',
                                      value_name='Southbound (VMT)')
        nMelt['datetime'] = nMelt['Date'] + ' ' + nMelt['Time']
        sMelt['datetime'] = sMelt['Date'] + ' ' + sMelt['Time']
        nMelt.drop(columns=['Time', 'Date'], axis=1, inplace=True)
        sMelt.drop(columns=['Time', 'Date'], axis=1, inplace=True)
        nMelt = dtk.df_str2dt(nMelt, 'datetime', '%m/%d/%Y %H:%M', curr_tz='America/Los_Angeles',
                              overwrite=True).set_index('datetime-America/Los_Angeles')
        sMelt = dtk.df_str2dt(sMelt, 'datetime', '%m/%d/%Y %H:%M', curr_tz='America/Los_Angeles',
                              overwrite=True).set_index('datetime-America/Los_Angeles')
        self._data = pd.concat([nMelt, sMelt], axis=1)
        self._data = self._data[~self._data.index.isnull()]
        if sort:
            self._data = self._data[~self._data.index.duplicated()].sort_index()
        return

    def get_data(self):
        return self._data


def load_gridsmart():
    return


def load_clarity():
    return


def load_meteorology():
    return


def load_travelTime():
    return


def updateSQL_gridsmart(data: pd.DataFrame):
    assert list(data.columns) == [
        'reading_idx',
        'Intersection',
        'Data',
        'Time',
        'Northbound',
        'Eastbound',
        'Southbound',
        'Westbound',
        'Unassigned',
        'Total'
    ]
    return


def updateSQL_HighResClarity(data: pd.DataFrame):
    assert list(data.columns) == [
        'reading_idx',
        'Sensor Name',
        'nodeID',
        'Cross Streets',
        'datetime - UTC',
        'datetime - America/Los_Angeles',
        'DayOfWeek',
        'Date'
        'Hour',
        'Minutes',
        'AQI',
        'NO_2 Raw Concentration(ppb)',
        'NO_2 Calibrated Concentration(ppb)',
        'PM_2.5 Calibrated Concentration',
        'Internal Temperature(degC)',
        'Internal Relative Humidity(%)',
        'Longitude',
        'Latitude'
    ]
    return


def updateSQL_bgNO2(data: pd.DataFrame):
    return
