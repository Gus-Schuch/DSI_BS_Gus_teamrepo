import matplotlib.pyplot as plt
import yaml
import requests
import pandas as pd
import logging

class Analysis():
    '''   Load config into an Analysis object

    Load system-wide configuration from `configs/system_config.yml`, user configuration from
    `configs/user_config.yml`, and the specified analysis from config.yml file

    Parameters
    ----------
    config : str
    Path to the analysis/job-specific configuration file. This file was named 'config.yml'

    Returns
    -------
    analysis_obj : Analysis
    Analysis object containing consolidated parameters from the configuration files

    Example
    -----   
    analysis_obj = Analysis('config.yml')

    It generates a Dictionary with pairs Key: value
      
      Ex:  
        Key             Value
        --------       ------------
    title_analisys:  Top 100 Most Popular Git Repos Analisys

    '''



    def __init__(self, config: str) -> None:
        CONFIG_PATHS = [r'configs\system_config.yml' , r'configs\user_config.yml']

        # add the analysis config to the list of paths to load
        paths = CONFIG_PATHS + [config]

        # initialize empty dictionary to hold the configuration
        config = {}

        # load each config file and update the config dictionary
        for path in paths:
            with open(path, 'r') as f:
                this_config = yaml.safe_load(f)
            config.update(this_config)

        self.config = config
        
    
        # to print config info to check if it is loaded.
    def print_config(self): 
        return print(self.config)
    
       
    def load_data(self) -> None:
        ''' Retrieve data from the GitHub API.
            The token code has to be inserted in the ./configs/user_config.yml file in the key token:' '.

            This function makes an HTTPS request to the GitHub API and retrieves a search of the " MOST POPULAR REPOSITORIES IN GIT ".
            The data is stored in the Analysis object.
            
            It prints in the computer screen a Summary Table with the columns:
            
            Variable column that can be changed in the config file
            ------------------------------------------------------------
            selected_feature -> is one of the columns selected in the "config.yml file that is the object of the analisys. The options to be selected 
                                are Watchers_Qty, Size_in_Bytes , Forks_Qty, Open_Issues_Qty)
             
            Fixed columns
            --------------                    
            'Repo_Name'      -> the git repository name
            'Description'    -> the description of the repository subjects
            'url'            -> the url address
            'Year_Creation'  -> the year the repository was created. The year is shown with the last 2 digits format as 20XX, where XX are the last two digits shown
                               (ex: 11 refers to 2011, 19 refers to 2019,....)


            Parameters
            ----------
            None

            Returns
            -------
            None

            '''
        
        
        logging.basicConfig(
            level=logging.INFO, 
            handlers=[logging.StreamHandler(), logging.FileHandler('Log_analysis.log')],
            )
        
        response = requests.get(url='https://api.github.com/search/repositories?q=stars:>1&sort=stars&per_page=100',
                                headers={'Authorization': 'Bearer ' + self.config['token'],
                                 'Accept': 'application/vnd.github+json'})
           
        
        if response.status_code == 200:
            print(f'Response Status Code:"{response.status_code}". The git api search request was successful.')
        else:
             print(f'Status Code:"{response.status_code}". Git api Request ERROR')
            
        
        response_json = response.json()

        assert 'items' in response_json, "error loadding column with repositories info."

        data = pd.DataFrame(response_json['items'])
    
    
        assert isinstance(data, pd.DataFrame), "error loading repositories search, data resulted from request was not converted to a dataframe."
        
        config_variable = self.config['selected_feature']  #(Watchers_Qty, Size_in_Bytes , Forks_Qty, Open_Issues_Qty)
        
        variable_name = config_variable
        lst= ['Watchers_Qty', 'Size_in_Bytes' , 'Forks_Qty', 'Open_Issues_Qty']
        if variable_name not in lst:
            raise NameError(f'"{variable_name}" feature in analysis_config file is not in the Options to be calculated.')
        
        config_lines_number = self.config['selected_number_lines']
        
        value = config_lines_number
        try:
            lines_number = int(value)
        except ValueError as e:
            e.add_note(f'Number of lines "{lines_number}" in analysis_config file is not an integer')
            raise e

       
        data.rename(columns={'name':'Repo_Name','description':'Description' ,'created_at':'Date_Creation',
                             'watchers_count':'Watchers_Qty', 'size':'Size_in_Bytes', 'forks_count':'Forks_Qty',
                             'has_projects':'Use_Projects','open_issues_count':'Open_Issues_Qty'}, inplace=True)
        data.sort_values(config_variable, ascending=False, inplace=True)
           
       
        data['Date_Creation'] = pd.to_datetime(data['Date_Creation']) 
        data['Year_Creation'] = data['Date_Creation'].dt.strftime('%y') 

        data_summary = data[[config_variable, 'Repo_Name','Description', 'url', 'Year_Creation']].copy() 
        
        config_system_title = self.config['title_corp']
        config_analysis_title = self.config['title_analisys']
        
        print(f'{config_system_title}. {config_analysis_title} ordered by {config_variable}:')  
        
        self.dataset = data_summary

        try:
            pd.set_option("display.max_columns", None)
            print(self.dataset.head(config_lines_number))
        except Exception as e:
            e.add_note(f'Number of lines "{config_lines_number}" in analysis_config file is not an integer. Error on printing on Screen the Summary list of Repositories.')
            logging.error(f'Number of lines "{config_lines_number}" in analysis_config file is not an integer. Error on printing on Screen the Summary list of Repositories.')
            raise e
        
    def compute_analysis(self) -> None:
        '''Analyze previously-loaded data.

        This function runs an analytical measure (mean).
        It has a sub function "variable_mean" that is used to calculate the mean of a feature (column) in a DataFrame.
        The feature can be changed in the "config.yml", changing the values in the key "selected_feature:". The repositories features that
        can be analised are (Watchers_Qty, Size_in_Bytes , Forks_Qty, Open_Issues_Qty).
        
        
        Parameters
        ----------
        None

        Returns
        -------
        Returns the mean of a column
        '''

        # the subfunction inside the function compute_analysis
        def variable_mean(feature:str, data_frame):
            '''Subfunction of compute_analysis. Calculate the mean of a column in a Dataframe.
        
        Parameters
        ----------
        feature: name of a column
        data_fame: a pandas dataframe

        Returns
        -------
        Returns the mean of a column
        
        '''
            return data_frame[feature].mean()

        # the final part of the function compute_analysis
        feature = self.config['selected_feature']                
        self.dataset.to_excel(f'./repo_ordered_by_{feature}.xlsx', index=False)
        
        mean = variable_mean(feature, self.dataset)
        logging.info(f' By "{feature}", the top 100 most popular repositories MEAN is:{mean}')
        mean_info =(f' By "{feature}", the MEAN is:{mean}')        
        return  mean_info
        
    
    def plot_data(self) -> plt.Figure:
        ''' Analyze and plot data

        Generates a plot, display it to screen, and save it to the local directory.

        Parameters
        ----------
        None
        
        Returns
        -------
        fig : matplotlib.Figure

        '''
       
       
        data_order = self.dataset
        
        data_order.sort_values('Year_Creation', ascending=True, inplace=True)     
        
        feature = self.config['selected_feature']
        color = self.config['plot_color']
            
        plt.scatter(data_order['Year_Creation'],
                    data_order[feature],
                    label='Total Events',
                    color=color)
        #plt.legend()
        plt.grid()
        plt.title(f'Repo {feature} x Year Creation')
        plt.ylabel(feature)
        plt.xlabel('Year Repos Creation 20XX')
        plt.show
        plt.savefig(f'repos_{feature}_by_year_creation.png')
                    
        
        
    def notify_done() -> None:
        ''' Notify the user that analysis is complete.

        Send a notification to the user through the ntfy.sh webpush service.

        Parameters
        ----------
        None

        Returns
        -------
        None

        '''   
        
        topic = 'dsi_c2_brs'
        title = 'LUIZ_GUSTAVO - Cohort_2 Assignment Building Software!'
        message = 'Analysis Done'

      
        return requests.post(
            'https://ntfy.sh/' + topic,
            data=message.encode('utf-8'),
            headers={'Title': title}
            )
