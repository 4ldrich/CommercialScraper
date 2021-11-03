
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains

class Bnbscraper:

    def __init__(self, driver, webpage):
        self.driver = driver 
        self.webpage = webpage 

        webpage = "https://www.airbnb.co.uk/"



    driver = webdriver.Chrome() 
    URL = "https://www.airbnb.co.uk/"
    driver.get(URL)
    driver.maximize_window()
    time.sleep(5)
    print(driver.title)


    # #search_location = driver.find_element_by_xpath("/html/body/div[5]/div/div/div[1]/div/div/div/div/div/div[1]/div/div/div/div/header/div/div[2]/div/div/div/div[2]/div/div/div/form/div[2]/div/div[1]/div/label/div/input")
    # click_button = driver.find_element_by_xpath("/html/body/div[5]/div/div/div[1]/div/div/div/div/div/main/div[1]/div/div/div/div/div[2]/div/div/div/div[2]/div/div[1]/div/div[2]/a/span")
    # click_button.send_keys(Keys.RETURN)
    # time.sleep(5)
    element = driver.find_element_by_xpath("/html/body/div[5]/div/div/div[1]/div/div/div/div/div/main/div[1]/div/div/div/div/div[2]/div/div/div/div[2]/div/div[1]/div/div[2]/a/span")
    driver.execute_script("arguments[0].click();", element)
    time.sleep(5)

    next_header = driver.find_element_by_xpath("/html/body/div[5]/div/div/div[1]/div/div/div/div[1]/main/div/div[1]/div/div/div/div/div/div/div/div/span/div/div[2]/div/div[1]/div/div[3]/div[2]/button")
    driver.execute_script("arguments[0].click();", next_header)
    next_header.send_keys(Keys.RETURN)
    time.sleep(5)

    next_header1 = driver.find_element_by_xpath("/html/body/div[5]/div/div/div[1]/div/div/div/div[1]/main/div/div[1]/div/div/div/div/div/div/div/div/span/div/div[2]/div/div[1]/div/div[3]/div[3]/button")
    driver.execute_script("arguments[0].click();", next_header1)
    next_header1.send_keys(Keys.RETURN)
    time.sleep(5)


    next_header2 = driver.find_element_by_xpath("/html/body/div[5]/div/div/div[1]/div/div/div/div[1]/main/div/div[1]/div/div/div/div/div/div/div/div/span/div/div[2]/div/div[1]/div/div[3]/div[4]/button")
    next_header3 = driver.find_element_by_xpath("/html/body/div[5]/div/div/div[1]/div/div/div/div[1]/main/div/div[1]/div/div/div/div/div/div/div/div/span/div/div[2]/div/div[1]/div/div[3]/div[5]/button")
    driver.execute_script("arguments[0].click(); arguments[1].click()", next_header2, next_header3)
    next_header2.send_keys(Keys.RETURN)
    time.sleep(10)
    next_header3.send_keys(Keys.RETURN)
    time.sleep(5)

    next_header4 = driver.find_element_by_xpath("/html/body/div[5]/div/div/div[1]/div/div/div/div[1]/main/div/div[1]/div/div/div/div/div/div/div/div/span/div/div[2]/div/div[1]/div/div[3]/div[6]/button")
    driver.execute_script("arguments[0].click();", next_header4)
    next_header4.send_keys(Keys.RETURN)
    time.sleep(5)

    click_more_button = driver.find_element_by_xpath("/html/body/div[5]/div/div/div[1]/div/div/div/div[1]/main/div/div[1]/div/div/div/div/div/div/div/div/span/div/div[2]/div/div[1]/div/div[3]/div[7]/button")
    driver.execute_script("arguments[0].click();", click_more_button)
    actions = ActionChains(driver)
    actions.click_and_hold(click_more_button).perform()
    click_more_button.send_keys(Keys.PAGE_DOWN, Keys.PAGE_DOWN)
    actions.release(click_more_button).perform()



    
    

    time.sleep(10)

    














    #search_text = driver.find_element_by_name("bigsearch")
    #search_location.send_keys("South Gloucestershire")
    #search_location.send_keys(Keys.RETURN)

    #click_check_in = driver.find_element_by_xpath("/html/body/div[5]/div/div/div[1]/div/div/div/div/div/div[1]/div/div/div/div/header/div/div[2]/div/div/div/div[2]/div/div/div/form/div[2]/div/div[3]/div[2]/div/div/section/div/div/div/div/div[2]/div[1]/div[1]/div/div/div/div[2]/div[2]/div/div[2]/div/table/tbody/tr[3]/td[5]/div/div")
    #click_check_in.click()
    #search_check_out = driver.find_element_by_xpath("/html/body/div[5]/div/div/div[1]/div/div/div/div/div/div[1]/div/div/div/div/header/div/div[2]/div/div/div/div[2]/div/div/div/form/div[2]/div/div[3]/div[2]/div/div/section/div/div/div/div/div[2]/div[1]/div[1]/div/div/div/div[2]/div[2]/div/div[2]/div/table/tbody/tr[3]/td[7]/div")
    #search_check_out.send_keys(Keys.RETURN)
    
    def __exit__(self, driver):
        driver.quit()


    

    '''
    link = driver.find_element_by_link_text("I’m flexible")
    link.click()

    
    try:
        element = driver(driver, 10).until(
            
        )
    '''
    

    

