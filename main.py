#!/bin/python3
from multiprocessing.connection import wait
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
# import Action chains 
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

class InitializeSelenium:

   

    def  initialize_selenium(self):
        searchOptions = {
            "q" : "informatique",
            "l" : "Île-de-France",
            "start" : 0,
            "jt" : "apprenticeship",
            "profile_path" : "/home/meteor314/.config/google-chrome-beta/Profile 1" 
        }

        listURl = []
        i = searchOptions["start"]
        while i <=100:
            link = "https://fr.indeed.com/jobs?q="+searchOptions['q']+"&l="+searchOptions['l']+"&start="+str(i)+"&jt="+searchOptions['jt']
            i+=10
            listURl.append(link)

        options = Options()
        options.binary_location = "/usr/bin/google-chrome-beta"
        options.add_argument("user-data-dir=" + searchOptions["profile_path"])   # Path to your chrome profile
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(listURl[0])
        driver.maximize_window()
    

        easyApply = driver.find_elements(By.CLASS_NAME, value="iaIcon")
        
        for e in easyApply:
            # right click and open link in new tab
            ActionChains(driver).context_click(e).key_down(Keys.CONTROL).click(e).perform()  
            # switch to new tab
            driver.switch_to.window(driver.window_handles[1])
        
        time.sleep(600)




        


IndeedBot = InitializeSelenium() # create an instance of the class
IndeedBot.initialize_selenium() # call the method
IndeedBot.easy_job()
        