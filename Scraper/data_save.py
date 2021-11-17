"""
A dynamic and intelligent module to save both structured and unstructured data locally and/or on the cloud.

Structured data shopuld be inputted in the form of a pandas dataframe, and unstructurted data should be inputted as a dictionary 
containing relevant id's as keys and iterable objects of source links as values.
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

class Save:
    def __init__(self, df : pd.DataFrame, unstructured=None) -> None:
        """This makes the process of permenently storing data easy and abstract.

        When an instance of the `Save` class is initialised, the data frame and (optional) source links
        can be easily written to a range of storage formats both locally and on the cloud, by utiliing the
        powerful functionality of pandas and sqlalchemy.

        Attributes
        ----------
        df : pd.DataFrame
            A pandas dataframe is the required input format for structured data.
        unstructured : dict of {any : iterable}
            'unstructured' must  be inputted as a dictionary containing relevant id's as keys and iterable objects of source links as values.

        """
        self.df = df
        self.unstructured = unstructured

    @staticmethod
    def __dirs_check_and_make(struct: bool = False, unstruct: bool = False) -> None:
        # Makes local directories if they havent already been made so that local data can be stored neatly
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
        """Saves a pandas dataframe object locally to a csv file in specified name.

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
        """Saves a pandas dataframe object locally to a pickle object in specified name.

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
        """Saves a pandas dataframe object locally to a JSON file in specified name.

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
        # This pvt. method feeds into df_to_postgresql() as the `method` parameter in the pandas method to_sql
        # gets a DBAPI connection that can provide a cursor
        dbapi_conn = conn.connection
        with dbapi_conn.cursor() as cur:
            s_buf = StringIO()
            writer = csv.writer(s_buf)
            writer.writerows(data_iter)
            s_buf.seek(0)

            # Manually formats df to csv. This is computationally the fastest method
            columns = ', '.join('"{}"'.format(k) for k in keys)
            if table.schema:
                table_name = '{}.{}'.format(table.schema, table.name)
            else:
                table_name = table.name

            sql = 'COPY {} ({}) FROM STDIN WITH CSV'.format(
                table_name, columns)
            cur.copy_expert(sql=sql, file=s_buf)


    def df_to_postgresql(self, table_name: str, username: str, password: str, hostname: str, port: str, database: str) -> None:
        """Abstracts the process of saving a pandas dataframe to a postgres sql database.

        Parameters
        ----------
        table_name : str
            The name of the table that you wish to assign.
        username : str
            The username of the connected postgres sql database. This can be found on the 'Properties' tab on the server.
        password : str
            The user's password.
        hostname : str
            The host name/address. This can be found on the 'Properties' tab on the server.
        port : str
            The port number of the database. This can be found on the 'Properties' tab on the server.
        database : str
            The name of the database that you wish to store your table.
        
        """
        print(f'Saving dataframe to SQL: {database}.{table_name}')
        # Ensures that the port parameter is an string and not an integer, which would break the method
        if isinstance(port, str) is False:
            port = str(port)
        engine = create_engine(f'postgresql://{username}:{password}@{hostname}:{port}/{database}')
        self.df.to_sql(table_name, engine, method=self.__psql_insert_copy, index=False)


    def df_to_s3(self, aws_access_key_id : str, region_name : str, aws_secret_access_key : str, bucket_name : str, upload_name : str) -> None:
        """Storing on the cloud made easy. All that is required is an s3 bucket that is open to the local IP address. For more information about setting up an AWS s3 bucket, see https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html

        Parameters
        ----------
        aws_access_key_id : str
            The access_key provided by AWS.
        region_name : str
            The region name provided by AWS.
        aws_secret_access_key : str
            The secret access_key provided by AWS.
        bucket_name : str
            The name of the bucket that the user has assigned upon creation.
        upload_name : str
            The name of the directory inside the s3 bucket that the user wishes to assign.

        """
        print(f'Uploading dataframe to AWS s3 bucket: {bucket_name}')
        self.s3_client = boto3.client('s3', aws_access_key_id= aws_access_key_id , region_name= region_name, aws_secret_access_key= aws_secret_access_key)
        # A temporary file ensures that the data isn't permanently stored locally
        with tempfile.NamedTemporaryFile() as temp:
            self.df.to_csv(temp.name + '.csv')
            self.s3_client.upload_file(f'{temp.name}.csv', bucket_name, f'{upload_name}/{temp.name}.csv')
            temp.close()  


    def images_to_local(self) -> None:
        """A method of storing source links for unstructured data locally. 
        
        Each source is stored as a png file, and all sources are stored locally in data/unstructured/ 
        Furthermore, the png's will be stored in respective directories that each are dedicated to a single ID.
        """
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
        """Storing on the cloud made easy. All that is required is an s3 bucket that is open to the local IP address. For more information about setting up an AWS s3 bucket, see https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html
 
        Parameters
        ----------
        aws_access_key_id : str
            The access_key provided by AWS.
        region_name : str
            The region name provided by AWS.
        aws_secret_access_key : str
            The secret access_key provided by AWS.
        bucket_name : str
            The name of the bucket that the user has assigned upon creation.
        upload_name : str
            The name of the directory inside the s3 bucket that the user wishes to assign.

        """
        print(f'Uploading images to AWS s3 bucket: {bucket_name}')
        self.s3_client = boto3.client('s3', aws_access_key_id= aws_access_key_id , region_name= region_name, aws_secret_access_key= aws_secret_access_key)
        # A temporary file ensures that the data isn't permanently stored locally
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

     