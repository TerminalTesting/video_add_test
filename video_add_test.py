# -*- coding: utf-8 -*-
import unittest
import sys
import os, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from models import *

class VideoAddTest(unittest.TestCase):
    
    SITE = 'http://nsk.%s/' % os.getenv('SITE')
    ARTSOURCE = '%sartifact/' % os.getenv('BUILD_URL')
    driver = webdriver.Firefox()
    driver.implicitly_wait(30)

    HOST = os.getenv('HOST')
    PORT = os.getenv('PORT')
    SCHEMA = os.getenv('SCHEMA')
    USER = os.getenv('USER')
    PSWD = os.getenv('PSWD')

    CONNECT_STRING = 'mysql://%s:%s@%s:%s/%s?charset=utf8' %(USER, PSWD, HOST, PORT, SCHEMA)
    engine = create_engine(CONNECT_STRING, echo=False) #Значение False параметра echo убирает отладочную информацию
    metadata = MetaData(engine)
    session = create_session(bind = engine)

    os.system('find -iname \*.png -delete')

    TEST_VIDEO = {'title': 'AutoTest Video Title',
                 'description': 'AutoTest Video Description',
                 'video': '<iframe width="560" height="315" src="//www.youtube.com/embed/0keGvSjv3iw" frameborder="0" allowfullscreen></iframe>',
                 }


    def tearDown(self):
        """Удаление переменных для всех тестов. Остановка приложения"""
        
        self.driver.close()
        if sys.exc_info()[0]:   
            print sys.exc_info()[0]

    def test_video_add(self):
        cnt=0
        
        self.driver.get('%slogin' % self.SITE)
        time.sleep(5)
        self.driver.find_element_by_id('username').send_keys(os.getenv('AUTH'))
        self.driver.find_element_by_id('password').send_keys(os.getenv('AUTHPASS'))
        self.driver.find_element_by_class_name('btn-primary').click()
        time.sleep(5)
        self.driver.get('%sterminal/admin/' % self.SITE)
        time.sleep(5)
        #self.driver.find_element_by_partial_link_text(u'тестовый режим').click()
        self.driver.get('%sterminal/admin/site/terminal/cgoodsvideo/list' % self.SITE)
        self.driver.find_element_by_link_text(u'Добавить новый').click()

        #добавляем заголовок видео
        self.driver.find_element_by_css_selector('input[id*="_title"]').send_keys(self.TEST_VIDEO['title'])

        #заполняем поле description
        self.driver.find_element_by_css_selector('textarea[id*="_description"]').send_keys(self.TEST_VIDEO['description'])

        #заполняем поле с внешним кодом проигрывателя
        self.driver.find_element_by_css_selector('textarea[id*="_resultBody"]').send_keys(self.TEST_VIDEO['video'])

        #сохраняем запись
        self.driver.find_element_by_name('btn_create_and_edit').click()

        #переходим в карточку товара в админке для получения алиаса и ид
        good = self.session.query(Goods).\
               join(Goods_stat, Goods.id == Goods_stat.goods_id).\
               join(Region, Goods_stat.city_id == Region.id).\
               join(Goods_block, Goods.block_id == Goods_block.id).\
               join(Main_goods_prices, Goods.id == Main_goods_prices.goods_id ).\
               filter(Region.domain == 'nsk').\
               filter(Goods_stat.status == 1).\
               filter(Goods.overall_type == 0).\
               filter(Goods_block.delivery_type == 1).\
               filter(Main_goods_prices.price_type_guid == Region.price_type_guid).\
               filter(Main_goods_prices.price < 3000).\
               first()

        #добавляем ид товаров
        self.driver.find_element_by_link_text(u'Добавление товаров по ID').click()
        self.driver.find_element_by_name('goods[ids]').send_keys(str(good.id))
        self.driver.find_element_by_css_selector('button[type="button"]').click()

        #сохраняем запись
        self.driver.find_element_by_name('btn_update_and_edit').click()

        #находим id товара
        vid_url = self.driver.current_url
        vid_id = vid_url[vid_url.find('video/')+6:vid_url.find('/edit')]


        #переходим в публичную часть и вызываем слой с видео
        self.driver.get('%sproduct/%s/' % (self.SITE, good.alias))
        self.driver.find_element_by_class_name('movies-button').click()

        dialog = self.driver.find_element_by_class_name('ui-dialog')

        if self.TEST_VIDEO['title'] != dialog.find_element_by_class_name('title').text:
            cnt += 1
            print u'Некорректный title:'
            print u'Нужно: ', self.TEST_VIDEO['title']
            print u'На сайте: ', dialog.find_element_by_class_name('title').text
            print '*'*80

        if 'http://' + self.TEST_VIDEO['video'][self.TEST_VIDEO['video'].find('www.youtube'):self.TEST_VIDEO['video'].find('" frameborder')] != dialog.find_element_by_tag_name('iframe').get_attribute('src'):
            cnt += 1
            print u'Некорректная ссылка на видео:'
            print u'Нужно: ', 'http://' + self.TEST_VIDEO['video'][self.TEST_VIDEO['video'].find('www.youtube'):self.TEST_VIDEO['video'].find('" frameborder')]
            print u'На сайте: ', dialog.find_element_by_tag_name('iframe').get_attribute('src')
            print '*'*80

        #удаляем видео
        self.driver.get('%sterminal/admin/site/terminal/cgoodsvideo/%s/delete' % (self.SITE, vid_id))
        self.driver.find_element_by_css_selector('input[type="submit"]').click()

        self.driver.get('%slogout' % self.SITE)
        self.driver.close()

        self.driver = webdriver.Firefox()
        

        #переходим в публичную часть и вызываем слой с видео
        self.driver.get('%sproduct/%s/' % (self.SITE, good.alias))
 
        try:
            self.driver.find_element_by_class_name('movies-button')
            cnt += 1
            print u'Видео не удалилось'
            self.driver.get_screenshot_as_file('%s.png' % good.alias)
            print '*'*80

        except:
            pass

        assert cnt==0, (u'Errors:%d')%(stat)

        
        
        
       

