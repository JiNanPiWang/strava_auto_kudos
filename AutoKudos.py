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

    def run(self):
        self.driver.get(self.url)
        self.max_screen()
        time.sleep(1000)
