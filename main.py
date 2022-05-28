#!/bin/python3
from multiprocessing.connection import wait
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
# import Action chains 
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


# import applyForm
import applyForm


class InitializeSelenium:


    def __init__(self):
        self.now = datetime.now()   # current date and time         
        # dd/mm/YY H:M:S
        self.dt_string = self.now.strftime("%d/%m/%Y %H:%M:%S")  
        self.searchOptions = {
            "q" : "informatique",
            "l" : "Île-de-France",
            "start" : 0,
            "jt" : "apprenticeship",
            "end" : 100
            
        }
        self.paths = {
            "profile_path" : "/home/meteor314/.config/google-chrome/Profile 4",
            "binary_location" :  "/usr/bin/google-chrome-stable",
        }

        self.options = Options()
        self.options.binary_location = self.paths['binary_location']
        self.options.add_argument("user-data-dir=" + self.paths["profile_path"])   # Path to your chrome profile
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)

        pass   


    def  initialize_selenium(self):
        
        listURL = []
        i = self.searchOptions["start"]
        while i <= self.searchOptions["end"]:
            link = "https://fr.indeed.com/jobs?q="+self.searchOptions['q']+"&l="+self.searchOptions['l']+"&start="+str(i)+"&jt="+self.searchOptions['jt']
            i+=10
            listURL.append(link)

        self.driver.get(listURL[0]) # go to the first link of the list
        self.driver.maximize_window() 
        
        resumecount=0
        # switch to new tab for apply
        j =1
        while j< len(listURL):   # loop for all url  

            easyApply = self.driver.find_elements(By.CLASS_NAME, value="iaIcon") #link to the easy apply button
            print(len(easyApply))
            print("J : ", j)                     
            for e in easyApply:
                # right click and open link in new tab
                ActionChains(self.driver).context_click(e).key_down(Keys.CONTROL).click(e).perform()  
            i=0  
            while i< len(easyApply):
                self.driver.switch_to.window(self.driver.window_handles[-1])
                #time.sleep(2000)

                # write all logs in a file
                title = self.driver.title
                url = self.driver.current_url
                self.write_logs(url, title) 


                #Click on first button to apply


                indeedapply = self.driver.find_element(By.ID, "indeedApplyButton")
                indeedapply.click()

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
        f.write(title + "," + url + "," + self.dt_string + "\n") 
        f.close()
        pass
        
    
    def applyForm(self):
        # detect which type of form is it :
        # if it is a resume form, we need to upload a resume or we can just click on the button if we alreday registered our CV
        # if it is a job application form, we need to fill the form and click on the apply button
        print ("applyForm")

        try :
            if self.driver.find_element(By.CLASS_NAME, "ia-continueButton").is_displayed():
                applyButton = self.driver.find_element(By.CLASS_NAME, "ia-continueButton")
            
            elif self.driver.find_element(By.ID, "resume-display-buttonHeader").is_displayed():      
                cvButton = self.driver.find_element(By.ID, "resume-display-buttonHeader")

            elif self.driver.find_element(By.TAG_NAME, "textarea").is_displayed():
                availibility = self.driver.find_element(By.TAG_NAME, "textarea")
                # job application form
                availibility.send_keys("I am available from now")
                applyButton.click()

            elif self.driver.find_element(By.ID, "jobTitle").is_displayed():
                jobTitle = self.driver.find_element(By.ID, "jobTitle")
                # job application form
                jobTitle.send_keys("Web Developer as Trainee ")
                companyName = self.driver.find_element(By.ID, "companyName")
                companyName.send_keys("GFCPHARMA")                    
                applyButton.click()
            else:
                print("No button found")
                applyButton.click()
                pass


        except Exception as e:
            try:
                applyButton.click() # try to continue to apply
                print ("Apply button found")
            except:
                print("Error occured : Can't apply for this job", e) # if we can't click on the button, we can't apply for this job, close the tab and go to the next one
                self.driver.close()         
        
         
        


IndeedBot = InitializeSelenium() # create an instance of the class
IndeedBot.initialize_selenium() # call the method

        