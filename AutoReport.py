from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import time
import re


class Browser():
    def __init__(self, cardnumber, passcode):
        
        self.browser = webdriver.Chrome()
        self.username = cardnumber
        self.password = passcode

        self.login_url = "http://ehall.seu.edu.cn/new/index.html"
        self.main_page = "http://ehall.seu.edu.cn/amp3/index.html#/home"

    def login(self):
        '''登录网上办事大厅'''
        self.browser.get(self.login_url)

        # 等待加载登录按钮
        login_button = WebDriverWait(self.browser, 5).until(
            expected_conditions.element_to_be_clickable((By.XPATH, '//*[@id="ampHasNoLogin"]')))
        login_button.click()

        # 切换url至登录页面（不知有无更好方法？）
        self.browser.get(self.get_current_url())

        # 执行登录
        username_input = WebDriverWait(self.browser, 5).until(
            expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="username"]')))
        password_input = self.browser.find_element(
            By.XPATH, '//*[@id="password"]')
        student_login_button = self.browser.find_element(
            By.XPATH, '//*[@id="xsfw"]')
        username_input.send_keys(self.username)
        password_input.send_keys(self.password)
        time.sleep(1)
        student_login_button.click()

        if (self.get_current_url() == "https://newids.seu.edu.cn/authserver/login?service=https://newids.seu.edu.cn/authserver/login2.jsp"):
            raise Exception()

    def get_page_source(self, url):
        '''获取目标页面的源码'''
        return self.browser.page_source

    def get_current_url(self):
        '''获取当前url'''
        return str(self.browser.current_url)

    def daily_report(self):
        '''信息化自动填报'''
        self.browser.get(self.main_page)
        self.function_search("全校师生每日健康申报系统")
        # 切换为新窗口
        handles = self.browser.window_handles
        self.browser.switch_to_window(handles[1])
        self.browser.get(self.get_current_url())

        # 点击"新增"按钮
        add_button = WebDriverWait(self.browser, 15).until(
            expected_conditions.element_to_be_clickable((By.XPATH, '//*[@data-action="add"]')))
        add_button.click()
        # 自动填报
        save_button = WebDriverWait(self.browser, 10).until(
            expected_conditions.element_to_be_clickable((By.XPATH, '//*[@id="save"]')))
        daily_temperature_input = WebDriverWait(self.browser, 10).until(
            expected_conditions.presence_of_element_located((By.XPATH, '//*[@data-caption="当天晨检体温"]')))
        daily_temperature_input.send_keys("37")
        save_button.click()
        # 进行确认
        self.browser.switch_to_default_content()
        confirm_button = WebDriverWait(self.browser, 5).until(expected_conditions.element_to_be_clickable(
            (By.XPATH, '//*[@class="bh-dialog-btn bh-bg-primary bh-color-primary-5"]')))
        confirm_button.click()

        time.sleep(1)
        # 关闭新窗口
        self.browser.close()
        # 切换为旧窗口
        self.browser.switch_to_window(handles[0])

    def function_search(self, function):
        '''
        用于在搜索栏中定位功能
        会打开新选项卡
        '''
        self.browser.get(self.main_page)
        # 打开搜索栏
        search_column = WebDriverWait(self.browser, 15).until(
            expected_conditions.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[1]/div/div[2]/div[1]')))
        search_column.click()

        # 进行指定功能的搜索
        search_input = self.browser.find_element(
            By.XPATH, '//*[@id="app"]/div[1]/div/div[2]/div[1]/div[1]/input')
        search_button = self.browser.find_element(
            By.XPATH, '//*[@id="app"]/div[1]/div/div[2]/div[1]/div[1]/button')
        search_input.send_keys(function)
        search_button.click()
        # 进入首结果
        result_button = WebDriverWait(self.browser, 5).until(expected_conditions.presence_of_element_located(
            (By.XPATH, '//*[@id="app"]/div[1]/div/div[2]/div[2]/div[1]/div/div[1]/span/div[1]/div[2]/a')))
        result_button.click()

    def close(self):
        self.browser.close()

    def quit(self):
        self.browser.quit()

def info_analyse(info, cases):
    if (cases == 0):
        return info[:9]
    if (cases == 1):
        return re.search(" (.+?) ", info).group().strip()
    if (cases == 2):
        return info[-1:]

fopen = open("C2P.txt", "r")
userlist = fopen.readlines()

for i in range(len(userlist)):
    cardnumber = info_analyse(userlist[i].strip("\n"), 0)
    password = info_analyse(userlist[i].strip("\n"), 1)
    case = info_analyse(userlist[i].strip("\n"), 2)

    repoter = Browser(cardnumber, password)
    try:
        repoter.login()
    except:
        repoter.quit()
        print(str(cardnumber) + " Failed: Wrong Password.")
        continue
    try:
        repoter.daily_report()
    except:
        repoter.quit()
        print(str(cardnumber) + " Failed: Has Reported.")
        continue
    repoter.close()
    print(str(cardnumber) + " Success.")
    
