import requests
import yaml
import pandas as pd
from pprint import pprint
import math
import numpy as np


with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)

response = requests.get(url='https://api.github.com/search/repositories?q=stars:>1&sort=stars&per_page=100',
                        headers={'Authorization': 'Bearer ' + config['token'],
                                 'Accept': 'application/vnd.github+json'})

print(response.status_code)


response_json = response.json()

data= pd.DataFrame(response_json['items'])

config_variable = 'Watchers_Qty'
config_lines_number = 99 #Max 99 Repo lines 

data.rename(columns={'name':'Repo_Name','description':'Description' ,'created_at':'Date_Creation', 'watchers_count':'Watchers_Qty', 'size':'Size_in_Bytes', 'forks_count':'Forks_Qty', 'has_projects':'Use_Projects','open_issues_count':'Open_Issues_Qty'}, inplace=True)
data.sort_values(config_variable, ascending=False, inplace=True)

#pd.set_option("display.max_columns", 4)

data_summary = data[['Repo_Name','Description', 'url' , config_variable ]].copy()
#data_summary = data[['Repo_Name','Date_Creation','Description' ,'Watchers_Qty', 'Size_in_Bytes', 'Forks_Qty', 'Open_Issues_Qty', 'Use_Projects']].copy()
print(data_summary.head(config_lines_number))


def variable_mean(feature:str, data_frame):
    return data_frame[feature].mean()

mean_feature = variable_mean(config_variable, data_summary)
print(f' By "{config_variable}", the top 100 most popular repositories MEAN is "{mean_feature}"')

print ('END LINE PROCESSED')

