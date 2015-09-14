import re
import getpass
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from utils import remove_accents, download, create_folder

url_login = 'http://www.unipacbomdespacho.com.br/v2/'
url_academic_zone = "http://web.unipacbomdespacho.com.br/autenticaunidade/integracao/validaportalblack"


class StudentWorker():
    def __init__(self):
        try:
            self.browser = webdriver.PhantomJS()
            self.browser.set_window_size(1120, 550)
            self.wait = WebDriverWait(self.browser, 5)
        except WebDriverException:
            raise WebDriverException("Check if PhantomJS is installed")

    def close(self):
        self.browser.quit()

    def get_page_source(self):
        return BeautifulSoup(self.browser.page_source, "html.parser")

    def check_visibility(self, by, arg):
        self.wait.until(ec.visibility_of_element_located((by, arg)))

    def login(self):
        try:
            self.browser.get(url_login)
            user_edit = self.browser.find_element_by_name("user")
            user_edit.send_keys((input(r'Enter your enrollment: ')))
            pass_edit = self.browser.find_element_by_name("pass")
            pass_edit.send_keys(getpass.getpass())
            user_edit.send_keys(Keys.RETURN)
        except NoSuchElementException:
            raise NoSuchElementException("You're not connected at internet or the website is offline, try again later")

    def authenticate_academic_zone(self):
        try:
            print("Entering in academic zone... wait plz")
            self.browser.get(url_academic_zone)
            self.check_visibility(By.ID, "_22_1termCourses_noterm")
        except TimeoutException:
            print("Sorry, Academic Zone is offline, try again later.")

    def extract_classes(self):
        classes_html = self.get_page_source().find('ul', {'class': 'portletList-img courseListing coursefakeclass '})
        classes = []
        for klass in classes_html.find_all('a'):
            classes.append(
                {'href': klass.attrs['href'].strip(),
                 'class': (re.search(r'([^:]*)\(', klass.string)).group().strip()[:-1]}  # Removing Whitespaces and (
            )
        return classes

    def extract_content(self):
        classes = self.extract_classes()
        for klass in classes[1:]:  # Exclude ONLINE CLASS
            folder_name = remove_accents(klass['class'])
            create_folder(folder_name)
            print('Extracting Class: {0}'.format(klass['class']))
            self.browser.get('https://unipac-bomdespacho.blackboard.com{0}'.format(klass['href']))
            self.browser.find_element_by_id('header::0-whatsNewView::CO').click()  # Open content list
            block_class_contents = self.browser.find_element_by_id('block::0-whatsNewView::CO')
            class_contents = block_class_contents.find_elements_by_css_selector(
                "a[onclick*='nautilus_utils.actionSelected']"
            )
            i_content = 0
            for i_content in range(i_content, len(class_contents)):
                try:
                    block_classes_contents = self.browser.find_element_by_id('block::0-whatsNewView::CO')
                    class_contents = block_classes_contents.find_elements_by_css_selector(
                        "a[onclick*='nautilus_utils.actionSelected']"
                    )
                    class_contents[i_content].click()
                    self.check_visibility(By.CLASS_NAME, "individualContent-link")
                    file_link = self.browser.find_element_by_class_name('individualContent-link').get_attribute('href')
                    cookies = self.browser.get_cookies()
                    download(cookies, file_link, folder_name)
                    self.browser.back()
                    self.check_visibility(By.ID, "block::0-whatsNewView::CO")
                except TimeoutException:
                    print("Error in: {0} - {1}".format(klass['class'], klass['href']))

    def execute(self):
        self.login()
        self.authenticate_academic_zone()
        self.extract_content()
        self.close()


if __name__ == '__main__':
    studentWorker = StudentWorker()
    studentWorker.execute()