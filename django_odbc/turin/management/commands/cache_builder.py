# -*- coding:utf-8  -*-

import sys
sys.path.append('/Users/jheasly/Development/django_odbc')
sys.path.append('/Users/jheasly/Development/django_odbc/django_odbc')
sys.path.append('/Users/jheasly/.virtualenvs/django_odbc/lib/python2.7/site-packages')
import logging
import logging.handlers
import mxodbc_django
import mx.ODBC.Manager as ODBC
import os
from os import environ
import pprint
import requests
from cache_builder_settings import SUBCATEGORIES_TO_IGNORE
from django.core.management.base import BaseCommand, CommandError
environ['DJANGO_SETTINGS_MODULE'] = 'django_odbc.settings'

class Command(BaseCommand):
    help = u'Requests subcategory indexes pages in order to build a cache.'

    def handle(self, *args, **options):
        log_file_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)))
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)-6s: %(name)s - %(levelname)s - %(message)s')
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        fileLogger = logging.handlers.RotatingFileHandler(filename=(os.path.join(log_file_dir, 'cache_builder.log')), maxBytes=256*2048, backupCount=5) # 256x2048 = 512k
        fileLogger.setFormatter(formatter)
        logger.addHandler(fileLogger)

        connection = ODBC.DriverConnect('DSN=Dtnews')
        connection.encoding = 'utf-8'
        connection.stringformat = ODBC.NATIVE_UNICODE_STRINGFORMAT
        cursor = connection.cursor()

        cursor.execute('''SELECT subCategoryName, subCategoryId FROM SubCategory WHERE subCategoryName NOT IN %s''' % (str(SUBCATEGORIES_TO_IGNORE)))
        results = cursor.fetchall()
        subcategory_count_list = []
        for result in results:
            # ('Reviews', '153')
            print result[0].encode('utf-8'), result[1]
            cursor.execute('''SELECT COUNT(*) FROM dbo.Story WHERE Story.subCategoryId=%s AND Story.deskId <> 11''' % str(result[1]))
            # [(1,)]
            story_count = cursor.fetchall()
            self.stdout.write('%s stories in SubCategory %s' % (story_count[0][0], result[0]) )
            logger.debug('%s stories in SubCategory %s, Id: %s' % (story_count[0][0], result[0], result[1]))
            if int(story_count[0][0]):
                # Delete older cache
                # cursor.execute('''DELETE FROM custom_rg.Scraper WHERE name = 'si_%s' ''' % result[1])
                # cache_clear_results = cursor.rowcount
                # print 'cache_clear_results row count:', cache_clear_results
                # connection.commit()
                requests.get('http://registerguard.com/rg/news/categories/?subcats=%s' % result[1])
                self.stdout.write('Requesting page: http://registerguard.com/rg/news/categories/?subcats=%s' % result[1])
                logger.debug('Requesting page: http://registerguard.com/rg/news/categories/?subcats=%s\n' % result[1])
            else:
                self.stdout.write('Skipping subcategory %s. %s stories' % (result[0], story_count[0][0]))
                logger.debug('Skipping subcategory %s. %s stories\n' % (result[0], story_count[0][0]))
            # http://registerguard.com/rg/news/categories/?subcats=
            # subcategory_count_list.append()

        cursor.close()
        pprint.pprint(subcategory_count_list)
