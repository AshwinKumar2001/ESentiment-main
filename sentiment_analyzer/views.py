import re
import requests
import json
from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
import re
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
import os

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from re import sub
from decimal import Decimal

chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")

# chrome_options.add_argument("--headless")



class AmazonReview:
    def __init__(self, **kwargs):
        self.rating = kwargs['rating']
        self.title = kwargs['title']
        self.review = kwargs['review_text']
        self.author = kwargs['author']
        self.date = kwargs['date']
        self.sentiment = kwargs['sentiment_cat']
        self.g_rating = kwargs['g_rating']


def index(request):
    # template = loader.get_template('')
    a = [1, 2, 3, 4, 5]
    return render(request, 'sentiment_analyzer/sentiment.html', {'a': a})


def sentiment_check(request):
    text = request.POST.get('text')
    if text is None:
        return render(request, 'sentiment_analyzer/single.html')
    # print(type(text))
    # sent = TextBlob(text, analyzer=NaiveBayesAnalyzer())
    analyser = SentimentIntensityAnalyzer()
    analysis = analyser.polarity_scores(text)
    sentiment = ''
    if analysis['compound'] >= 0.4:
        sentiment = 'P'
    elif analysis['compound'] < 0.4 and analysis['compound'] > -0.6:
        sentiment = 'N'
    elif analysis['compound'] <= -0.6:
        sentiment = 'Neg'
    return render(request, 'sentiment_analyzer/single.html', {'t': analysis, 'text': text, 'sentiment': sentiment})


def features(request):
    return render(request, 'sentiment_analyzer/features.html')

def AmazonSG(text1):    
    driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
    driver.get('https://www.amazon.in/')
    a = driver.find_element_by_id('twotabsearchtextbox')
    a.send_keys(text1)
    a.send_keys(Keys.RETURN)
    text = "No results for"
    b = driver.current_url
    driver.get(b)

    results = True

    def MoneyToValue(monstring):
        value = Decimal(sub(r'[^\d.]', '', monstring))
        return value

    def getRNum(rstring):
        rstring = rstring.strip(' ')
        rstring = int((rstring.split(' ')[0]).replace(',',''))
        return(rstring)

    if text in driver.page_source:
        print("No results")
        results = False

    approve_name = False
    accepted = 0
    approve_no_of_reviews = False
    approve_price = False
    best_price = 0
    most_revs = 0


    if(results):
        l = driver.find_elements_by_css_selector('.a-size-medium.a-color-base.a-text-normal')
        money = driver.find_elements_by_css_selector('.a-price-whole')
        links = driver.find_elements_by_css_selector(".s-underline-text.s-underline-link-text")
        links = links[1:]
        selected = links[0].get_attribute('href')
        for n,product in enumerate(l):
            prod_name = product.get_attribute('innerHTML')
            prod_name_text = ""
            for l in range(len(text1.split(' '))):
                prod_name_text = prod_name_text + ' ' + prod_name.split(' ')[l]
            input_prod = (text1.upper()).replace(' ','')
            web_prod = (prod_name_text.upper()).replace(' ','')                                                    
            if(input_prod in web_prod):
                approve_name =  True
                selected = links[n].get_attribute('href')
                print(product.get_attribute('innerHTML'), selected)
                accepted += 1
                if (accepted>3):
                    break
            else:
                approve_name = False
    driver.get(selected)
    return(driver)


def amazon_review(request):
    positive = 0
    negative = 0
    neutral = 0
    total_g_rating = 0
    site = 'amazon'
    product_name = request.POST.get('prodname')
    driver_new = AmazonSG(product_name)
    time.sleep(5)
    
    amazon_review_dict = []

    if site == 'amazon':
        product_title = driver_new.find_element_by_css_selector('.a-size-large.product-title-word-break').get_attribute('innerHTML').strip(' ')
        # product_title = ''
        try:
            product_image = driver_new.find_element_by_css_selector('.a-dynamic-image.a-stretch-horizontal').get_attribute('src')
            
        except:
            product_image = driver_new.find_element_by_css_selector('.a-dynamic-image.a-stretch-vertical').get_attribute('src')
        #total_rating = driver_new.find_element_by_css_selector('.a-size-medium.a-color-base').get_attribute('innerHTML').split(' ')[0]
        total_rating = driver_new.find_element_by_xpath("//span[@class ='a-size-medium a-color-base']").get_attribute('innerHTML').split(' ')[0]

        reviews_link = driver_new.find_element_by_css_selector('.a-link-emphasis.a-text-bold').get_attribute('href')
        driver_new.get(reviews_link)
        # comment extraction goes here --->>>>
        rev_titles = driver_new.find_elements_by_css_selector('.a-size-base.a-link-normal.review-title.a-color-base.review-title-content.a-text-bold')
        rev_authors =  driver_new.find_elements_by_css_selector('.a-profile-name')
        #rev_ratings = driver_new.find_elements_by_css_selector('.a-icon-alt')
        rev_ratings = driver_new.find_elements_by_xpath("//div[@class ='a-section celwidget']")
        rev_texts = driver_new.find_elements_by_css_selector('.a-size-base.review-text.review-text-content > span')
        rev_dates = driver_new.find_elements_by_css_selector('.a-size-base.a-color-secondary.review-date')
        analyser = SentimentIntensityAnalyzer()

        for i,title in enumerate(rev_titles):
            title = ((rev_titles[i].get_attribute("text")).replace('\n','')).strip(' ')
            author = rev_authors[i].get_attribute('innerHTML')
            #rating = rev_ratings[i].get_attribute('innerHTML')
            rating = rev_ratings[i].find_element_by_css_selector('.a-link-normal').get_attribute('title')
            review_text = ((rev_texts[i].get_attribute('innerHTML')).replace('\n','')).strip(' ')
            date = rev_dates[i].get_attribute('innerHTML')

            analysis = analyser.polarity_scores(review_text)
            analyze_title = analyser.polarity_scores(title)
            sentiment_cat = ''
            if(analyze_title['compound'] < -0.3):
                sentiment_cat = 'Neg'
                negative += 1
                if analyze_title['compound'] > -0.5:
                    g_rating = 2
                elif analyze_title['compound'] >= -0.99:
                    g_rating = 1
            elif(analyze_title['compound'] > 0.65):
                sentiment_cat = 'P'
                positive += 1
                if analyze_title['compound'] < 0.8:
                    g_rating = 4
                elif analyze_title['compound'] <= 0.99:
                    g_rating = 5
            else:
                if analysis['compound'] >= 0.4:
                    sentiment_cat = 'P'
                    positive += 1
                    if analysis['compound'] >= 0.7:
                        g_rating = 5
                    elif analysis['compound'] >= 0.4:
                        g_rating = 4
                    elif analysis['compound'] >= 0.2:
                        g_rating = 3
                elif analysis['compound'] < 0.4 and analysis['compound'] > -0.6:
                    sentiment_cat = 'N'
                    neutral += 1
                    if analysis['compound'] >= 0.2:
                        g_rating = 3
                    elif analysis['compound'] >= -0.4:
                        g_rating = 2
                elif analysis['compound'] <= -0.6:
                    sentiment_cat = 'Neg'
                    negative += 1
                    g_rating = 1

            total_g_rating += g_rating
            amazon_review_obj = AmazonReview(author=author, rating=rating[:3], date=date, title=title,
                                             review_text=review_text, sentiment_cat=sentiment_cat, g_rating=g_rating)
            '''flipkart_review_obj = FlipkartReview(author=author, rating=rating[:3], date=date, title=title,
                                             review_text=review_text, sentiment_cat=sentiment_cat, g_rating=g_rating)'''
            amazon_review_dict.append(amazon_review_obj)
            #review_dict.append(flikart_review_obj)

        try:
            next_page = 'https://www.amazon.in' + soup.find('li', class_='a-last').a['href']
        except:
            next_page = None

        while (next_page != None):
            # comment extraction goes here --->>>>
            driver_new.get(next_page)
            soup = BeautifulSoup(driver_new.page_source, 'lxml')

            rev_titles = driver_new.find_elements_by_css_selector('.a-size-base.a-link-normal.review-title.a-color-base.review-title-content.a-text-bold')
            rev_authors =  driver_new.find_elements_by_css_selector('.a-profile-name')
            #rev_ratings = driver_new.find_elements_by_css_selector('.a-icon-alt')
            rev_ratings = driver_new.find_elements_by_xpath("//div[@class ='a-section celwidget']")
            rev_texts = driver_new.find_elements_by_css_selector('.a-size-base.review-text.review-text-content > span')
            rev_dates = driver_new.find_elements_by_css_selector('.a-size-base.a-color-secondary.review-date')

            for i,title in enumerate(rev_titles):
                title = ((rev_titles[i].get_attribute("text")).replace('\n','')).strip(' ')
                author = rev_authors[i].get_attribute('innerHTML')
                #rating = rev_ratings[i].get_attribute('innerHTML')
                rating = rev_ratings[i].find_element_by_css_selector('.a-link-normal').get_attribute('title')
                review_text = ((rev_texts[i].get_attribute('innerHTML')).replace('\n','')).strip(' ')
                date = rev_dates[i].get_attribute('innerHTML')

                analysis = analyser.polarity_scores(review_text)
                analyze_title = analyser.polarity_scores(title)
                sentiment_cat = ''

                if(analyze_title['compound'] < -0.3):
                    sentiment_cat = 'Neg'
                    negative += 1
                    if analyze_title['compound'] > -0.5:
                        g_rating = 2
                    elif analyze_title['compound'] >= -0.99:
                        g_rating = 1
                elif(analyze_title['compound'] > 0.65):
                    sentiment_cat = 'P'
                    positive += 1
                    if analyze_title['compound'] < 0.8:
                        g_rating = 4
                    elif analyze_title['compound'] <= 0.99:
                        g_rating = 5
                else:
                    if analysis['compound'] >= 0.4:
                        sentiment_cat = 'P'
                        positive += 1
                        if analysis['compound'] >= 0.7:
                            g_rating = 5
                        elif analysis['compound'] >= 0.4:
                            g_rating = 4
                        elif analysis['compound'] >= 0.2:
                            g_rating = 3
                    elif analysis['compound'] < 0.4 and analysis['compound'] > -0.6:
                        sentiment_cat = 'N'
                        neutral += 1
                        if analysis['compound'] >= 0.2:
                            g_rating = 3
                        elif analysis['compound'] >= -0.4:
                            g_rating = 2
                    elif analysis['compound'] <= -0.6:
                        sentiment_cat = 'Neg'
                        negative += 1
                        g_rating = 1

                total_g_rating += g_rating
                amazon_review_obj = AmazonReview(author=author, rating=rating[:3], date=date, title=title,
                                                 review_text=review_text, sentiment_cat=sentiment_cat, g_rating=g_rating)
                amazon_review_dict.append(amazon_review_obj)

            try:
                next_page = 'https://www.amazon.in' + soup.find('li', class_='a-last').a['href']
            except:
                next_page = None

        driver_new.quit()
        if(positive + negative + neutral) == 0:
            total_given_rating = 0
        else:
            total_given_rating = total_g_rating / (positive + negative + neutral)
        return render(request, 'sentiment_analyzer/show_table.html', {'review_dict': amazon_review_dict,
                                                                      'product_title': product_title,
                                                                      'product_image': product_image,
                                                                      'positive': positive,
                                                                      'negative': negative,
                                                                      'neutral': neutral,
                                                                      'total' : positive+neutral+negative,
                                                                      'total_rating': total_rating,
                                                                      'total_g_rating': round(total_given_rating, 1)})
