#! en/usr/bin/env python3
from selenium import webdriver
import time
import random
import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


# countdown timer

# connexion
def connexion_indeed():
    mail = "meteor3141592@gmail.com"
    pwd = "****"



# write on a csv file
def write_file(title, url):
    f = open("entreprise.csv", "a", encoding='utf8')
    current_time = (datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S"))  # time to string
    f.write(title + ";" + url + ";" + current_time + "\n")  # url, title of the post, time posted
    f.close()


# calculate time execution
def execution_time(b, e):  # begging  & endging
    print("Temps d'éxecution :", e - b)
    return e - b


def if_id_exist(id, text_to_enter) :  # find the id and enter the text on this id
    id = driver.find_element_by_id(id)
    if(len(id)>0): #if id exist
        id.clear()
        id.send_key(text_to_enter)


def apply() : ##Complete auto the form
    try :
        # Click on the indeedApplyButton to continue
        driver.find_element_by_id('indeedApplyButton').click()


        #First Page
        driver.find_element_by_id("input-firstName").send_keys("Nmae   ")
        driver.find_element_by_id("input-lastName").send_keys("Name")
        driver.find_element_by_id("input-phoneNumber").send_keys("00000")
        driver.find_element_by_id("input-location").send_keys("Paris, France")
        driver.find_element_by_class_name('ia-continueButton').click()
        driver.implicitly_wait(10)

        #Second Page
        element= driver.find_element_by_class_name('ia-SmartApplyCard').click()
        driver.find_element_by_class_name('ia-continueButton').click()
        driver.implicitly_wait(10)

        #third Page
        try :
                driver.find_element_by_tag_name('textarea').send_keys("Available")
                driver.find_element_by_class_name('ia-continueButton').click()
                driver.implicitly_wait(10)
                #Page Four :
                driver.find_element_by_id('jobTitle').send_keys("Software engeinner")
                driver.find_element_by_id('companyName').send_keys("Google")
                driver.find_element_by_class_name('ia-continueButton').click()
                driver.implicitly_wait(10)
                time.sleep(10)

                #Page Fie :
                driver.find_element_by_class_name('ia-continueButton').click()
                driver.implicitly_wait(10)
                #Page Six :
                driver.find_element_by_class_name('ia-continueButton').submit()
                driver.implicitly_wait(5)

        except : # if the page four is empty
            #Page Four :
            driver.find_element_by_id('jobTitle').send_keys("Engeinner")
            driver.find_element_by_id('companyName').send_keys("google")
            driver.find_element_by_class_name('ia-continueButton').click()
            driver.implicitly_wait(10)
            #Page Fie :
            driver.find_element_by_class_name('ia-continueButton').click()
            driver.implicitly_wait(10)
            #Page Six :
            driver.find_element_by_class_name('ia-continueButton').submit()
            time.sleep(10)
    except Exception as e:
        print("An error orccurd, can't apply")
        print(e)







def main ():

    # connect to the indeed website
    connexion_indeed()
    time.sleep(1)
    elems = driver.find_elements_by_partial_link_text("Candidature facile")
    lens = len(elems)
    # print(elems)
    links = []
    lens_link = 0
    i = 0
    # put all element on an array table links

    for e in elems:
        link = (e.get_attribute("href"))
        links.append(link)
        # print(link)

    for i in range(0, len(links)):
        driver.execute_script('window.open("{}", "_blank");'.format(links[i]))
        time.sleep(10)
        print(driver.title)
        apply()
        time.sleep(20)
        # Getting current URL source code
        get_title = driver.title
        write_file(get_title, links[i])
        time.sleep(5)
        print(links[i])


# YOU MSUT NEED TO CONNECT TO ON INDEED BEFORE CONTINUE (COZ  BOT SECURITY ), YOU HAVE  30s
secs_beg = time.time()
PATH = "C:\Program Files (x86)\geckodriver.exe"
driver = webdriver.Firefox(executable_path=PATH)


"""
PATH = 'C:\Program Files (x86)\chromedriver.exe'
driver = webdriver.Chrome(PATH)"""
driver.get('https://secure.indeed.com/account/login?hl=fr_FR')
time.sleep(60)
driver.maximize_window()

# ##-------------------Connexion -------------------- ## #

# ## when you 're connected
# ### get the lists of all the url  :
lists_url = []
i = 0
while i <= 100 :
    link = "https://fr.indeed.com/jobs?q=alternance+informatique&l=Île-de-France&start=" + str(i)
    lists_url.append(link)
    i = i +10

print(lists_url)
### open all the link
driver.get(lists_url[0])
main() # main function to execute.

for list_url in lists_url[1:]:
    driver.execute_script('window.open("{}", "_blank");'.format(list_url))
    main() # main function to execute.
    time.sleep(400)


start  =  0
while(start <= 100):
    start = start +10
    time.sleep(random.randint(25,30))

secs_end = time.time()
execution_time(secs_beg, secs_end)