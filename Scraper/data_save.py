"""
MODULE DOCSTRING HERE
"""
import pandas as pd
from sqlalchemy import create_engine
import psycopg2 
import io
from io import StringIO
import csv

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


    def __psql_insert_copy(self, table, conn, keys, data_iter) -> None:
        # gets a DBAPI connection that can provide a cursor
        dbapi_conn = conn.connection
        with dbapi_conn.cursor() as cur:
            s_buf = StringIO()
            writer = csv.writer(s_buf)
            writer.writerows(data_iter)
            s_buf.seek(0)

            columns = ', '.join('"{}"'.format(k) for k in keys)
            if table.schema:
                table_name = '{}.{}'.format(table.schema, table.name)
            else:
                table_name = table.name

            sql = 'COPY {} ({}) FROM STDIN WITH CSV'.format(
                table_name, columns)
            cur.copy_expert(sql=sql, file=s_buf)


    def df_to_postgresql(self, table_name: str, username: str, password: str, hostname: str, port: str, database: str) -> None:
        if isinstance(port, str) is False:
            port = str(port)
        engine = create_engine(f'postgresql://{username}:{password}@{hostname}:{port}/{database}')
        self.df.to_sql(table_name, engine, method=self.__psql_insert_copy)


    # TODO:
    def df_to_s3(self):
        pass



def main():
    df = pd.DataFrame({'name': ['Raphael', 'Donatello'],
                    'mask': ['red', 'purple'],
                    'weapon': ['sai', 'bo staff']})
    print(df)
    x = Save(df)
    x.df_to_postgresql('args', 'postgres', 'Badwolf10-1', 'localhost', 5432, 'Pagila')


if __name__ == '__main__':
    main()
