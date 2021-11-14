"""
MODULE DOCSTRING HERE
"""
import pandas as pd
from sqlalchemy import create_engine
import psycopg2 
from io import StringIO
import csv
import tempfile
import boto3

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
        self.df.to_sql(table_name, engine, method=self.__psql_insert_copy, index=False)


    # TODO:
    def df_to_s3(self,aws_access_key_id,region_name, aws_secret_access_key, bucket_name, upload_name ) -> None:
        self.s3_client = boto3.client('s3', aws_access_key_id= aws_access_key_id , region_name= region_name, aws_secret_access_key= aws_secret_access_key)
        with tempfile.NamedTemporaryFile() as temp:
            self.df.to_csv(temp.name + '.csv')
            self.s3_client.upload_file(f'{temp.name}.csv', bucket_name, f'{upload_name}/{temp.name}.csv')
            temp.close()  



def main():
    df = pd.DataFrame({'name': ['Raphael', 'Donatello'],
                    'mask': ['red', 'purple'],
                    'weapon': ['sai', 'bo staff']})
    print(df)
    x = Save(df)
    x.df_to_postgresql('args', 'postgres', 'Badwolf10-1', 'localhost', 5432, 'Pagila')


if __name__ == '__main__':
    main()

"""
    def __scrape_product_images(self, driver, ID):
        os.mkdir('data/images/'+ str(ID))


        sleep(0.33)
        homePage_html = driver.find_element_by_xpath('//*')
        homePage_html = homePage_html.get_attribute('innerHTML')
        homePage_soup = BeautifulSoup(homePage_html, 'lxml')
        images = homePage_soup.find_all('img', class_='_6tbg2q')

        if images is None:
            raise Exception

        char_no = 97
        for image in images:
            image_src = image['src']
            urllib.request.urlretrieve(image_src,'data/images/' + str(ID) + '/' + str(ID) + chr(char_no) + '.png')
            char_no +=1
        
"""