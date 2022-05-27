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
            
        }

        paths = {
            "profile_path" : "C:/Users/thesu/AppData/Local/Google/Chrome/User Data",
            "binary_location" : "C:\Program Files\Google\Chrome\Application\chrome.exe",
            "Profile_name" : "profile-directory=Profile 1"
        }

        listURL = []
        i = searchOptions["start"]
        while i <=100:
            link = "https://fr.indeed.com/jobs?q="+searchOptions['q']+"&l="+searchOptions['l']+"&start="+str(i)+"&jt="+searchOptions['jt']
            i+=10
            listURL.append(link)

        options = Options()
        options.binary_location = paths['binary_location']
        options.add_argument("user-data-dir=" + paths["profile_path"])   # Path to your chrome profile
        options.add_argument(paths["profile_path"])
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(listURL[0])
        driver.maximize_window() 
        


        
        # switch to new tab for apply
        j =1
        while j< len(listURL):      

            easyApply = driver.find_elements(By.CLASS_NAME, value="iaIcon")
            print(len(easyApply))
            print("J : ", j)  
                   
            for e in easyApply:
                # right click and open link in new tab
                ActionChains(driver).context_click(e).key_down(Keys.CONTROL).click(e).perform()  

            i=0  
            while i< len(easyApply):
                driver.switch_to.window(driver.window_handles[-1])
                time.sleep(1)

                #Click on first button to apply
                indeedapply = driver.find_element_by_id("indeedApplyButton")
                indeedapply.click()

                time.sleep(2)
                driver.close()

                driver.switch_to.window(driver.window_handles[-1])
                i +=1  
            
            
            body = driver.find_element(By.TAG_NAME, value="body")
            body.send_keys(Keys.CONTROL + 'n')
            driver.get(listURL[j]) 
            
            # switch to new tab
            
            
            time.sleep(3)   


            j+=1


           
        
            # switch to new tab for   search easy apply
            
        
        #time.sleep(600)

IndeedBot = InitializeSelenium() # create an instance of the class
IndeedBot.initialize_selenium() # call the method

        