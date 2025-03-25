import pandas as pd

class AHS_Parser:
    _default_path = '/Users/diol5851/Documents/rental-housing-cost/raw_data/AHS_National/AHS_All_Possible_Vars_2015_To_2023.csv'

    def __init__(self, path_to_defs:str = _default_path):
        defs = pd.read_csv(path_to_defs, index_col=False)
        self._defs = defs[['Variable', 'Survey Years', 'Type', 'Response Codes']]
        self._defs.loc[:, 'Survey Years'] = self._defs['Survey Years'].apply(lambda x: [int(y[:4]) for y in x.split(', ')])

    def _select_var(self, var:str, year:int) -> pd.DataFrame:
        '''Return a DataFrame with the unique specification for the given variable name and year.

        Parameters
        ----------
        var : str
            The name of the variable to select.
        year : int
            The year of the AHS dataset being processed.
        
        Returns
        -------
        pd.DataFrame
            A DataFrame containing the unique specification for the variable in the given year.

        Raises
        ------
        ValueError
            If the variable is not found in the AHS dataset or if a unique specification cannot be determined.
        '''
        values = self._defs[self._defs['Variable'] == var]
        idx_arr = [year in s for s in values['Survey Years']]
        if sum(idx_arr) == 0:
            raise ValueError(f'Variable not found in {year} AHS dataset.')
        elif sum(idx_arr) > 1:
            raise ValueError(f'Unique variable cannot be determined for the given year.')
        return values[idx_arr]

    def parse_categorical(self, var:str, year:int) -> dict:
        '''Return a dictionary of the response codes and descriptions for a given categorical variable.

        Parameters
        ----------
        var : str
            The name of the variable to parse.
        year : int
            The year of the AHS dataset being processed.

        Returns
        -------
        dict
            A dictionary where the keys are the numeric response codes and the values are the 
            text descriptions.

        Raises
        ------
        ValueError
            If the variable is not found in the AHS dataset.
        TypeError
            If the variable is not categorical according to the AHS dataset.
        '''
        # Check if the variable exists in the AHS dataset.
        if var not in self._defs['Variable'].values:
            raise ValueError(f'Variable {var} not found in AHS dataset.')
        # Check if the variable is categorical.
        variable = self._select_var(var, year)
        if variable['Type'].item() == 'Numeric':
            raise TypeError(f'Variable {var} is numeric and cannot be parsed as a categorical value.')
        # If the below code executes, the variable exists and is categorical.
        resp_str = variable['Response Codes'].item()
        resp_dict = dict()
        for resp in resp_str.split('||'):
            idx = resp.find(':')
            code = resp[:idx]
            desc = resp[idx+1:].strip()
            if code.find('or') == -1:
                resp_dict["'" + code + "'"] = desc
            else:
                codes = code.split(' or ')
                for c in codes:
                    resp_dict["'" + c + "'"] = desc
        return resp_dict