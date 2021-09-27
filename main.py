#!/bin/python3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import datetime
import random

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
        # Getting current URL
        get_url = driver.current_url
        print(get_url)

        indeedApplyButton = driver.find_element_by_xpath('//*[@id="indeedApplyButton"]/div/span')
        indeedApplyButton.click()


        #First Page
        try :
            driver.find_element_by_xpath("/html/body/div[2]/div/div[1]/div/main/div[2]/div[2]/div/div/div[1]/div/div[1]/div[3]/div/div/div").click()
            driver.find_element_by_xpath("/html/body/div[2]/div/div/div/main/div[2]/div[2]/div/div/div[2]/div/button/span").click()
            driver.implicitly_wait(10)
        except :
            driver.find_element_by_class_name('ia-continueButton').click()
            print("An error occured, can't continue !")

        #Second Page
        try :
            """driver.find_element_by_class_name('ia-SmartApplyCard').click()
            driver.find_element_by_class_name('ia-continueButton').click()"""
            driver.find_element_by_xpath("/html/body/div[2]/div/div/div/main/div[2]/div[2]/div/div/div[2]/div/button/span").click()
            driver.implicitly_wait(10)
            time.sleep(5)
        except Exception \
                as e:
            driver.find_element_by_class_name('ia-continueButton').click()
            print("An error occured, can't continue !")
            print(e)


        #third Page
        try :
                driver.find_element_by_tag_name('textarea').send_keys("Je suis disponible dès que possible. ")
                driver.find_element_by_class_name('ia-continueButton').click()
                driver.implicitly_wait(10)
                #Page Four :
                driver.find_element_by_id('jobTitle').send_keys("Apprenti informatique ")
                driver.find_element_by_id('companyName').send_keys("Atempo")
                driver.find_element_by_class_name('ia-continueButton').click()
                driver.implicitly_wait(10)
                time.sleep(5)




                #Page Five :
                try :

                    """ scroll to the bottom of the page"""
                    js = 'window.scrollTo(0, document.documentElement.scrollHeight)'  # scroll to the bottom of the page.
                    driver.execute_script(js)
                    btnNext = driver.find_element_by_xpath('/*[@id="ia-container"]/div/div/div/main/div[2]/div[2]/div/div/div[2]/div/button')
                    driver.execute_script("arguments[0].click();", btnNext)
                    time.sleep(3)
                except  Exception as e:
                    js = 'window.scrollTo(0, document.documentElement.scrollHeight)'  # scroll to the bottom of the page.
                    driver.execute_script(js)
                    btnNext = driver.find_element_by_xpath(
                        '/*[@id="ia-container"]/div/div/div/main/div[2]/div[2]/div/div/div[2]/div/button')
                    driver.execute_script("arguments[0].click();", btnNext)
                    time.sleep(3)
                    driver.find_element_by_class_name('ia-continueButton').click()
                    print("An error occured, can't continue !")
                    print(e)
                #Page Six :
                try :
                    js = 'window.scrollTo(0, document.documentElement.scrollHeight)'  # scroll to the bottom of the page.
                    driver.execute_script(js)
                    btnNext = driver.find_element_by_xpath(
                        '/*[@id="ia-container"]/div/div/div/main/div[2]/div[2]/div/div/div[2]/div/button')
                    driver.execute_script("arguments[0].click();", btnNext)
                    time.sleep(3)
                    driver.find_element_by_xpath('//*[@id="ia-container"]/div/div/div/main/div[2]/div[2]/div/div/div[2]/div/button/span').submit() # you can close the page if you want
                    driver.implicitly_wait(5)
                except Exception as e:
                    js = 'window.scrollTo(0, document.documentElement.scrollHeight)'  # scroll to the bottom of the page.
                    driver.execute_script(js)
                    btnNext = driver.find_element_by_xpath(
                        '/*[@id="ia-container"]/div/div/div/main/div[2]/div[2]/div/div/div[2]/div/button')
                    driver.execute_script("arguments[0].click();", btnNext)
                    time.sleep(3)
                    driver.find_element_by_class_name('ia-continueButton').click()
                    print("An error occured, can't continue !")
                    print(e)

        except : # if the page four is empty
            #Page Four :
            """
            driver.find_element_by_id('jobTitle').send_keys("Apprenti informatique")
            driver.find_element_by_id('companyName').send_keys("Atempo")
            driver.find_element_by_class_name('ia-continueButton').click()"""
            driver.find_element_by_xpath("/html/body/div[2]/div/div/div/main/div[2]/div[2]/div/div/div[2]/div/button/span").click()
            driver.implicitly_wait(1)
            # Page Five :
            try:
                driver.find_element_by_xpath(
                    '//*[@id="ia-container"]/div/div/div/main/div[2]/div[2]/div/div/div[2]/div/button').click()
                driver.implicitly_wait(1)
            except Exception as e :
                driver.find_element_by_class_name('ia-continueButton').click()
                print("An error occured, can't continue !")
                print(e)
            # Page Six :
            try:
                driver.find_element_by_xpath(
                    '//*[@id="ia-container"]/div/div/div/main/div[2]/div[2]/div/div/div[2]/div/button/span').submit()  # you can close the page if you want
                driver.implicitly_wait(5)
            except Exception as e:
                driver.find_element_by_class_name('ia-continueButton').click()
                print("An error occured, can't continue !" + e)
    except Exception as e:
        print("An error occurred, can't apply")
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
        print(link)

    for i in range(0, len(links)):
        driver.execute_script('window.open("{}", "_blank");'.format(links[i]))
        driver.switch_to.window(driver.window_handles[-1]) # switch to the tab recently open
        time.sleep(1)
        print(driver.title)
        apply()
        time.sleep(1)
        # Getting current URL source code
        get_title = driver.title
        write_file(get_title, links[i])
        time.sleep(5)
        print(links[i])


# YOU MSUT NEED TO CONNECT TO ON INDEED BEFORE CONTINUE (COZ  BOT SECURITY ), YOU HAVE  30s

secs_beg = time.time()
"""
PATH = "C:\Program Files (x86)\geckodriver.exe"
driver = webdriver.Firefox(executable_path=PATH)
"""

options = Options()
path= "/home/kali/.config/google-chrome/Default" # modify with your personnal path
options.add_argument("--user-data-dir=" + path)  # you need to change the profile path (you cand find this on chrome://version/ )
chrome_path = r"./chromedriver" # || please replace by chromedriver.exe if you are on w10
options.page_load_strategy = 'normal'
driver = webdriver.Chrome(chrome_path, options = options)

driver.get('https://fr.indeed.com/jobs?q=informatique&l=%C3%8Ele-de-France&jt=apprenticeship&taxo2=eXAh-UqhTh2uUxY71DdIeQ&start=0')
driver.implicitly_wait(2)
input("Apuuyez sur un bouton pour commencer, si la page de connexion s'affiche, veuillez vous connecter puis redémarrer le script! :")
driver.maximize_window()

# ##-------------------Connexion -------------------- ## #

# ## when you 're connected
# ### get the lists of all the url  :
lists_url = []
i = 0
while i <= 100 :
    link = "https://fr.indeed.com/jobs?q=informatique&l=%C3%8Ele-de-France&jt=apprenticeship&taxo2=eXAh-UqhTh2uUxY71DdIeQ" \
           "&start=" + str(i)
    lists_url.append(link)
    i = i +10

print(lists_url)
### open all the link
driver.get(lists_url[0])
main() # main function to execute.

for list_url in lists_url[1:]:
    driver.execute_script('window.open("{}", "_blank");'.format(list_url))
    main() # main function to execute.
    """ not sure if it's really work, never tested this section !"""
    driver.switch_to.window(driver.window_handles[-1]) # switch to the tab recently open
    time.sleep(10)


start  =  0
while(start <= 100):
    start = start +10
    time.sleep(random.randint(1,6))

secs_end = time.time()
execution_time(secs_beg, secs_end)