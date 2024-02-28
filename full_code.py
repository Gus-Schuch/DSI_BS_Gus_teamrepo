## CONFIG

import argparse
import yaml
from pprint import pprint

CONFIG_PATHS = ['system_config.yml', 'user_config.yml']


paths = CONFIG_PATHS + ['analysis_config.yml']

# initialize empty dictionary to hold the configuration
config = {}

# load each config file and update the config dictionary
for this_config_file in paths:
    with open(this_config_file, 'r') as f:
        this_config = yaml.safe_load(f)
    config.update(this_config)

## print the config in an easier to read way


## LOAD DATA

import requests
import yaml
import pandas as pd
from pprint import pprint
import math
import numpy as np


#with open('config.yml', 'r') as f:
#    config = yaml.safe_load(f)

response = requests.get(url='https://api.github.com/search/repositories?q=stars:>1&sort=stars&per_page=100',
                        headers={'Authorization': 'Bearer ' + config['token'],
                                 'Accept': 'application/vnd.github+json'})

print(response.status_code)


response_json = response.json()

data= pd.DataFrame(response_json['items'])

config_variable = config['selected_feature']  #(Watchers_Qty, Size_in_Bytes , Forks_Qty, Open_Issues_Qty)

config_lines_number = config['selected_number_lines']

data.rename(columns={'name':'Repo_Name','description':'Description' ,'created_at':'Date_Creation', 'watchers_count':'Watchers_Qty', 'size':'Size_in_Bytes', 'forks_count':'Forks_Qty', 'has_projects':'Use_Projects','open_issues_count':'Open_Issues_Qty'}, inplace=True)
data.sort_values(config_variable, ascending=False, inplace=True)


data_summary = data[['Repo_Name','Description', 'url', config_variable]].copy() # config_variable

print(data_summary.head(config_lines_number))


def variable_mean(feature:str, data_frame):
    return data_frame[feature].mean()

mean_feature = variable_mean(config_variable, data_summary)
print(f' By "{config_variable}", the top 100 most popular repositories MEAN is "{mean_feature}"')

print ('END LINE PROCESSED')
