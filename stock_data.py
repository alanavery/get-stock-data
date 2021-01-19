# Imports
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import datetime
import re
import requests
import io
import time
import random
import string
from datetime import date
from pymongo import MongoClient
from credentials import email, password
from list_of_stocks import stock_list
import pprint


client = MongoClient()
db = client['stock_data']
collection = db['current_data']


driver = webdriver.Chrome(
    '/Users/alan/Web Development/General Assembly/SEI1019/unit-04/codealong/get-stock-data/chromedriver')
time.sleep(3)


def sign_in(email=email, password=password):
    driver.get('https://wallmine.com')
    time.sleep(2)
    driver.find_element_by_xpath(
        '/html/body/main/header/div/ul/li[1]/ul/li[3]/a').click()
    time.sleep(2)
    driver.find_element_by_xpath(
        '//*[@id="new_user"]/div[5]/div[1]/div[2]/a').click()
    time.sleep(0.1)
    if 'We\'re glad you\'re back!' in driver.page_source:
        print('On sign-in page.')
        driver.find_element_by_xpath('//*[@id="user_email"]').send_keys(email)
        driver.find_element_by_xpath(
            '//*[@id="user_password"]').send_keys(password)
        time.sleep(0.1)
        driver.find_element_by_xpath(
            '//*[@id="new_user"]/div[5]/div[2]/div[1]/button').click()
        time.sleep(3)
        if 'Stock market overview' in driver.page_source:
            print('Sign-in successful.')
    else:
        print('Restart app.')


sign_in(email, password)


def change_to_float(xpath):
    if xpath:
        string = driver.find_element_by_xpath(xpath).text
        if string[0] == '$':
            if string[-1] == 'T':
                return float(string[1:-1]) * 1000000000000
            elif string[-1] == 'B':
                return float(string[1:-1]) * 1000000000
            elif string[-1] == 'M':
                return float(string[1:-1]) * 1000000
        else:
            if string[-1] == 'T':
                return float(string[:-1]) * 1000000000000
            elif string[-1] == 'B':
                return float(string[:-1]) * 1000000000
            elif string[-1] == 'M':
                return float(string[:-1]) * 1000000
    else:
        return 'N/A'


def get_data(stock_list):
    for i in range(len(stock_list)):
        stock = stock_list[i]
        print(f'{i}: {stock.get("stock_ticker")}, exchange: {stock.get("exchange")}')
        driver.get(
            f'https://wallmine.com/{stock.get("exchange")}/{stock.get("stock_ticker")}')
        time.sleep(3)
        company_name = driver.find_element_by_xpath(
            '/html/body/main/section/div[2]/div/div[1]/h1/div[2]/a').text
        current_price = driver.find_element_by_xpath(
            '/html/body/main/section/div[3]/div/div/div/div/div[2]/div/div[1]/span[1]').text
        percentage = driver.find_element_by_xpath(
            '/html/body/main/section/div[3]/div/div/div/div/div[2]/div/div[2]/div').text
        price_movement = True
        if driver.find_elements_by_class_name('badge.badge-success'):
            price_up = driver.find_elements_by_class_name(
                'badge.badge-success')[0].text
            if price_up == percentage:
                print('Price is going up.')
        elif driver.find_elements_by_class_name('badge.badge-danger'):
            price_down = driver.find_elements_by_class_name(
                'badge.badge-danger')[0].text
            if price_down == percentage:
                price_movement = False
                print('Price is going down.')
        amount_changed = float(driver.find_element_by_xpath(
            '/html/body/main/section/div[3]/div/div/div/div/div[2]/div/div[1]/span[2]').text[1:])
        market_cap = change_to_float(
            '/html/body/main/section/div[4]/div[1]/div[2]/div[1]/div[1]/table/tbody/tr[1]/td/span')
        enterprise_value = change_to_float(
            '/html/body/main/section/div[4]/div[1]/div[2]/div[1]/div[1]/table/tbody/tr[2]/td/span')
        revenue = change_to_float(
            '/html/body/main/section/div[4]/div[1]/div[2]/div[1]/div[2]/table/tbody/tr[1]/td/span')
        ebitda = change_to_float(
            '/html/body/main/section/div[4]/div[1]/div[2]/div[1]/div[2]/table/tbody/tr[2]/td/span')
        income = change_to_float(
            '/html/body/main/section/div[4]/div[1]/div[2]/div[1]/div[2]/table/tbody/tr[3]/td/span')
        # volume_values = driver.find_element_by_xpath(
        #     '/html/body/main/section/div[4]/div[1]/div[2]/div[2]/div[1]/table/tbody/tr[1]/td').text.split(' / ')
        # volume_purchased = change_to_float(volume_values[0])
        # volume_outstanding = change_to_float(volume_values[1])
        stock_object = {
            'company_name': company_name,
            'stock_ticker': stock.get('stock_ticker'),
            'exchange': stock.get('exchange'),
            'current_price': current_price,
            'percentage': percentage,
            'price_movement': price_movement,
            'amount_changed': amount_changed,
            'market_cap': market_cap,
            'enterprise_value': enterprise_value,
            'revenue': revenue,
            'ebitda': ebitda,
            'income': income,
            # 'volume_purchased': volume_purchased,
            # 'volume_outstanding': volume_outstanding,
            # 'date': date.today()
        }

        db.current_data.insert_one(stock_object)
        retrieve_stock = db.current_data.find_one(
            {'stock_ticker': stock.get('stock_ticker')})
        print(retrieve_stock)


get_data(stock_list)
