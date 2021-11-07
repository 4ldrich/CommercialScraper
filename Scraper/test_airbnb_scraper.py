import unittest
from airbnb_scraper import Scraper


class ScraperTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.scraper = Scraper()

    ### I'm in 2 minds about testing initialisation..... leave it for now

    def test_get_categories(self):
        pass

    def test_get_products(self):
        pass

    def test_string_clean(self):
        pass
    
unittest.main(argv=[''], verbosity=0, exit=False)
