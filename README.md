# Airbnb Scraper

A fully dynamic and scalable data pipeline made in Python dedicated to scraping Airbnb's commercial website for both alphanumeric and image data, and saving both locally and/or on the cloud.

## Installation
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install CommercialScraper.
```bash
pip install CommercialScraper
```

## Usage
```python
from CommercialScraper.pipeline import AirbnbScraper
from CommercialScraper.data_save import Save

scraper = AirbnbScraper()

# Returns a dictionary of structured data and a list of image sources for a single product page
product_dict, imgs = scraper.scrape_product_data('https://any/airbnb/product/page', any_ID_you_wish, 'Any Category Label you wish')

# Returns a dataframe of product entries as well as a dictionary of image sources pertaining to each product entry
df, imgs = scraper.scrape_all()


# Initialise an instance of the saver object to save yielded data where you wish
saver = Save(df, imgs)

# Saves the dataframe to a csv in your local directory inside a created 'data/' folder. 
# Structured data can be saved in numerous formats, image data can only be saved in .png files
saver.df_to_csv('any_filename')

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