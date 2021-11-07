"""
MODULE DOCSTRING HERE
"""
import pandas as pd
from sqlalchemy import create_engine
import psycopg2

# TODO: Need to figure out how to handle the images

class Save:
    """A dynamic and intelligent way to save both structured and unstructured data locally and/or on the cloud.

    FINISH WHEN CLASS IS FINISHED
    """
    def __init__(self, dataframe : pd.DataFrame, unstructured = None) -> None:
        self.df = dataframe
        self.unstructured = unstructured


    def df_to_csv(self, filename: str) -> None:
        """Saves a pandas dataframe object locally to a csv file in specified name/path.

        Parameters
        ----------
        filename : str
            The name and/or path that the csv is assigned. No path specified means that the csv file is saved in the local folder.
            If the extension .csv is not detected, this is allowed for and the method will automatically add this.
        """
        if filename[-4:] != '.csv':
            filename +='.csv'
        self.df.to_csv(filename, index=False)


    def df_to_pickle(self, filename: str) -> None:
        """Saves a pandas dataframe object locally to a pickle object in specified name/path.

        Parameters
        ----------
        filename : str
            The name and/or path that the pickle object is assigned. No path specified means that the pickle object is saved in the local folder.
            If the extension .pkl is not detected, this is allowed for and the method will automatically add this.
        """
        if filename[-4:] != '.pkl':
            filename += '.pkl'
        self.df.to_pickle(filename)


    def df_to_json(self, filename: str) -> None:
        """Saves a pandas dataframe object locally to a JSON file in specified name/path.

        Parameters
        ----------
        filename : str
            The name and/or path that the JSON file is assigned. No path specified means that the JSON file is saved in the local folder.
            If the extension .json is not detected, this is allowed for and the method will automatically add this.
        """
        if filename[-5:] != '.json':
            filename += '.json'
        self.df.to_json(filename)

    # TODO:
    def df_to_sql(self, name):
        DATABASE_TYPE = 'postgresql'
        DBAPI = 'psycopg2'
        HOST = 'localhost'
        USER = 'postgres'
        PASSWORD = 'password'
        DATABASE = 'Pagila'
        PORT = 5432
        engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")

        self.df.to_sql(name,engine)

    # TODO:
    def df_to_s3(self):
        pass



def main():
    df = pd.DataFrame({'name': ['Raphael', 'Donatello'],
                    'mask': ['red', 'purple'],
                    'weapon': ['sai', 'bo staff']})
    print(df)

    x = Save(df)
    x.df_to_json('test.json')


if __name__ == '__main__':
    main()
