#!/bin/python3

"""
MIT License
Copyright (c) 2021 meteor314 dalek63
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from multiprocessing.connection import wait
from optparse import Values
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from tomlkit import date
from traitlets import default
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# import Action chains 
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

# import applyForm
import applyForm

class InitializeSelenium:


    def __init__(self):
        self.infoUrl =""
        self.now = datetime.now()   # current date and time         
        # dd/mm/YY H:M:S
        self.dt_string = self.now.strftime("%d/%m/%Y %H:%M:%S")  
        self.searchOptions = {
            "q" : "devops",
            "l" : "Île-de-France",
            "start" : 0,
            "jt" : "apprenticeship",
            "end" : 100
            
        }
        self.paths = {
            "profile_path" : "/home/meteor314/.config/google-chrome/Profile 4",
            "binary_location" :  "/opt/google/chrome/google-chrome"
        }
        

        self.options = Options()
        self.options.binary_location = self.paths['binary_location']
        
        self.options.add_argument("user-data-dir=" + self.paths["profile_path"] )   # Path to your chrome profile
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)
        #time.sleep(75)
        pass 

    # verify if we find JSON web token, if yes, we apply else user is not connected yet, send an alert with JS to the user.
    def isConnected (self):
        cookies = self.driver.get_cookie("PPID") # returns list of dicts
        # {'domain': '.indeed.com', 'expiry': 1687703185, 'httpOnly': True, 'name': 'PPID', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': '""'}
        login_status = False
        for cookie in cookies :
            print(cookies["value"])
            if not cookies["value"] == '\"\"': #check if the value is diffrent from 'value': '""'
                login_status =  True
                break
        print(login_status)          

        if not  login_status:
            self.driver.execute_script("alert('Please connect to Indeed first. Do not Forget to upload your CV and restrat this program :>')")
            print ('User is not connected :')
            time.sleep(120)
            self.driver.quit()
       

    def  initialize_selenium(self):
     
        listURL = []
        i = self.searchOptions["start"]
        while i <= self.searchOptions["end"]:
            link = "https://fr.indeed.com/jobs?q="+self.searchOptions['q']+"&l="+self.searchOptions['l']+"&start="+str(i)+"&jt="+self.searchOptions['jt']
            i+=10
            listURL.append(link)

        self.driver.get(listURL[0]) # go to the first link of the list
        self.driver.maximize_window() 
        self.driver.implicitly_wait(10)


        # verify if the user is connected to indeed
        self.isConnected()       

        resumecount=0
        # switch to new tab for apply
        j =1
        while j< len(listURL):   # loop for all url  

            easyApply = self.driver.find_elements(By.CLASS_NAME, value="iaIcon") #link to the easy apply button
            print("Apply with indeed available in this page : ", len(easyApply))                     
            for e in easyApply:
                # right click and open link in new tab
                ActionChains(self.driver).context_click(e).key_down(Keys.CONTROL).click(e).perform()  
            i=0  
            while i< len(easyApply):
                self.driver.switch_to.window(self.driver.window_handles[-1])
                #time.sleep(2000)



                #Click on first button to apply

                if(self.driver.find_element(By.ID, value="indeedApplyButton").is_displayed()):
                    self.infoUrl = self.driver.current_url
                    self.driver.find_element(By.ID, value="indeedApplyButton").click()
                    time.sleep(2)

                    # apply form
                    self.applyForm() 

                # close current tab
                #self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[-1])
                i +=1  
            
            
            body = self.driver.find_element(By.TAG_NAME, value="body")
            body.send_keys(Keys.CONTROL + 'n') # open new tab
            self.driver.get(listURL[j]) 
            j+=1


     
    # write all logs in a file 
    def write_logs(self, url, title ):
        f = open("logs.txt", "a")
        f.write(title + " , " + url + " , " + self.dt_string + "\n") 
        f.close()
        pass
        
    
    def applyForm(self):  
            # verify the current url and open the apply form

            try :
                continueButton = self.driver.find_element(By.CLASS_NAME, "ia-continueButton")
                currentURL = self.driver.current_url
                while continueButton.is_displayed():
                    if "questions" in currentURL :                     
                        questionsURL = self.driver.current_url
                        time.sleep(2)                   

                        continueButton.click()

                        time.sleep(2)

                        continueButton = self.driver.find_element(By.CLASS_NAME, "ia-continueButton")
                        currentURL = self.driver.current_url
                        #verify the current url, if the currentURL is same as the questionsURL, then the form contains some obligatory fields, we can close the tab and continue to another job
                        if questionsURL == currentURL:
                            self.driver.close()
                            self.driver.switch_to.window(self.driver.window_handles[-1])
                            print("mandatory fields, can not continue, switch to another job ...")
                            break
                    elif "resume" in currentURL :
                        time.sleep(2)


                        print ("add letter or personnal documents")
                        wait = WebDriverWait(self.driver, 10)
                        cvButton = wait.until(EC.element_to_be_clickable((By.ID, "resume-display-buttonHeader")))
                        cvButton.click()
                        continueButton.click()

                        time.sleep(2)
                        continueButton = self.driver.find_element(By.CLASS_NAME, "ia-continueButton")
                        currentURL = self.driver.current_url
                        

                    elif "review" in currentURL: # review
                        time.sleep(2)
                        print ("review and submit")
                        goToBottomOfPage = 'window.scrollTo(0, document.documentElement.scrollHeight)'  # scroll to the bottom of the page.
                        self.driver.execute_script(goToBottomOfPage)
                        continueButton.click()

                        # write all logs in a file
                        title = self.driver.title
                        url = self.infoUrl
                        self.write_logs(url, title) 

                        time.sleep(2)
                        self.driver.close()
                        self.driver.switch_to.window(self.driver.window_handles[-1])

                        time.sleep(2)
                        print("Apply send :)")

                        break
                    else :
                        continueButton.click()

                        time.sleep(2)
                        continueButton = self.driver.find_element(By.CLASS_NAME, "ia-continueButton")
                        currentURL = self.driver.current_url
                        time.sleep(2)
                    
                                
                    
            #continueButton = self.driver.find_element(By.CLASS_NAME, "ia-continueButton")
            except Exception as e:

                continueButton.click()
                URL = self.driver.current_url

                time.sleep(2)
                continueButton = self.driver.find_element(By.CLASS_NAME, "ia-continueButton")
                currentURL = self.driver.current_url
                time.sleep(2)
                URL2 = self.driver.current_url
                if URL == URL2:
                    print ("Error occured : " + str(e))
                    (self.driver.close())
                    
                    
                        

                



IndeedBot = InitializeSelenium() # create an instance of the class
IndeedBot.initialize_selenium() # call the method

        
