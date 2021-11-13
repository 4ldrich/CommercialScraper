import unittest
import sys
sys.path.append('../')
from Scraper.airbnb_scraper import Scraper
from bs4 import BeautifulSoup
from time import sleep


# Not in the test folder for now. Having trouble importing from parallel directories for some reason...

class ScraperTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.scraper = Scraper()
        self.product_url = 'https://www.airbnb.co.uk/rooms/23433324?category_tag=Tag%3A789&adults=1&check_in=2021-12-06&check_out=2021-12-13&federated_search_id=bd72f9fa-791d-4f7a-9357-2af7e75f2f14&source_impression_id=p3_1636829919_a7uuJaFzYS8j6Xgc&guests=1'
        self.headerpage_url = 'https://www.airbnb.co.uk/s/homes?search_mode=flex_destinations_search&date_picker_type=flexible_dates&tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_dates%5B%5D=april&flexible_trip_dates%5B%5D=december&flexible_trip_dates%5B%5D=february&flexible_trip_dates%5B%5D=january&flexible_trip_dates%5B%5D=march&flexible_trip_dates%5B%5D=november&flexible_trip_lengths%5B%5D=seven_days_starting_long_weekend&location_search=MIN_MAP_BOUNDS&search_type=filter_change&category_tag=Tag%3A789'

    def test_get_categories(self):
        pass

    def test_get_products(self):
        pass

    def test_string_clean(self):
        # Checking if the value error for an incorrect keyword is raised
        self.assertRaises(ValueError, Scraper.string_clean, 'any text', 'wrong str type input')

        # Get a sample product page data
        self.scraper.driver.get(self.product_url)
        sleep(2)
        homePage_html = self.scraper.driver.find_element_by_xpath('//*')
        homePage_html = homePage_html.get_attribute('innerHTML')
        homePage_soup = BeautifulSoup(homePage_html, 'lxml')

        # Checking if 'info' functionality produces correct output
        expected_info = [('guests', '2'), ('bedrooms', '1'), ('beds', '1'), ('bathrooms', '1')]
        actual_info = self.scraper.string_clean(homePage_soup.find('div', {'class': '_xcsyj0'}).next_sibling.text, 
                            str_type = 'info')
        self.assertEqual(expected_info, actual_info)

        # Checking if 'review count' functionality produces correct output
        expected_revs = 63
        actual_revs = self.scraper.string_clean(homePage_soup.find('span', {'class': '_142pbzop'}).text, 
                            str_type = 'review count') 
        self.assertEqual(expected_revs, actual_revs)

        # Checking if 'amenities' functionality produces correct output
        expected_amens = 57
        amenities_container = homePage_soup.find('div', class_ = 'b6xigss dir dir-ltr')
        actual_amens = self.scraper.string_clean(
            amenities_container.a.text, 
            str_type='amenities')
        self.assertEqual(expected_amens, actual_amens)

    
unittest.main(argv=[''], verbosity=0, exit=False)
