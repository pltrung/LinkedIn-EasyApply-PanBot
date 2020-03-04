import time, random, os, csv, datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import pyautogui
from tkinter import filedialog, Tk
import tkinter.messagebox as tm
from urllib.request import urlopen
import loginGUI 

class EasyApplyBot:

    #MAX_APPLICATIONS = 500

    def __init__(self,username,password, premium, language, num_label, position, location, resumeloctn, appliedJobIDs, filename):

        print("\nWelcome to Easy Apply Bot\n")
        dirpath = os.getcwd()
        print("current directory is : " + dirpath)
        chromepath = dirpath + '/assets/chromedriver.exe'
        #foldername = os.path.basename(dirpath)
        #print("Directory name is : " + foldername)

        self.language = language
        self.premium = premium
        self.num_label = num_label
        self.appliedJobIDs = appliedJobIDs
        self.filename = filename
        self.options = self.browser_options()
        #self.browser = webdriver.Chrome()
        #self.browser = webdriver.Chrome(executable_path = "C:/cphromedriver_win32/chromedriver.exe")
        self.browser = webdriver.Chrome(options=self.options, executable_path = chromepath)
        self.wait = WebDriverWait(self.browser, 30)
        self.start_linkedin(username,password)


    def browser_options(self):
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--ignore-certificate-errors")
        #options.add_argument("user-agent=Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393")
        #options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        #options.add_argument('--disable-gpu')
        #options.add_argument('disable-infobars')
        options.add_argument("--disable-extensions")
        return options

    def start_linkedin(self,username,password):
        print("\nLogging in.....\n \nPlease wait :) \n ")
        self.browser.get("https://www.linkedin.com/login?trk=guest_homepage-basic_nav-header-signin")
        try:
            user_field = self.browser.find_element_by_id("username")
            pw_field = self.browser.find_element_by_id("password")
            login_button = self.browser.find_element_by_css_selector(".btn__primary--large")
            user_field.send_keys(username)
            user_field.send_keys(Keys.TAB)
            time.sleep(1)
            pw_field.send_keys(password)
            time.sleep(1)
            login_button.click()
        except TimeoutException:
            print("TimeoutException! Username/password field or login button not found")

    def wait_for_login(self):
        if language == "en":
             title = "Sign In to LinkedIn"
        elif language == "es":
             title = "Inicia sesión"
        elif language == "pt":
             title = "Entrar no LinkedIn"

        time.sleep(1)

        while True:
            if self.browser.title != title:
                print("\nStarting LinkedIn bot\n")
                break
            else:
                time.sleep(1)
                print("\nPlease Login to your LinkedIn account\n")

    def fill_data(self):
        self.browser.set_window_size(0, 0)
        self.browser.set_window_position(2000, 2000)
        os.system("reset")

        self.position = position
        self.location = "&location=" + location
        self.resumeloctn = resumeloctn
        print(self.resumeloctn)

    def start_apply(self):
        #self.wait_for_login()
        self.fill_data()
        self.applications_loop()

    def applications_loop(self):

        self.MAX_APPLICATIONS = int(num_label)
        count_application = 0
        count_job = 0
        jobs_per_page = 0

        os.system("reset")

        print("\nLooking for jobs.. Please wait..\n")

        self.browser.set_window_position(0, 0)
        self.browser.maximize_window()
        self.browser, _ = self.next_jobs_page(jobs_per_page)
        print("\nLooking for jobs.. Please wait..\n")
        #below was causing issues, and not sure what they are for. 
        #self.browser.find_element_by_class_name("jobs-search-dropdown__trigger-icon").click()
        #self.browser.find_element_by_class_name("jobs-search-dropdown__option").click()
        #self.job_page = self.load_page(sleep=0.5)

        while count_application < self.MAX_APPLICATIONS:

            # sleep to make sure everything loads, add random to make us look human.
            time.sleep(random.uniform(3.5, 6.9))
            self.load_page(sleep=1)

            # get job links
            links = self.browser.find_elements_by_xpath(
                    '//div[@data-job-id]'
                    )

            # get job ID of each job link
            IDs = []
            for link in links :
                temp = link.get_attribute("data-job-id")
                jobID = temp.split(":")[-1]
                IDs.append(int(jobID))
            IDs = set(IDs)

            # remove already applied jobs
            jobIDs = [x for x in IDs if x not in self.appliedJobIDs]

            if len(jobIDs) == 0:
                jobs_per_page = jobs_per_page + 25
                count_job = 0
                self.avoid_lock()
                self.browser, jobs_per_page = self.next_jobs_page(jobs_per_page)

            # loop over IDs to apply
            for jobID in jobIDs:
                count_job += 1
                self.get_job_page(jobID)

                # get easy apply button
                button = self.get_easy_apply_button ()
                if button is not False:
                    button.click()
                    self.easy_apply_application()
                    self.send_inmail()
                    count_application += 1
                else:
                    print("Position doesn't have Easy Apply Button ( or already applied )")
                    see_more = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='See more']")))
                    see_more.click()

                position_number = str(count_job + jobs_per_page)
                print(f"\nPosition {position_number}:\n {self.browser.title} \n")

                # append applied job ID to csv file
                timestamp = datetime.datetime.now()
                job_description = self.browser.title
                job_title = job_description.split('|')[0]
                company = job_description.split('|')[1]

                if premium == 'yes':
                    while True:
                        try:
                            Recruiter = self.browser.find_element_by_tag_name("dt").text
                            Recruiter_job = self.browser.find_element_by_tag_name("dd").text
                            break
                        except NoSuchElementException:
                            Recruiter = 'None'
                            Recruiter_job = 'None'
                            break
                else:
                    Recruiter = 'None'
                    Recruiter_job = 'None'


                toWrite = [company, job_title, jobID, timestamp, Recruiter, Recruiter_job]
                with open(self.filename,'a') as f:
                    writer = csv.writer(f)
                    writer.writerow(toWrite)

                # sleep every 20 applications
                if count_application % 20 == 0:
                    sleepTime = random.randint(300, 500)
                    print('\n\n****************************************\n\n')
                    print('\n\n**sleeping time****\n\n')
                    print('\n\n****************************************\n\n')
                    time.sleep (sleepTime)

                # go to new page if all jobs are done
                if count_job == len(jobIDs):
                    jobs_per_page = jobs_per_page + 25
                    count_job = 0
                    print('\n\n****************************************\n\n')
                    print('Going to next jobs page, YEAAAHHH!!')
                    print('\n\n****************************************\n\n')
                    self.avoid_lock()
                    self.browser, jobs_per_page = self.next_jobs_page(jobs_per_page)

        self.finish_apply()

    def get_job_links(self, page):
        links = []
        for link in page.find_all('a'):
            url = link.get('href')
            if url:
                if '/jobs/view' in url:
                    links.append(url)
        return set(links)

    def get_job_page(self, jobID):
        #root = 'www.linkedin.com'
        #if root not in job:
        job = 'https://www.linkedin.com/jobs/view/'+ str(jobID)
        self.browser.get(job)
        self.job_page = self.load_page(sleep=0.5)
        return self.job_page

    def got_easy_apply(self, page):
        #button = page.find("button", class_="jobs-apply-button artdeco-button jobs-apply-button--top-card artdeco-button--3 ember-view")

        button = self.browser.find_elements_by_xpath(
                    '//button[contains(@class, "jobs-apply")]/span[1]'
                    )
        EasyApplyButton = button [0]
        if EasyApplyButton.text in "Easy Apply" :
            return EasyApplyButton
        else :
            return False
        #return len(str(button)) > 4

    def get_easy_apply_button(self):
        try :
            button = self.browser.find_elements_by_xpath(
                        '//button[contains(@class, "jobs-apply")]/span[1]'
                        )
            #if button[0].text in "Easy Apply" :
            EasyApplyButton = button [0]
        except :
            EasyApplyButton = False

        return EasyApplyButton

    def easy_apply_xpath(self):
        button = self.get_easy_apply_button()
        button_inner_html = str(button)
        list_of_words = button_inner_html.split()
        next_word = [word for word in list_of_words if "ember" in word and "id" in word]
        ember = next_word[0][:-1]
        xpath = '//*[@'+ember+']/button'
        return xpath

    def click_button(self, xpath):
        triggerDropDown = self.browser.find_element_by_xpath(xpath)
        time.sleep(0.5)
        triggerDropDown.click()
        time.sleep(1)

    def send_inmail(self):
        if premium == 'yes':
            while True:
                try:
                    see_more = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='See more']")))
                    see_more.click()
                    inMail = self.browser.find_element_by_xpath("//button[contains(.,'Send InMail')]")
                    if inMail.is_displayed():
                        while True:
                            try:
                                inMail.click()
                                Recruiter = self.browser.find_element_by_tag_name("dt").text
                                Recruiter_job = self.browser.find_element_by_tag_name("dd").text
                                print("InMail Message sent to " + Recruiter)
                                print(Recruiter_job)
                                send = self.browser.find_element_by_xpath("//button[text()='Send']")
                                send.click()
                            except (NoSuchElementException, TimeoutException):
                                break
                    else:
                        print("*Position have no InMail Message*")
                        break
                except NoSuchElementException:
                    print("Position have no InMail Message!")
                    break
        else:
            print("     ")

    def easy_apply_application(self):
        while True:
            try:
                if self.browser.find_element_by_css_selector('button[aria-label = "Continue to next step"]').is_displayed():
                    while True:
                        try:
                            next_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Continue to next step']")))
                            next_button.click()
                        except (NoSuchElementException, TimeoutException):
                            break
                else:
                    break
            except NoSuchElementException:
                try :
                    #if self.browser.find_element_by_css_selector('button[aria-label = "Review your application"]').is_displayed():
                    review_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Review your application']")))
                    review_button.click()
                    submit_button = None
                    while not submit_button:
                        submit_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Submit application']")))
                    submit_button.click()
                    time.sleep(random.uniform(2, 4))
                    print("Application Complete! Congratulations!")
                    break
                except (NoSuchElementException, TimeoutException):
                    try:
                        submit_button = None
                        while not submit_button:
                            submit_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Submit application']")))
                        submit_button.click()
                        time.sleep(random.uniform(2,4))
                        print ("Application Complete! Congratulations!")
                        break
                    except(NoSuchElementException, TimeoutException):
                        print("Application cannot be done, Continue to next job!")
                        break


    #def send_resume(self):
     #   try:
      #      self.browser.find_element_by_xpath('//*[@id="file-browse-input"]').send_keys(self.resumeloctn)
       #     submit_button = None
        #   while not submit_button:
         #       if language == "en":
          #          submit_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Submit application']")))
           #     elif language == "es":
            #        submit_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Enviar solicitud']")))
             #       #submit_button = self.browser.find_element_by_xpath("//*[contains(text(), 'Enviar solicitud')]")
              #  elif language == "pt":
               #     submit_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Enviar candidatura']")))
                    #submit_button = self.browser.find_element_by_xpath("//*[contains(text(), 'Enviar candidatura')]")
            #submit_button.click()

            #time.sleep(random.uniform(1.5, 2.5))

            #After submiting the application, a dialog shows up, we need to close this dialog
            #close_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Dismiss']")))
            
            #close_button.click()

        #except :
         #   print("cannot apply to this job")
    def load_page(self, sleep=1):
        scroll_page = 0
        while scroll_page < 4000:
            self.browser.execute_script("window.scrollTo(0,"+str(scroll_page)+" );")
            scroll_page += 200
            time.sleep(sleep)

        if sleep != 1:
            self.browser.execute_script("window.scrollTo(0,0);")
            time.sleep(sleep * 3)

        page = BeautifulSoup(self.browser.page_source, "lxml")
        #page = BeautifulSoup(self.browser.page_source, "html5lib")
        return page

    def avoid_lock(self):
        x, _ = pyautogui.position()
        pyautogui.moveTo(x+200, None, duration=1.0)
        pyautogui.moveTo(x, None, duration=0.5)
        pyautogui.keyDown('ctrl')
        pyautogui.press('esc')
        pyautogui.keyUp('ctrl')
        time.sleep(0.5)
        pyautogui.press('esc')

    def next_jobs_page(self, jobs_per_page):
        self.browser.get(
            "https://www.linkedin.com/jobs/search/?f_LF=f_AL&keywords=" +
            self.position + self.location + "&start="+str(jobs_per_page))
        self.avoid_lock()
        self.load_page()
        return (self.browser, jobs_per_page)

    def finish_apply(self):
        self.browser.close()

if __name__ == '__main__':

    # set use of gui (T/F)

    useGUI = True
    #useGUI = False

    # use gui
    if useGUI == True:

        app = loginGUI.LoginGUI()
        # Gets the requested values of the height and widht.
        windowWidth = app.winfo_reqwidth()
        windowHeight = app.winfo_reqheight()

        # Gets both half the screen width/height and window width/height
        positionRight = int(app.winfo_screenwidth() / 2 - windowWidth / 2)
        positionDown = int(app.winfo_screenheight() / 3 - windowHeight / 2)
        # Positions the window in the center of the page.
        app.geometry("+{}+{}".format(positionRight, positionDown))
        app.iconbitmap('icon2.ico')
        app.title("LinkedIn EasyApply Bot")
        app.mainloop()

        #get user info info
        username=app.frames["StartPage"].username
        password=app.frames["StartPage"].password
        premium = app.frames["StartPage"].premium
        num_label = app.frames["PageSeven"].num_label
        language=app.frames["PageOne"].language
        position=app.frames["PageTwo"].position
        location_code=app.frames["PageThree"].location_code
        if location_code == 1:
            location=app.frames["PageThree"].location
        else:
            location = app.frames["PageFour"].location
        resumeloctn=app.frames["PageFive"].resumeloctn

    # no gui
    if useGUI == False:

        username = ''
        password = ''
        language = 'en'
        premium = 'yes'
        position = 'marketing'
        location = ''
        #resumeloctn = ''

    # print input
    print("\nUser Input:")

    print(
        "\nUsername:  "+ username,
        "\nPassword:  "+ password,
        "\nPremium:   "+ premium,
        "\nLanguage:  "+ language,
        "\nPosition:  "+ position,
        "\nLocation:  "+ location,
        )

    print("Let's help you find " + num_label + " jobs in " +  position + " position " +  "in " + location + "!")

    # get list of already applied jobs
    filename = 'joblist.csv'
    try:
        colnames = ['Company', 'Job Title', 'Job ID', 'Date Applied', 'Recruiter', 'Recruiter Job']
        df = pd.read_csv(filename, header=None, names = colnames)
        df.to_csv('complete_joblist.csv', index = False)
        appliedJobIDs = list (df.iloc[:,1])
    except:
        appliedJobIDs = []

    # start bot
    bot = EasyApplyBot(username, password, premium, num_label, language, position, location, resumeloctn, appliedJobIDs, filename)
    #bot = EasyApplyBot(username, password, language, position, location, resumeloctn, appliedJobIDs, filename)
    bot.start_apply()
