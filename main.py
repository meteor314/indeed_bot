#!/bin/python3
from multiprocessing.connection import wait
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from tomlkit import date
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
        pass   


    def  initialize_selenium(self):
        searchOptions = {
            "q" : "informatique",
            "l" : "Île-de-France",
            "start" : 0,
            "jt" : "apprenticeship",
            "end" : 100
            
        }
        paths = {
            "profile_path" : "/home/meteor314/.config/google-chrome-beta/Profile 1",
            "binary_location" :  "/usr/bin/google-chrome-beta",
        }

        listURL = []
        i = searchOptions["start"]
        while i <= searchOptions["end"]:
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
        
        resumecount=0
        # switch to new tab for apply
        j =1
        while j< len(listURL):   # loop for all url  

            easyApply = driver.find_elements(By.CLASS_NAME, value="iaIcon")
            print(len(easyApply))
            print("J : ", j)                     
            for e in easyApply:
                # right click and open link in new tab
                ActionChains(driver).context_click(e).key_down(Keys.CONTROL).click(e).perform()  
            i=0  
            while i< len(easyApply):
                driver.switch_to.window(driver.window_handles[-1])
                #time.sleep(1)

                # write all logs in a file
                title = driver.title
                url = driver.current_url
                self.write_logs(url, title) 


                #Click on first button to apply


                indeedapply = driver.find_element(By.ID, "indeedApplyButton")
                indeedapply.click()

                # applyForm.applyForm()
                applyForm.applyForm()
                

                # close current tab
                driver.close()
                driver.switch_to.window(driver.window_handles[-1])
                i +=1  
            
            
            body = driver.find_element(By.TAG_NAME, value="body")
            body.send_keys(Keys.CONTROL + 'n')
            driver.get(listURL[j]) 
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
        applyButton = self.driver.find_element(By.CLASS_NAME, "ia-continueButton")
        applyButtonText = applyButton.text
        try :
            match applyButtonText:
                case "Continuer": # or continue  in english
                    applyButton.click()
                    return True
                case default:
                    applyButton.click()
        except Exception as e:
            try:
                applyButton.click() # try to continue to apply
            except:
                print("Error occured : Can't apply for this job", e) # if we can't click on the button, we can't apply for this job, close the tab and go to the next one
                self.driver.close()
            



        


IndeedBot = InitializeSelenium() # create an instance of the class
IndeedBot.initialize_selenium() # call the method

        