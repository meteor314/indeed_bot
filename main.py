#!/bin/python3
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
import personalInfo


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
        self.options.add_argument('--no-sandbox')
        self.options.add_argument("user-data-dir=" + self.paths["profile_path"] )   # Path to your chrome profile
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



                #Click on first button to apply

                if(self.driver.find_element(By.ID, value="indeedApplyButton").is_displayed()):
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
        f.write(title + "," + url + "," + self.dt_string + "\n") 
        f.close()
        pass
        
    
    def applyForm(self):  
            # verify the current url and open the apply form

            try :
                continueButton = self.driver.find_element(By.CLASS_NAME, "ia-continueButton")
                currentURL = self.driver.current_url
                while continueButton.is_displayed():
                    if currentURL == "ttps://m5.apply.indeed.com/beta/indeedapply/form/questions/1" :
                        time.sleep(2)

                        wait = WebDriverWait(self.driver, 10)
                        availiable = wait.until(EC.element_to_be_clickable(By.TAG_NAME, values="textarea"))
                        availiable.send_keys(personalInfo.availability)

                        time.sleep(2)

                        continueButton.click()
                        continueButton = self.driver.find_element(By.CLASS_NAME, "ia-continueButton")
                        currentURL = self.driver.current_url
                    elif currentURL == "https://m5.apply.indeed.com/beta/indeedapply/form/resume" :
                        time.sleep(2)

                        print ("add letter or personnal documents")
                        wait = WebDriverWait(self.driver, 10)
                        cvButton = wait.until(EC.element_to_be_clickable((By.ID, "resume-display-buttonHeader")))
                        cvButton.click()
                        continueButton.click()

                        time.sleep(2)
                        continueButton = self.driver.find_element(By.CLASS_NAME, "ia-continueButton")
                        currentURL = self.driver.current_url

                    elif currentURL == "https://m5.apply.indeed.com/beta/indeedapply/form/work-experience":
                        time.sleep(2)
                        print ("add work experience")
                        wait = WebDriverWait(self.driver, 10)
                        jobTitle = wait.until(EC.element_to_be_clickable((By.ID, "jobTitle")))
                        jobTitle.clear()
                        time.sleep(2)
                        jobTitle.send_keys(personalInfo.jobTitle).send_keys(Keys.ENTER)
                        time.sleep(1)
                        self.driver.find_element(By.ID, "companyName").send_keys(personalInfo.companyName).send_keys(Keys.ENTER)
                        continueButton.click()

                        time.sleep(2)
                        continueButton = self.driver.find_element(By.CLASS_NAME, "ia-continueButton")
                        currentURL = self.driver.current_url

                    elif currentURL == "https://m5.apply.indeed.com/beta/indeedapply/form/review" :
                        time.sleep(2)
                        print ("review and submit")
                        goToBottomOfPage = 'window.scrollTo(0, document.documentElement.scrollHeight)'  # scroll to the bottom of the page.
                        self.driver.execute_script(goToBottomOfPage)
                        continueButton.click()

                        # write all logs in a file
                        title = self.driver.title
                        url = self.driver.current_url
                        self.write_logs(url, title) 



                        time.sleep(2)
                        continueButton = self.driver.find_element(By.CLASS_NAME, "ia-continueButton")
                        currentURL = self.driver.current_url

                    else :
                        continueButton.click()

                        time.sleep(2)
                        continueButton = self.driver.find_element(By.CLASS_NAME, "ia-continueButton")
                        currentURL = self.driver.current_url
                        time.sleep(2)
                        


                    """match (currentURL) :
                        case "https://m5.apply.indeed.com/beta/indeedapply/form/questions/1" : # personnal question or availability
                            try : 
                                print ("personnal question or availability")
                                if self.driver.find_element(By.TAG_NAME, "textarea").is_displayed() :
                                    self.driver.find_element(By.TAG_NAME, "textarea").send_keys(personalInfo.availability)                                      
                                   
                                    continueButton.click()
                            except Exception as e:
                                # continueButton does not work close this tabe and open a new one 
                                print("Exception : ", e)               
                                if (currentURL == "https://m5.apply.indeed.com/beta/indeedapply/form/questions/1") :
                                    (self.driver.close())  
                                        
                                    
                        case "https://m5.apply.indeed.com/beta/indeedapply/form/resume" : # add letter or personnal documents
                            try :
                                time.sleep(2)
                                print ("add letter or personnal documents")

                                wait = WebDriverWait(self.driver, 10)
                                element = wait.until(EC.element_to_be_clickable((By.ID, "resume-display-buttonHeader")))
                                continueButton.click()
                            except Exception as e:
                                print ("Error occured : " + str(e))
                                (self.driver.close())  
                                    
                                    
                        case "https://m5.apply.indeed.com/beta/indeedapply/form/work-experience" : # work experience
                            try :

                                time.sleep(2)
                                print ("work experience")
                                self.driver.find_element(By.ID, "jobTitle").send_keys(personalInfo.jobTitle)
                                self.driver.find_element(By.ID, "companyName").send_keys(personalInfo.companyName)
                                continueButton.click()
                            except Exception as e:
                                print ("Error occured : " + str(e))
                                (self.driver.close())
                                    
                                    
                            
                        case "https://m5.apply.indeed.com/beta/indeedapply/form/review": # review and submit
                            try :

                                time.sleep(2)
                                print ("review and submit")
                                goToBottomOfPage = 'window.scrollTo(0, document.documentElement.scrollHeight)'  # scroll to the bottom of the page.
                                self.driver.execute_script(goToBottomOfPage)
                                continueButton.click()
                            except Exception as e:
                                print ("Error occured : " + str(e))
                                (self.driver.close())
                                   
                                    
                                    


                        case _: #default case
                            print("default case")
                            currentURL = self.driver.current_url
                                #continueButton.click()

                            time.sleep(2)
                            # if the current url is the same after click on continue button close the tab
                            if (currentURL == self.driver.current_url) :
                               (self.driver.close())


                    continueButton = self.driver.find_element(By.CLASS_NAME, "ia-continueButton")
                    currentURL = self.driver.current_url
                       """             
                                
                    
            #continueButton = self.driver.find_element(By.CLASS_NAME, "ia-continueButton")
            except Exception as e:
                print ("Error occured : " + str(e))
                (self.driver.close())
                    
                    
                        

                



IndeedBot = InitializeSelenium() # create an instance of the class
IndeedBot.initialize_selenium() # call the method

        