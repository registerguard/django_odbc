#!/Users/jheasly/.virtualenvs/django_odbc/bin/python
# -*- coding:utf-8  -*-

import sys
import time
sys.path.append('/Users/jheasly/Development/django_odbc/django_odbc')
sys.path.append('/Users/jheasly/.virtualenvs/django_odbc/lib/python2.7/site-packages/egenix_mxodbc_django-1.2.0-py2.7-macosx-10.5-x86_64.egg')
from os import environ
from datetime import datetime
environ['DJANGO_SETTINGS_MODULE'] = 'django_odbc.settings'

'''
See
http://www.saltycrane.com/blog/2011/07/example-parsing-xml-lxml-objectify/
sftp://go.registerguard.com//rgcalendar/oper/WFA/process_feed.py
'''

import mxodbc_django
import mx.ODBC.Manager as ODBC
from mx.ODBC.Error import OperationalError
from lxml import objectify, etree

def main():
    try:
        connection = ODBC.DriverConnect('DSN=Dtnews')
        connection.encoding = 'utf-8'
        connection.stringformat = ODBC.NATIVE_UNICODE_STRINGFORMAT
        cursor = connection.cursor()
        cursor.execute('''SELECT TOP 1 storyId, storyName, created, subCategoryId, text FROM dbo.Story WHERE Story.priorityId = (SELECT priorityId FROM dbo.Priority WHERE Priority.priorityName = '05 Bulletin') 
            AND Story.created > {fn TIMESTAMPADD(SQL_TSI_HOUR,-6,CURRENT_DATE)}
            GROUP BY Story.textLength  
            ORDER BY Story.created DESC''')
        updates_list = getattr(cursor, 'fetchall', '')
        if updates_list:
           [storyId, storyName, created, subCategoryId, text] = updates_list()[0]
#         print 'STORYID:', storyId
#         print 'STORYNAME:', storyName
#         print 'CREATED:', created
#         print 'SUBCATEGORYID:', subCategoryId
#         print 'TEXT:', text
    
        cursor.close()
    except OperationalError, err:
        # log this ... 
        print err
    
    '''
    
    Sample updates_list:
    
    [(
    23913754, 
    u'US--APNewsAlert W0857', 
    <mx.DateTime.DateTime object for '2013-08-09 12:55:15.67' at 10c215738>, 
    54, 
    u'<?xml version="1.0" encoding="UTF-8"?>\n<?DTI version="1.0"?><DTGroup xmlns:dti="http://www.dtint.com/2006/Turin">\n\n\n\n<DTStory>\n\n<DTElement type_name="Headline" type="1" DTElementID="51904888" honorTypography="false" xmlns="http://www.dtint.com/2006/Turin" xmlns:x="adobe:ns:meta/">\n<text-nostyling>AP NewsAlert</text-nostyling>\n</DTElement>\n\n\n\n<DTElement type_name="Text" type="3" DTElementID="35621175" honorTypography="true" xmlns="http://www.dtint.com/2006/Turin" xmlns:x="adobe:ns:meta/">\n<text-nostyling>AP-US\u2014APNewsAlert,11<p/>AP NewsAlert<p/>WASHINGTON \u2014 Obama calls Republican effort to repeal health care law \u2018ideological fixation\u2019</text-nostyling>\n</DTElement>\n\n</DTStory>\n</DTGroup>\n'
    )]
    '''
    try:
        root = objectify.fromstring(text.encode('utf-8'))
    except (UnboundLocalError, AttributeError):
       # Log: No text element found
       root = ''
    
    last_graf = u''
    created = u''
    try:
        for x in root.DTStory.getchildren():
            if x.attrib['type_name'] == 'Text':
                # Iterate through the paragraphs of Text element and take the last one
                [last_graf for last_graf in x['{http://www.dtint.com/2006/Turin}text-nostyling'].itertext()]
                last_graf = last_graf.encode('utf-8')
    except AttributeError:
        # Log this ... 
        print 'No DTStory element found'
    if last_graf:
        print '    ', last_graf
    if created:
        print '    ', created
    
    connection.encoding = 'utf-8'
    connection.stringformat = ODBC.NATIVE_UNICODE_STRINGFORMAT
    cursor = connection.cursor()
#     print 'Before:', cursor.rowcount
    
    # Check and see what the latest entry in DT is
    cursor.execute('''SELECT top 1 * FROM dt_z_guide.apBulletin ORDER BY id DESC''')
    [(latest_id, ap_timestamp, current_string, my_timestamp)] = cursor.fetchall()
    current_string = current_string.encode('utf-8')
    print u'Most recent in DT database:', latest_id, ap_timestamp, current_string, my_timestamp
    
#     cursor.execute('''UPDATE dt_z_guide.apBulletin SET updateText = '%s', createdDateTime = '%s' WHERE ID=2''' % (last_graf, created))
#     cursor.execute('''INSERT INTO dt_z_guide.apBulletin (updateText, createdDateTime) VALUES ('WASHINGTON — US to reopen 18 of 19 embassies, consulates shuttered this week due to terrorist threat.', '2013-08-09 17:45:52.59')''')
    
    if (last_graf and current_string) and last_graf == current_string:
        print 'No CHANGE'
        # No change in update date, but we'll update logTimestamp
        cursor.execute('''UPDATE dt_z_guide.apBulletin SET logTimestamp = '%s' WHERE id = %s''' % (datetime.now().strftime('%c'), latest_id))
    else:
        cursor.execute('''INSERT INTO dt_z_guide.apBulletin (updateText, createdDateTime, logTimestamp) VALUES ('%s', '%s', '%s')''' % (last_graf.decode('utf-8'), created, datetime.now().strftime('%c')))
#     print 'After:', cursor.rowcount
    
    connection.commit()
    
    # Clean up once a day at 3:15 a.m., 'cause, why not?
    if (3, 15) == (time.localtime().tm_hour, time.localtime().tm_min):
        cursor.execute('''SELECT TOP 25 Id FROM dt_z_guide.apBulletin ORDER BY Id DESC''')
        nested_id_list = cursor.fetchall()
        id_list = [story_id[0] for story_id in nested_id_list]
        id_tuple = str(tuple(id_list))
        cursor.execute('''DELETE FROM dt_z_guide.apBulletin WHERE id NOT IN %s''' % id_tuple)
        print cursor.rowcount
        connection.commit()
    
    cursor.close()
    connection.close()

if __name__ == "__main__" : main()
