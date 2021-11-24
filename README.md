# Airbnb Scraper

A fully dynamic and scalable data pipeline made in Python dedicated to scraping Airbnb's commercial website for both alphanumeric and image data, and saving both locally and/or on the cloud.

## Installation
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install airbnbscraper.
```bash
pip install airbnbscraper
```

## Usage
```python
from airbnbscraper.Scraper import AirbnbScraper

scraper = AirbnbScraper()

# Returns a dictionary of structured data and a list of image sources for a single product page
product_dict, imgs = scraper.scrape_product_data('https://any/airbnb/product/page', any_ID_you_wish, 'Any Category Label you wish')

# Returns a dataframe of product entries as well as a dictionary of image sources pertaining to each product entry
df, imgs = scraper.scrape_all()

```
## Docker Image 
This package has been containerised in a docker image where it can be run as an application. Please note that data can only be stored onto an SQL database or on the cloud by this method, not in local directories.
[Docker Image](https://hub.docker.com/r/docker4ldrich/airbnb-scraper)

```bash
docker pull docker4ldrich/airbnb-scraper

docker run -it docker4ldrich/airbnb-scraper
```
## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)