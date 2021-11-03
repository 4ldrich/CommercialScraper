import unittest
from unittest.main import main

from selenium.webdriver.chrome import options
import airbnb_scraper
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class BnbScraper_Test(unittest.TestCase):
   def setUp(self):
      self.driver = airbnb_scraper.Scraper
      self.driver.maximize_window()

   def test_geturl(self):
      pageUrl = "https://www.airbnb.co.uk/"
      driver=self.driver
      driver.get(pageUrl)
      self.assertIn("Airbnb") in driver.title
      

   def test_cookies_button_accept(self):
      #cookies function returns True when run
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



