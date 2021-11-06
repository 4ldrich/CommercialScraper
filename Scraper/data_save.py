"""
MODULE DOCSTRING HERE
"""
import pandas as pd
from sqlalchemy import create_engine
import psycopg2

# TODO: Need to figure out how to handle the images



class Store:
    def __init__(self, dataframe : pd.DataFrame, unstructured = None) -> None:
        self.df = dataframe
    
    def df_to_csv(self, filename: str) -> None:
        if filename[-4:] != '.csv':
            filename +='.csv'
        self.df.to_csv(filename, index=False)
    

    # TODO
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



    def df_to_s3(self):
        pass




def main():
    df = pd.DataFrame({'name': ['Raphael', 'Donatello'],
                    'mask': ['red', 'purple'],
                    'weapon': ['sai', 'bo staff']})

    x = Store(df)
    x.df_to_csv('test.csv')
    x.df_to_csv('test')

if __name__ == '__main__':
    main()