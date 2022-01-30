"""
Utilises the powerful tools of Selenium to safely navigate and collect data from websites without the use of an API.
"""
from typing import Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import numpy as np
import pandas as pd
from time import sleep
import uuid

class AirbnbScraper:
    def __init__(self, slow_internet_speed : bool=False, config : str='default', messages : bool=False):
        """A Webscraper that crawls through Airbnb's website and gathers structured/unstructured data.

        When an instance of Scraper is initialized, a Selenium Webdriver gets the homepage by use
        of the `url` attribute. Then it clicks past the cookie wall (if applicable), and navigates onto
        the main products hub.

        Parameters
        ----------
        slow_internet_speed : bool, default=False
            The crawler is designed to allow for lag whilst loading elements on a page, but users with a 
            particularly slow internet speed may cause the crawler to miss elements. A `slow_internet_speed` flag
            allows those users to still enjoy the potential of the scraper. It is not recommended to run the full
            scraper `scrape_all()` with `slow_internet_speed` enabled. This will take > 12 hours.
        config : str, defualt = 'default'
            Option to confiigure the selenium webdriver to operate in 'headless' mode or 'default' mode.
        messages : bool, default=False
            Option to activate messages of each successful item saved by the scraper, and any errors if applied.

        Attributes
        ----------
        BATCH_ATTEMPTS : int
            It is common that a Scraper can fail to find an element on a webpage for numerous reasons,
            for example that the element hasn't been loaded yet. `BATCH_ATTEMPTS` allows for this and 
            offers up to 25 attempts for the Scraper to locate and pull data from each element it is looking 
            for, until the Scraper assumes that the element doesn't exist in the particular page. If 
            `slow_internet_speed` is enabled, the attempts limit is increased to 50.
        main_url : str
            The URL for Airbnb's home page, provided for the Selenium webdriver to get upon initialization
            of the Scraper object.
        driver : Selenium Webdriver
            The webdriver that is utilized to crawl through Airbnb's website
        slow_internet_speed : bool
            The crawler is designed to allow for lag whilst loading elements on a page, but users with a 
            particularly slow internet speed may cause the crawler to miss elements. A `slow_internet_speed` flag
            allows those users to still enjoy the potential of the scraper. It is not recommended to run the full
            scraper `scrape_all()` with `slow_internet_speed` enabled. This will take > 12 hours. 
        messages : bool
            Option to activate messages of each successful item saved by the scraper, and any errors if applied.

        """
        self.main_url = "https://www.airbnb.co.uk/"
        self.slow_internet_speed = slow_internet_speed
        self.driver = None
        self.BATCH_ATTEMPTS = 50 if self.slow_internet_speed else 25
        self.messages = messages
        self.COOKIE_CLICKED = False

        # Initialising the selenium webdriver
        options = webdriver.ChromeOptions()
        if config == 'default':
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            options.add_argument("--start-maximized")
            self.driver = webdriver.Chrome(options=options)
        elif config == 'headless':
            options.add_argument('--no-sandbox')
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            options.add_argument('--log-level=3')
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument("--window-size=1920, 1200")
            options.add_argument('--disable-dev-shm-usage')
            self.driver = webdriver.Chrome(options=options)
            print('Running headless scraper. Do NOT close the program or interrupt the terminal.')
        else:
            raise ValueError(f'Configuration option "{config}" not recognised')


    def get_categories(self, count : int):
        """Gets category names and corresponding urls for each product header in Airbnb's main products page. 
        
        This method first clicks past a cookie wall if applicable. Using the `driver` that has been initialised
        with the Scraper object, this method located through and clicks each header button in the top menu bar of 
        the main products page. When each header is clicked, the category name and the current url of that clicked 
        header are stored into a zip object. 

        Parameters
        ----------
        count : int , optional
            When specified, the `count` parameter will set a limit to the number of headers that are clicked through
            and consequently, the number of categories and corresponding urls that are returned. This parameter is optional,
            and defaulted to 25 which is the number of total headers that populate Airbnb's products page.
        
        Returns
        -------
        zip of < tuples of (str, str) >
            A zipped object of tuples of the category name, followed by the url of opening that header.

        Raises
        ------
        ValueError
            If the count parameter is 0 or negative
        
        """
        # Getting the Airbnb url and clicking past the cookie wall
        self.driver.get(self.main_url)

        sleep(5 if self.slow_internet_speed else 2)
        self._cookie_check_and_click()
        # Click the I'm flexible to get to the product browser 
        flexible_button = self.driver.find_element(By.LINK_TEXT,"I’m flexible")
        flexible_button.click()
        sleep(5 if self.slow_internet_speed else 2)

        # The count variable is an input to stop the header yield at any given index of iteration
        # for example: if count was set to 3, then the loop below to collect header links/titles
        # would break on the third iteration.
        if count > 29: ### WRONG, MAKE MAX DYNAMIC
            count = 29
        if count < 1:
            raise ValueError('Count must be a positive integer greater than 1')

        #self._cookie_check_and_click()

        # START of the header yield code. This uses seleniums webdriver
        # to both click through and catch the header names and urls of each of the
        header_container = self.driver.find_element(By.XPATH, '/html/body/div[5]/div/div/div[1]/div/div/div/div/div/div[1]/div/nav/div/div/div/div/div[2]/div/div[1]/div/div[3]')
        headers = header_container.find_elements(By.XPATH, "./*")
        headers.pop()

        # First, get the text for the headers up to the 'more'. (Not all headers are visible immediately)
        # if the count is lower than current visible headers, this is sliced at the bottom
        categories = []
        category_links = []
        for header in headers:
            categories.append(header.text)
        categories.remove('More')
        categories = categories[:count]


        # Click through the visible headers to get urls for each one (except for 'More')
        counted = 0
        for i in range(len(headers)):
            headers[i].click()
            if i!= len(headers) - 1:
                category_links.append(self.driver.current_url)
                counted +=1
                # Break the entire function if count is met
                if counted == count:
                    return zip(categories, category_links)

            sleep(3 if self.slow_internet_speed else 1)
            # Click the 'More' header and get the elements for rest of headers whilet they're visible
            if i == len(headers) - 1:
                sleep(1.5 if self.slow_internet_speed else 0.5)
                more_menu = headers[i].find_element(By.XPATH, '//*[@id="flexible-destination-more-menu"]')
                more_headers = more_menu.find_elements(By.XPATH, "./*")
          

                # The offset means indexing goes 0, 0, 1, 2, 3, 4,... because of the nature of the 'More' column
                for j in range(-1,len(more_headers)-1):
                    if j == -1:
                        j+=1
                    # Click the 'More' header and get the elements for rest of headers whilet they're visible
                    # the difficulty with sich a dynamic page is that this has to be repeatedly done
                    more_menu = headers[i].find_element(By.XPATH, '//*[@id="flexible-destination-more-menu"]')
                    more_headers = more_menu.find_elements(By.XPATH, "./*")
                    sleep(1.5 if self.slow_internet_speed else 0.5)
                    # Get the category name from header
                    categories.append(more_headers[j].text)
                    more_headers[j].click()
                    sleep(1.5 if self.slow_internet_speed else 0.5)
                    # After clicking that header, get the corresponding header url for it
                    category_links.append(self.driver.current_url)
                    headers[i].click()
                    counted+=1
                    # Break the entire function if count is met
                    if counted == count:
                        return zip(categories, category_links)


    def __scroll(self, driver : webdriver, SCROLL_PAUSE_TIME : int):
        # Get scroll height
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait to load page
            sleep(SCROLL_PAUSE_TIME)
            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                return
            last_height = new_height


    def get_products(self, header_url : str, SCROLLING : bool = True):
        """ Returns an array of the product urls for a homepage with a certain header clicked.

        Parameters
        ----------
        header_url : str
            the url of the header to be opened by the `driver` where the corresponding products can be found.
        SCROLLING : bool , default=True
            When a header page is opened, the lazy loading of the Airbnb's website prevents all products from 
            being located. When `SCROLLING` is set to True, this calls a protected method that scrolls through the
            entire page so that every product is loaded and therefore the url can be stored. Setting to False is a
            clever way of electing to only take a sample of the products from each header page. This parameter is
            optional and defaulted to True.
        
        Returns
        -------
        product_links : np.array of str
            A numpy array of strings containing the urls for each product that has been found.
        """
        self.driver.get(header_url)
        sleep(1.5 if self.slow_internet_speed else 0.5)
        self._cookie_check_and_click()
        self.driver.execute_script("document.body.style.zoom='75%'")
        sleep(5 if self.slow_internet_speed else 2)

        # Set to FALSE when testing/sampling
        if SCROLLING:
            pause_time = 7 if self.slow_internet_speed else 3.5
            self.__scroll(self.driver, pause_time)
        for i in range(self.BATCH_ATTEMPTS):
            try:
                # Store all links for locations listed on page in array
                places_container = self.driver.find_element(By.XPATH, '//*[@id="site-content"]/div/div/div/div/div/div/div/div/div[2]/div/div/div')
                places = places_container.find_elements(By.XPATH, "./*" )
                product_links = np.array([])
                for place in places:
                    href = place.find_element(By.TAG_NAME, 'a')
                    url = f"{href.get_attribute('href')}"
                    product_links = np.append(product_links,url)
            except Exception as e:
                pass
        return product_links


    @staticmethod 
    def string_clean(text: str, str_type : str) -> str:
        """ Takes in raw text from elements on Airbnb product pages and formats them into parsable strings.

        Text data from elements in a product page on Airbnb's website come in a variety of forms not so easily 
        understandable by machines. This static method is necessary to essentially clean the text from certain elements 
        in each product page.

        Parameters
        ----------
        text : str
            The raw text data from the element from the product page.
        str_type : {'info', 'review count', 'amenities'}
            The nature of the text data differs for each element of the product webpage, thus the pythonic 
            strategem for cleaning the text data must do the same. Specifying which page element the text comes 
            from will specify which set of programmatic instructions the method needs to take in order to clean 
            the text data.
        
        Returns
        -------
        if `str_type` is 'info':
            output: list of [tuples of (str, int)]
                where the strings are labels of guests, bedrooms beds, and bathrooms, and the corresponding 
                int is their count.
        if `str_type` is 'review count`:
            output: int
                Number of reviews for product.
        if `str_type` is 'amenities':
            output: int
                Number of amenities for product.

        Raises
        ------
        ValueError
            If the inputted string for `str_type` doesn't match any of the accepted strings.
        """
        if str_type == 'info':
            output = []
            # Organises the text into a clean list of 
            # ['x guests', 'x bedrooms', 'x beds', 'x bathrooms']
            # this is much easier to be iterated over and parsed
            text = text.replace('·', '')
            text = text.split('  ')
            clean_info = []
            for i in text:
                clean_info.append(i)
            
            for val in clean_info:
                label = val.split()[1]
                # unlikely to happen, but if theres an anomaly in the site text, 
                # the certain element is ignored and this doesn't mess up the data
                if label not in ['guests', 'guest', 'bedrooms', 'bedroom',
                    'beds', 'bed', 'bathrooms' ,'bathroom', 'private bathroom']:
                    pass

                
                else:
                    # An element with a count of '1' (e.g. 1 bedroom) has no 's' on the end, which 
                    # will confuse the dictionary and dataframe. So all singular instances have an 's' added
                    if label[-1] != 's':
                        label += 's'
                    # The output is a list of tuples: [('guests', x), ('bedrooms', x) ...] 
                    output.append((label, float(val.split()[0])))
            return output
        


        elif str_type == 'review count':
            # Gets rid of brackets if they are there
            text = text.replace('(','')
            text = text.replace(')','')
            # Split up the number and reviews string into [x, 'Reviews']
            text = text.split(' ')
            output =  text[0]
            return int(output)
        

        elif str_type == 'amenities':
            # Simply filters out the numerical value in the text:
            # "Show all xx amenities"
            output = int(''.join(filter(str.isdigit, text)))
            return output

        else:
            raise ValueError('Please specify a distinct part of the page to clean. Have you checked your spelling?')


    def __scrape_product_images(self, driver : webdriver):

        images_container = driver.find_element(By.XPATH, '//*[@id="site-content"]/div/div[1]/div[1]/div[2]/div/div/div/div/div/div/div/div[1]/div')
        images = images_container.find_elements(By.TAG_NAME, 'img')


        if images is None:
            raise Exception

        sources = []
        for image in images:
            sources.append(image.get_attribute('src'))
        
        return sources
            

    def scrape_product_data(self, product_url: str, ID : uuid.uuid4, category : str, message : bool=False):
        """Gets a page of an Airbnb product and scrapes structured and unstructured data. Utilises both Selenium and BeautifulSoup.

        Parameters
        ----------
        product_url : str
            The url of the product page to be scraped
        ID : int
            The unique ID assigned to the particular product. This will be used to identify the data in a database/data lake.
        category : str
            The category name corresponding to where a product is found. This can be read on the headers tab on Airbnb's website.
        message : bool, default=False
            With the `message` flag enabled, the product scrape status will be logged to the terminal, as well as whether any
            images were saved.

        Returns
        -------
        product_dict : dict of {str : any}
            Structured data stored in the form of a dictionary containing relevant and human readable information about the product.
        image_data : list of [str, str, ...]
            A tuple of source links for the images found on Airbnb's website. These can be transformed into image files.

        """
        
        self._cookie_check_and_click()

        # Initialising default dict and adding the passed ID and 
        # category parameters
        product_dict = dict()
        product_dict['ID'] = ID
        product_dict['Category'] = category

        # Getting the product page with driver
        self.driver.get(product_url)
        sleep(3 if self.slow_internet_speed else 0.5)


        for i in range(self.BATCH_ATTEMPTS):
            try:
                image_data = self.__scrape_product_images(self.driver)
                if image_data:
                    break
                else:
                    raise Exception
            except Exception as e:
                continue

        # Getting data from page. Looped through multiple attempts 
        # to allow for errors due to elements not being loaded yet
        for j in range(self.BATCH_ATTEMPTS):
            try:

                # Product title (str)
                for i in range(self.BATCH_ATTEMPTS):
                    try:
                        title_element = self.driver.find_element(By.TAG_NAME, 'h1')
                        title = title_element.text
                        product_dict['Title'] = title_element.text
                        break
                    except Exception as e:
                        continue

                # Product Locaton (str)
                for i in range(self.BATCH_ATTEMPTS):
                    try:
                        location_elem = self.driver.find_element(By.XPATH, '//*[@id="site-content"]/div/div[1]/div[1]/div[1]/div/div/div/div/section/div[2]/div[1]/span[5]/button/span')
                        location = location_elem.text.replace(',', '')
                        product_dict['Location'] = location
                        break
                    except Exception as e:
                        continue

                # Counts for beds, bedrooms, beds and bathrooms (all int)
                for i in range(self.BATCH_ATTEMPTS):
                    try:
                        info_container = self.driver.find_element(By.XPATH, '//*[@id="site-content"]/div[1]/div/div/section/div/div/div/div[1]/ol' )
                        info = self.string_clean(
                            info_container.text, 
                            str_type = 'info')
                        for val in info:
                            product_dict[val[0]] = val[1]
                        break
                    except Exception as e:
                        continue

                # Number of Reviews (int)
                for i in range(self.BATCH_ATTEMPTS):
                    try:
                        review_elem = self.driver.find_element(By.XPATH, '//*[@id="site-content"]/div/div[1]/div[1]/div[1]/div/div/div/div/section/div[2]/div[1]/span[1]/span[3]/button')
                        reviews = self.string_clean(review_elem.text, 'review count')
                        product_dict['Review_Count'] = reviews
                        break
                    except Exception as e:
                        continue

                # Overall star rating (float)
                for i in range(self.BATCH_ATTEMPTS):
                    try:
                        rating_elem = self.driver.find_element(By.XPATH, '//*[@id="site-content"]/div/div[1]/div[1]/div[1]/div/div/div/div/section/div[2]/div[1]/span[1]/span[2]')
                        overall_rating = rating_elem.text.replace('·', '')
                        product_dict['Overall_Rate'] = float(overall_rating)
                        break
                    except Exception as e:
                        continue

                # Price per night (float)
                for i in range(self.BATCH_ATTEMPTS):
                    try:
                        price_elem = self.driver.find_element(By.XPATH, '//*[@id="site-content"]/div/div[1]/div[3]/div/div[2]/div/div/div[1]/div/div/div/div/div/div/div[1]/div[1]/div[1]/div/div/div/span[1]')
                        price_pNight = price_elem.text[1:] # Gets rid of £
                        product_dict['Price_Night'] = float(price_pNight)
                        break
                    except Exception as e:
                        continue

                # Sub ratings (list of floats)
                for i in range(self.BATCH_ATTEMPTS):
                    try:
                        subratings_container = self.driver.find_element(By.XPATH, '//*[@id="site-content"]/div/div[1]/div[4]/div/div/div/div[2]/div[2]/div/div')
                        subratings_elements = subratings_container.find_elements(By.XPATH, "./*")
                        for elem in subratings_elements:
                            subrating = elem.text.split('\n')
                            product_dict[subrating[0] + '_rate'] = subrating[1]
                        break
                    except Exception as e:
                        continue

                # How many amneties each location has (int)
                for i in range(self.BATCH_ATTEMPTS):
                    try:
                        amenities_elem = self.driver.find_element(By.XPATH, '//*[@id="site-content"]/div[5]/div/div[2]/section/div[4]/a')
                        amenities_count = self.string_clean(amenities_elem.text, 'amenities')
                        product_dict['amenities_count'] = amenities_count
                        break
                    except Exception as e:
                        continue

                # Product URL (str)
                product_dict['url'] = product_url

                # Catches if html hasn't been parsed properly due to loading lag, and re-runs the loop
                if  product_dict['Title'] == None \
                    or product_dict['Location'] == None\
                    or product_dict['url'] == None:
                    sleep(1 if self.slow_internet_speed else 0.25)
                    raise ValueError
                else:
                    break
            
            except Exception as e:
                continue

        if message:
            if image_data:
                print(f'Logged product "{title}" as {ID}. Images found: {len(image_data)}')
            else:
                print(f'Logged product "{title}" as {ID}. FAILED TO SAVE IMAGES.')
        
        return product_dict, image_data


    def scrape_all(self, sample : bool = False):
        """Crawls through the entire "I'm Feeling Lucky section" of Airbnb and collects structured and unstructured data from each product.
        
        Structured data is stored in the form of a pandas dataframe, and unstructured data (images) are stored in a dictionary of corresponding 
        product IDs as keys, and tuples of source links for each product as the values.

        Parameters
        ----------
        sample : bool, default=True
            Scraping the entirety of Airbnb's products hub is a large task. The `sample` logic, when set to true, severely restricts the number of products
            that the crawler will try to scrape, in the event that one simply wishes to only scrape a few products, or quickly test that the module is functioning.

        Returns
        -------
        df : pandas.DataFrame
            The pandas dataframe containing all of the information for each product scraped in a neat and structured fashion.
        image_dict : dict of {int : tuple of (str, str, ...)}
            Image data is stored in a dictionary of corresponding product IDs as keys, and tuples of source links for each product as the values.

        """
        # Primary key, pandas dataframe and a missing data count initialised
        #ID = 1000
        df = pd.DataFrame()
        image_dict = dict()


        # Establishing parameters to the called functions that are dependant on the boolean condition of sample
        scroll = not sample
        to_count = 2 if sample else 25

        try: 
            # Getting the zipped object of header names and urls
            categories = self.get_categories(count = to_count)

            # Iterating through each category yielded
            for header, link in categories:
                # All product links are gathered into self.product_links. 
                # When a new category is iterated, self.product_links is reassigned with the new products 
                # For a sample, scrolling is locked so only top 20 products are accounted for
                links = self.get_products(link, SCROLLING=scroll)

                # Iterating over each product url in a category
                for prod_url in links:
                    try:
                        ID = uuid.uuid4()
                        # Calling the scrape_product() function and logging data to the initialised pandas dataframe
                        product, images = self.scrape_product_data(prod_url, ID, header, message=self.messages)
                        df = df.append(product, ignore_index=True)
                        image_dict[ID] = images
       
                    except Exception as e:
                        # When a product page fails to give information, this is logged as missing data and doesn't break code
                        print(f'Error on product{ID}: {e}')
        finally:
            # Regardless of errors or interruptions, all yielded data is returned in a pandas dataframe
            self.driver.quit()
            return df, image_dict


    def _cookie_check_and_click(self):
        if self.COOKIE_CLICKED:
            return
        else:
            for i in range(self.BATCH_ATTEMPTS):
                try:
                    cookie_button = self.driver.find_element(By.XPATH, '/html/body/div[5]/div/div/div[1]/div/div[2]/section/div[2]/div[2]/button') 
                    cookie_button.click()
                    self.COOKIE_CLICKED = True
                    return
                except Exception as e:
                    pass


class Yell:
    def __init__(self,  slow_internet_speed : bool=False, config : str='default', messages : bool= False):

        self.main_url = 'https://www.yell.com/'
        self.slow_internet_speed = slow_internet_speed
        self.driver = None
        self.messages = messages
        self.COOKIE_CLICKED = False

        options = webdriver.ChromeOptions()
        if config == 'default':
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            options.add_argument("--start-maximized")
            self.driver = webdriver.Chrome(options=options)
        elif config == 'headless':
            options.add_argument('--no-sandbox')
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            options.add_argument('--log-level=3')
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument("--window-size=1920, 1200")
            options.add_argument('--disable-dev-shm-usage')
            self.driver = webdriver.Chrome(options=options)
            print('Running headless scraper. Do NOT close the program or interrupt the terminal.')
        else:
            raise ValueError(f'Configuration option "{config}" not recognised')
    
    def get_categories(self, count : int):
        # Getting the Yell url and clicking past the cookie wall
        self.driver.get(self.main_url)
    

    def _cooie_check_and_click(self):
        if self.COOKIE_CLICKED:
            return
        else:
            pass


def main():
    scraper = AirbnbScraper()
    DF, IMGS = scraper.scrape_all(True)
    print(DF)

if __name__ == '__main__':
    main()