import pandas as pd
import numpy as np

numbers= [0,0,0,32]
mean = np.mean(numbers)

def variable_mean(feature:str, data_frame):
    return data_frame[feature].mean()

data_set = pd.DataFrame({'values': [0,0,0,32]})

def test_variable_mean():

    mean_by_function = variable_mean('values', data_set)
    
    assert mean == mean_by_function, f"error: the function returned value {mean_by_function} is not  the mean."
        
    print(f'{mean} mean reference')
    print(f'{mean_by_function} mean calculated by function')