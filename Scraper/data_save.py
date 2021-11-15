"""
MODULE DOCSTRING HERE
"""
import pandas as pd
import urllib.request
from sqlalchemy import create_engine
import psycopg2 
from io import StringIO
import csv
import tempfile
import boto3
import os

# TODO: Need to figure out how to handle the images

class Save:
    """A dynamic and intelligent way to save both structured and unstructured data locally and/or on the cloud.

    FINISH WHEN CLASS IS FINISHED
    """
    def __init__(self, dataframe : pd.DataFrame, unstructured=None) -> None:
        self.df = dataframe
        self.unstructured = unstructured

    @staticmethod
    def __dirs_check_and_make(struct: bool = False, unstruct: bool = False) -> None:
        if struct:
            if os.path.exists('data') == False:
                os.mkdir('data')
            if os.path.exists('data/structured') == False:
                os.mkdir('data/structured')
        if unstruct:
            if os.path.exists('data') == False:
                os.mkdir('data')
            if os.path.exists('data/unstructured') == False:
                os.mkdir('data/unstructured')


    def df_to_csv(self, filename: str) -> None:
        """Saves a pandas dataframe object locally to a csv file in specified name/path.

        Parameters
        ----------
        filename : str
            The name and/or path that the csv is assigned. No path specified means that the csv file is saved in the local folder.
            If the extension .csv is not detected, this is allowed for and the method will automatically add this.
        """
        self.__dirs_check_and_make(struct = True)
        if filename[-4:] != '.csv':
            filename +='.csv'
        print(f'Saving dataframe to CSV file: {filename}')
        self.df.to_csv('data/structured/' + filename, index=False)


    def df_to_pickle(self, filename: str) -> None:
        """Saves a pandas dataframe object locally to a pickle object in specified name/path.

        Parameters
        ----------
        filename : str
            The name and/or path that the pickle object is assigned. No path specified means that the pickle object is saved in the local folder.
            If the extension .pkl is not detected, this is allowed for and the method will automatically add this.
        """
        self.__dirs_check_and_make(struct = True)
        if filename[-4:] != '.pkl':
            filename += '.pkl'
        print(f'Saving dataframe to pickle: {filename}')
        self.df.to_pickle('data/structured/' + filename)


    def df_to_json(self, filename: str) -> None:
        """Saves a pandas dataframe object locally to a JSON file in specified name/path.

        Parameters
        ----------
        filename : str
            The name and/or path that the JSON file is assigned. No path specified means that the JSON file is saved in the local folder.
            If the extension .json is not detected, this is allowed for and the method will automatically add this.
        """
        self.__dirs_check_and_make(struct = True)
        if filename[-5:] != '.json':
            filename += '.json'
        print(f'Saving dataframe to JSON: {filename}')
        self.df.to_json('data/structured/' + filename)


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
        print(f'Saving dataframe to SQL: {database}.{table_name}')
        if isinstance(port, str) is False:
            port = str(port)
        engine = create_engine(f'postgresql://{username}:{password}@{hostname}:{port}/{database}')
        self.df.to_sql(table_name, engine, method=self.__psql_insert_copy, index=False)


    def df_to_s3(self,aws_access_key_id,region_name, aws_secret_access_key, bucket_name, upload_name) -> None:
        print(f'Uploading dataframe to AWS s3 bucket: {bucket_name}')
        self.s3_client = boto3.client('s3', aws_access_key_id= aws_access_key_id , region_name= region_name, aws_secret_access_key= aws_secret_access_key)
        with tempfile.NamedTemporaryFile() as temp:
            self.df.to_csv(temp.name + '.csv')
            self.s3_client.upload_file(f'{temp.name}.csv', bucket_name, f'{upload_name}/{temp.name}.csv')
            temp.close()  


    def images_to_local(self) -> None:
        print('Saving images locally')
        self.__dirs_check_and_make(unstruct = True)
        for k, v in self.unstructured.items():
            char_no = 97
            ID = str(k)
            os.mkdir('data/unstructured/'+ str(ID))
            for image_src in v:
                urllib.request.urlretrieve(image_src,'data/unstructured/' + ID + '/' + ID + chr(char_no) + '.png')
                char_no+=1


    def images_to_s3(self,aws_access_key_id,region_name, aws_secret_access_key, bucket_name, upload_name) -> None:
        print(f'Uploading images to AWS s3 bucket: {bucket_name}')
        self.s3_client = boto3.client('s3', aws_access_key_id= aws_access_key_id , region_name= region_name, aws_secret_access_key= aws_secret_access_key)
        with tempfile.TemporaryDirectory() as tmp:
            for k, v in self.unstructured.items():
                ID = str(k)
                char_no = 97
                for image_src in v:
                    urllib.request.urlretrieve(image_src, f'{tmp}/{ID}{chr(char_no)}.png')
                    self.s3_client.upload_file(f'{tmp}/{ID}{chr(char_no)}.png', bucket_name, f'{upload_name}/{ID}/{ID}{chr(char_no)}.png')
                    char_no+=1



def main():
    df = pd.DataFrame({'name': ['Raphael', 'Donatello'],
                    'mask': ['red', 'purple'],
                    'weapon': ['sai', 'bo staff']})
    print(df)
    x = Save(df, None)
    x.df_to_json('yep')


if __name__ == '__main__':
    main()
    ###############################################################
# TO DO LIST:
    # Correct locations in df docstrings
    # Complete missing docstrings

     