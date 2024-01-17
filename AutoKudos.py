import json
import time
import platform
from datetime import datetime
import pdb

import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException


class AutoKudos:
    def __init__(self, url):
        self.athlete_name = None
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

    def login(self, max_attempts=10, retry_interval=20):
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
            WebDriverWait(self.driver, 240).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'feed-ui'))
            )
            print("Login successfully in %s" % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            return True
        except TimeoutError:
            print("Login timeout in %s" % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            return False

    # TODO：可能有时候要往上翻一点，才能刷新
    def scroll_to_bottom(self):
        print_interval = 60  # 设置输出间隔为60秒
        print_counter = -2

        while True:
            # 计数器递增
            print_counter += 2  # 假设每次迭代耗时2秒
            if print_counter >= print_interval:
                print("Scroll to page bottom in %s" % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

            if print_counter == 240:
                print("Scroll for 120 seconds, stop scrolling now.")
                break

            # 滚动到页面底部
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # 等待一段时间，让页面加载
            time.sleep(2)

            # 检查页面是否在刷新
            if not self.is_page_refreshing():
                break

            # 检查是否出现了特定class，表示没有更多内容了
            if self.is_no_entries_class_present():
                print("Reached the end of the page in %s" % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                break

    def is_page_refreshing(self):
        # 通过检查页面的加载状态来确定是否在刷新
        return self.driver.execute_script("return document.readyState") == "complete"

    def is_no_entries_class_present(self):
        # 检查是否存在特定class，表示没有更多内容了
        try:
            self.driver.find_element(By.CLASS_NAME, '------packages-feed-ui-src-Feed__no-entries--EiZWe')
            return True
        except selenium.common.exceptions.NoSuchElementException:
            return False

    def scroll_to_top(self):
        # 滚动到页面顶部
        print("Scroll to page top in %s" % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        self.driver.execute_script("window.scrollTo(0, 0);")

    # TODO：增加点击时的信息，比如点了谁的赞
    def kudos_all(self):
        # 获取所有指定class的元素
        entry_containers = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="kudos_button"]')
        # 逐个点击每个元素中的button
        for button in entry_containers:
            button.click()

            try:
                # 等待弹窗出现（可根据实际情况调整等待时间）
                WebDriverWait(self.driver, 2).until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, '------packages-ui-Modal-Modal-module__closeButton--fjdqh'))
                )
                # 获取弹窗中的关闭按钮并点击
                close_button = self.driver.find_element(By.CLASS_NAME,
                                                        '------packages-ui-Modal-Modal-module__closeButton--fjdqh')
                close_button.click()

            except TimeoutException:
                # 弹窗未出现，继续执行下一个按钮的点击操作
                print("Successfully giving a kudos in %s!" % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    def get_athlete_name(self):
        try:
            # 使用XPath定位<h2>元素
            h2_element = self.driver.find_element(By.XPATH, '//h2[@data-testid="dashboard-athlete-name"]')
            # 获取元素的文本内容
            athlete_name = h2_element.text
            return athlete_name

        except Exception as e:
            print("athlete name not found, error: %s" % e)
            return None

    def run(self):
        print("Start running program in %s!" % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        self.driver.get(self.url)
        self.max_screen()
        self.login()
        # 在登录成功后，开始滚动页面
        self.athlete_name = self.get_athlete_name()
        self.scroll_to_bottom()
        self.scroll_to_top()
        self.kudos_all()
        print("All kudos are given! Program over in %s!" % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        time.sleep(60)
