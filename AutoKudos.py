import json
import time
import platform
from datetime import datetime

import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class AutoKudos:
    def __init__(self, url):
        self.url = url
        self.os_type = platform.system()
        self.current_window_handle = None

        chrome_options = webdriver.ChromeOptions()
        edge_options = webdriver.EdgeOptions()
        if self.os_type == 'Linux':  # Linux 系统
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            self.driver = webdriver.Chrome(options=chrome_options)
        else:
            edge_options.add_argument("--mute-audio")
            self.driver = webdriver.Edge(options=edge_options)

        self.wait = WebDriverWait(self.driver, 10)

    def max_screen(self):
        # 窗口最大化
        self.driver.maximize_window()
        # 设置窗口大小
        # self.driver.set_window_size(1300, 800)
        # print('调整前尺寸:', self.driver.get_window_size())

    def get_account(self):
        try:
            with open('credentials.json') as f:
                data = json.load(f)
                email = data['email']
                password = data['password']
        except FileNotFoundError:
            print('Please create credentials.json file with your email and password.')
            exit(1)
        return email, password

    def login(self, max_attempts=3, retry_interval=10):
        attempts = 0
        while attempts < max_attempts:
            if self.try_to_login():
                return True
            else:
                print("Login attempt %d failed. Retrying in %d seconds." % (attempts + 1, retry_interval))
                time.sleep(retry_interval)
                attempts += 1

        print("Max login attempts reached. Exiting.")
        return False

    def try_to_login(self):
        email, password = self.get_account()
        # 登录
        email_field = self.driver.find_element(By.ID, 'email')
        email_field.send_keys(email)

        password_field = self.driver.find_element(By.ID, 'password')
        password_field.send_keys(password)

        login_button = self.driver.find_element(By.ID, 'login-button')
        login_button.click()

        # 等待登录成功后页面的元素出现（一个class为feed-ui的元素）
        try:
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'feed-ui'))
            )
            print("Login successfully in %s" % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            return True
        except TimeoutError:
            print("Login timeout in %s" % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            return False

    def scroll_to_bottom(self):
        while True:
            # 滚动到页面底部
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # 等待一段时间，让页面加载
            time.sleep(2)

            # 检查页面是否在刷新
            if not self.is_page_refreshing():
                break

            # 检查是否出现了特定class，表示没有更多内容了
            if not self.is_page_refreshing():
                print("Reached the end of the feed. Exiting scroll.")
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                break

    def is_page_refreshing(self):
        # 通过检查页面的加载状态来确定是否在刷新
        return self.driver.execute_script("return document.readyState") == "complete"

    def run(self):
        self.driver.get(self.url)
        self.max_screen()
        self.login()
        # 在登录成功后，开始滚动页面
        self.scroll_to_bottom()
        time.sleep(1000)
