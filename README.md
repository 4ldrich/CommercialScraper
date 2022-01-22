# Commercial Scraper

A fully dynamic and scalable data pipeline made in Python dedicated to scraping commercial websites that don't offer API's. Can yield structured and unstructured data, and is able to save data both locally and/or on the cloud via the data processing module.

Currently, the scraper is only built to scrape Airbnb's website, but more websites are in the works to generalise the package.

## Installation
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install CommercialScraper.
```bash
pip install CommercialScraper
```

## Usage
```python
from CommercialScraper.pipeline import AirbnbScraper
import CommercialScraper.data_processing

scraper = AirbnbScraper()

# Returns a dictionary of structured data and a list of image sources for a single product page
product_dict, imgs = scraper.scrape_product_data('https://any/airbnb/product/page', any_ID_you_wish, 'Any Category Label you wish')

# Returns a dataframe of product entries as well as a dictionary of image sources pertaining to each product entry
df, imgs = scraper.scrape_all()


# Saves the dataframe to a csv in your local directory inside a created 'data/' folder. 
data_processing.df_to_csv(df, 'any_filename')

# Saves images locally
data_processing.images_to_local(images)

# Saves structured data to sql database
data_processing.df_to_sql(df, table_name, username, password, hostname, port, database)

# Saves structured data to AWS cloud services s3 bucket
data_processing.df_to_s3(df, aws_access_key_id, region_name, aws_secret_access_key, bucket_name, upload_name)

# Saves images to AWS cloud services s3 bucket
data_processing.images_to_s3(source_links, aws_access_key_id,region_name, aws_secret_access_key, bucket_name, upload_name)

```
## Docker Image 
This package has been containerised in a docker image where it can be run as an application. Please note that data can only be stored on the cloud by this method, not locally.
[Docker Image](https://hub.docker.com/r/docker4ldrich/airbnb-scraper)

```bash
docker pull docker4ldrich/airbnb-scraper

docker run -it docker4ldrich/airbnb-scraper
```
Follow the prompts and insert credentials carefully, there won't be a chance to correct any typing errors!
It's recommended that you paste credentials in where applicable.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)