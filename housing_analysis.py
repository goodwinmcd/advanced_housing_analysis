#!/usr/bin/python

import numpy as np
import pandas as pd
import pprint

pp = pprint.PrettyPrinter(indent=4)
houses = pd.read_csv('C:\\Users\\mcdonago\\Source\\Repos\\advanced_housing_analysis\\train.csv')
houses = houses.dropna(subset=['MSZoning', 'Utilities', 'Exterior1st', 'Exterior2nd', 'KitchenQual'])
na_values = {
    'LotFrontage': 0,
    'Alley': 'NA',
    'MasVnrType': 'None',
    'MasVnrArea': 'None',
    'BsmtQual': 'NA',
    'BsmtCond': 'NA',
    'BsmtExposure': 'NA',
    'BsmtFinType1': 'NA',
    'BsmtFinType2': 'NA',
    'BsmtFinSF1': 0,
    'BsmtFinSF2': 0,
    'BsmtUnfSF': 0,
    'TotalBsmtSF': 0,
    'BsmtFullBath': 0,
    'BsmtHalfBath': 0,
    'Functional': 'Typ',
    'FireplaceQu': 'NA',
    'GarageType': 'NA',
    'GarageYrBlt': 0,
    'GarageFinish': 'NA',
    'GarageCars': 0,
    'GarageArea': 0,
    'GarageQual': 'NA',
    'GarageCond': 'NA',
    'PoolQC': 'NA',
    'Fence': 'NA',
    'MiscFeature': 'NA',
    'SaleType': 'Oth',
}
houses.fillna(value=na_values, inplace=True)
#Corner cases
houses.loc[houses['MasVnrArea']=='None', 'MasVnrArea'] = 0

def create_col_dict(data):
    col_dict = {}
    for column in data.keys():
        if column == 'InflSalePrice':
            continue
        col_dict[column] = {}
        for value in data[column].unique():
            col_dict[column][value] = {
                'mean': 0,
                'median': 0,
                'count': 0,
            }
    return col_dict

def classify_columns(data, columns):
    for column in columns:
        data[column] = pd.to_numeric(data[column])
        five_num_sum = data[column].describe()
        data.loc[data[column] == 0, column] = 0
        data.loc[(data[column] > 0) &
                 (data[column] < five_num_sum['25%']) &
                 (data[column] != 0), column] = 1
        data.loc[(data[column] < five_num_sum['50%']) &
                 (data[column] >= five_num_sum['25%']) &
                 (data[column] != 0), column] = 2
        data.loc[(data[column] < five_num_sum['75%']) &
                 (data[column] >= five_num_sum['50%']) &
                 (data[column] != 0), column] = 3
        data.loc[data[column] >= five_num_sum['75%'], column] = 4
    return data

def get_median(column_dataset):
    return column_dataset.median()

def get_mean(column_dataset):
    return column_dataset.mean()

def count_rows(column_dataset):
    return len(column_dataset)

def get_column_info(data):
    col_info = create_col_dict(data)
    for column in col_info:
        for value in col_info[column]:
            current_dataset = data.loc[data[column]==value]
            col_info[column][value]['median'] = get_median(current_dataset['InflSalePrice'])
            col_info[column][value]['mean'] = get_mean(current_dataset['InflSalePrice'])
            col_info[column][value]['count'] = count_rows(current_dataset['InflSalePrice'])
    return col_info

def find_remodeled_time(row):
   return -1 if row['YearRemodAdd'] == row['YearBuilt'] else 2018 - row['YearRemodAdd']

def figure_inflation_price(row):
    num_years = 2018 - row['YrSold']
    old_price = row['SalePrice']
    inflation_rate = .0218
    for year in range(num_years):
        old_price = old_price + (inflation_rate * old_price) 
    return old_price
        
def remodeled_class_col(row):
   return False if row['YearRemodAdd'] == row['YearBuilt'] else True

def inflation_prices(df):
    return df.apply(figure_inflation_price, axis=1)

def year_since_remod(df):
    return df.apply(find_remodeled_time, axis=1)

def remodeled(df):
    return df.apply(remodeled_class_col, axis=1)

houses['InflSalePrice'] = inflation_prices(houses)
houses['YrSinceRemod'] = year_since_remod(houses)
houses['remodeled'] = remodeled(houses)
houses = houses.drop('SalePrice', axis=1)

square_feet_columns =   [
                        'LotArea',
                        'LotFrontage',
                        'MasVnrArea',
                        'BsmtFinSF1',
                        'BsmtFinSF2',
                        'BsmtUnfSF',
                        'TotalBsmtSF',
                        '1stFlrSF',
                        '2ndFlrSF',
                        'LowQualFinSF',
                        'GrLivArea',
                        'GarageArea',
                        'WoodDeckSF',
                        'OpenPorchSF',
                        'EnclosedPorch',
                        '3SsnPorch',
                        'ScreenPorch',
                        'PoolArea',
                        ]

class_columns = houses.drop(labels=['Id',
                                    'GarageYrBlt',
                                    'YearRemodAdd',
                                    'YearBuilt',
                                    'MiscVal',
                                    'YrSold',
                                    'YrSinceRemod',
                                    ], axis=1)

classed_data = classify_columns(class_columns, square_feet_columns)
classes_dict = get_column_info(classed_data)
