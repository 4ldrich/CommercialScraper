import unittest
from unittest.main import main

from selenium.webdriver.chrome import options
import airbnb_scraper
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class BnbScraper_Test(unittest.TestCase):
   def setUp(self):
      # Why are you assigning a driver to a scraper object?
      self.driver = airbnb_scraper.Scraper

      # You dont need to do this. First, it wouldn't work because youve made self.driver a scraper object, not a webdriver,
      # but even if you assigned it correctly, this is redundant because the Scraper __init__ does this for you
      self.driver.maximize_window()

   def test_geturl(self):
      pageUrl = "https://www.airbnb.co.uk/"
      driver=self.driver
      driver.get(pageUrl)
      # Driver.title isn't an attribute
      self.assertIn("Airbnb") in driver.title
      

   def test_cookies_button_accept(self):
      # This just isn't a method. Theres no cookie_button() method in the Scraper class
      cookies_return = self.driver.cookie_button()
      self.assertTrue(cookies_return)

   



   
   #    elem = driver.find_element_by_id("button")
   #    elem.send_keys(user)
   #    elem = driver.find_element_by_id("pass")
   #    elem.send_keys(pwd)
   #    elem.send_keys(Keys.RETURN)
   def tearDown(self):
      self.driver.close()
   
# if __name__ == '__main__':
#    unittest.main()

unittest.main(argv=[""], verbosity=2, exit=False)



