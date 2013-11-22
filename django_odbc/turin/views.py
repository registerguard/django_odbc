import datetime, os
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
import mxodbc_django
import mx.ODBC.Manager as ODBC
from lxml import objectify, etree

def today(request):
    my_today = datetime.date.today()
    eight_digit_date = my_today.strftime("%Y-%m-%d")
    
    connection = ODBC.DriverConnect('DSN=Dtnews')
    connection.encoding = 'utf-8'
    connection.stringformat = ODBC.NATIVE_UNICODE_STRINGFORMAT
    cursor = connection.cursor()
    cursor.execute('''SELECT sty.storyId, cmsStory.Id, sty.storyname, api.pagesetname, api.letter, MIN(api.pagenum) as firstPage, totalDepth, author, origin, subcategoryid, seourl 
        FROM dbo.addbpageinfo api, dbo.storypageelements spe, dbo.story sty, dt_cms_schema.CMSStory 
        WHERE api.logicalPageId = spe.logicalPagesId 
        AND sty.storyId = spe.storyId 
        AND subCategoryId <> 0 
        AND NOT api.code = 'TMC' 
        AND sty.statusId IN (10, 1018, 1019) 
        AND cast (rundate as date) = cast ('%s' as date) 
        AND (numLines > 1 or words > 5) 
        AND (SELECT sum(isOnLayout) FROM dbo.storyelement WHERE storyid = sty.storyId) > 0 
        AND story->storyid=sty.storyid 
        GROUP BY sty.Id ORDER BY api.letter, firstPage, totalDepth DESC''' % eight_digit_date, '')
    results = cursor.fetchall()
    
    fancy_list = []
    for story_goods in results:
        # story_goods <--> [23781556, 30235242, u'a1.fishscreen.0805', u'MAIN NEWS', u'A', 1, 4072.93335, u'Josephine Woolington', u'The Register-Guard', 19528580, u'eweb-fish-screen-dam-power']
        cursor.execute('''SELECT image, fhdr.fileHeaderName FROM dt_cms_schema.CMSPicture pict, dbo.ForeignDbLink dblk, dbo.FileHeader fhdr, dbo.Story stry
            WHERE pict.fileheaderId = dblk.fileHeaderId 
            AND pict.fileheaderId = fhdr.fileHeaderId 
            AND dblk.foreignId = stry.storyId 
            AND pict.TheCMSPictureVersion = 16
            AND stry.storyId = %s''' % story_goods[0])
        im_results = cursor.fetchall()
        art_list = []
        for im_result in im_results:
            if im_result[0] and not os.path.isfile('/Users/jheasly/Development/django_odbc/django_odbc/turin/templates/turin/images/%s.jpg' % im_result[1]):
                # im_result[0] binary ooze; im_result[1] filename string
                art  = open('/Users/jheasly/Development/django_odbc/django_odbc/turin/templates/turin/images/%s.jpg' % im_result[1], 'wb')
                art.write(im_result[0])
                art.close()
                art_list.append(im_result[1])
        if art_list:
            story_goods = list(story_goods)
            story_goods.append(art_list)
        fancy_list.append(story_goods)
    
    cursor.execute('''SELECT TOP 1 storyId, storyName, created, subCategoryId, text FROM dbo.Story WHERE Story.priorityId = (SELECT priorityId FROM dbo.Priority WHERE Priority.priorityName = '05 Bulletin') 
        AND Story.created > {fn TIMESTAMPADD(SQL_TSI_HOUR,-6,CURRENT_DATE)} 
        GROUP BY Story.textLength 
        ORDER BY Story.created DESC''')
    updates_list = cursor.fetchall()
    
    if updates_list:
        [storyId, storyName, created, subCategoryId, text] = updates_list[0]
    
    try:
        root = objectify.fromstring(text.encode('utf-8'))
    except UnboundLocalError:
       # Log: No text element found
       root = ''
    
    try:
        for x in root.DTStory.getchildren():
            if x.attrib['type_name'] == 'Text':
                # Iterate through the paragraphs of Text element and take the last one
                [last_graf for last_graf in x['{http://www.dtint.com/2006/Turin}text-nostyling'].itertext()]
                update_string = last_graf.encode('utf-8')
    except AttributeError:
        # Log this ... 
        print 'No DTStory element found'
    
#     for update_item in updates_list:
#         print updates_list
#         (update_date, update_string) = update_item[2], update_item[4].split(u'\n')[6].split(u'<p/>')[1].rstrip(u'</text-nostyling>')
    cursor.close()
    
    update_date = created.strftime('%I:%M %p, %A, %b %d, %Y')
    
    return render(request, 'turin/base.html', {'list': fancy_list, 'update': (update_string, update_date),},)

def getStory(request, storyid, onLayout=None):
    connection = ODBC.DriverConnect('DSN=Dtnews')
    connection.encoding = 'utf-8'
    connection.stringformat = ODBC.NATIVE_UNICODE_STRINGFORMAT
    cursor = connection.cursor()
    if onLayout == True:
        cursor.execute('''SELECT channelText, xmlTagsId 
            FROM storyElement 
            WHERE storyId = %s 
            AND isOnLayout=1 
            AND xmltagsid IN (1, 2, 3, 4, 7, 11, 12, 13, 14, 16, 17, 18, 20, 21, 22, 23, 24, 430717) 
            AND ((SELECT count(*) FROM storyElement WHERE storyId = %s AND isOnLayout=1 AND xmltagsid =3) = 1)''' % (storyid, storyid))
    else:
        cursor.execute('''SELECT channelText, xmlTagsId 
            FROM storyElement 
            WHERE storyId = %s 
            AND xmltagsid IN (1, 2, 3, 4, 7, 11, 12, 13, 14, 16, 17, 18, 20, 21, 22, 23, 24, 430717) 
            AND ((SELECT count(*) FROM storyElement WHERE storyId = %s AND xmltagsid = 3) = 1)''' % (storyid, storyid))
    results = cursor.fetchall()
    cursor.close()
    return render(request, 'turin/story.html', {'detail_list': results, 'onLayout': onLayout},)

def welchIndex(request):
    connection = ODBC.DriverConnect('DSN=Dtnews')
    connection.encoding = 'utf-8'
    connection.stringformat = ODBC.NATIVE_UNICODE_STRINGFORMAT
    cursor = connection.cursor()
    cursor.execute('''SELECT sty.storyId, storyname, api.runDate 
        FROM dbo.AdDbPageInfo api, dbo.StoryPageElements spe, dbo.Story sty
        WHERE api.logicalPageId = spe.logicalPagesId 
        AND sty.storyId = spe.storyId 
        AND sty.storyName like '%cr.welch%' 
        GROUP BY sty.Id ORDER BY api.runDate DESC''')
    results = cursor.fetchall()
    out_result = []
    for result in results:
        result = list(result)
        result[2] = result[2].strftime('%A, %b %d, %Y')
        out_result.append(result)
    cursor.close()
#     return render(request, 'turin/columnist_index.html', {'list': results},)
    return render(request, 'turin/columnist_index.html', {'list': out_result},)

def status(request):
    '''
    An experiment to see if this date variable caches when it's outside of a 
    function.
    '''
    my_today = datetime.date.today()
    my_today_status = datetime.date.today()
    eight_digit_date_status = my_today_status.strftime("%Y-%m-%d")

    connection = ODBC.DriverConnect('DSN=Dtnews')
    connection.encoding = 'utf-8'
    connection.stringformat = ODBC.NATIVE_UNICODE_STRINGFORMAT
    cursor = connection.cursor()
    
#     for section in settings.DT_SECTIONS:
    
    cursor.execute('''SELECT st.storyId 
    FROM dt_cms_schema.Section se, dt_cms_schema.Publication pb, dt_cms_schema.PageLayout pl, dt_cms_schema.Grid gr, dt_cms_schema.Area ar, dt_cms_schema.Slot sl, dt_cms_schema.Mapping mp, dt_cms_schema.CMSStory cm, dbo.Story st 
    WHERE se.publicationID = pb.ID
    AND pl.publicationID = se.publicationID
    AND gr.pageLayoutID = pl.ID
    AND gr.ID = ar.gridID
    AND sl.areaID = ar.ID
    AND mp.slotReferenceID = sl.slotReferenceID
    AND mp.sectionID = se.%ID 
    AND cm.ID = mp.cmsStory 
    AND cm.story = st.ID
    AND pb.name = 'rg'
    AND se.name = 'local'
    AND pl.name = 'local'
    AND gr.name = 'Default'
    AND ar.name in ('Top Stories', 'Stories')
    AND mp.version = '0'
    ORDER BY ar.name DESC, mp.slotReferenceID ASC''')
    story_id_list = cursor.fetchall()
    story_id_tuple = tuple(story_id[0] for story_id in story_id_list)
    
    cursor.execute('''SELECT 
                        dbo.story.storyname, 
                        dbo.fileheader.priorityId, 
                        cmspicture.id,  
                        dbo.fileheader.fileheadername, 
                        dbo.fileheader.caption 
                    FROM 
                        dbo.story, 
                        dbo.fileheader, 
                        dbo.foreigndblink, 
                        dt_cms_schema.CMSPicture, 
                        dbo.Priority 
                    WHERE 
                        dbo.fileheader.fileheaderid = dbo.ForeignDbLink.fileheaderid 
                    AND 
                        dbo.story.storyid = dbo.foreigndblink.foreignid 
                    AND 
                        foreignDblink.fileheaderid = cmspicture.fileheaderId  
                    AND 
                        CMSPicture.TheCMSPictureVersion = 18 
                    AND 
                        Priority.priorityId = story.priorityId
                    AND 
                        dbo.story.storyid IN %s 
                    ORDER BY 
                        dbo.story.storyname, CASE fileheader.priorityId 
                                WHEN 0 THEN 1 
                                WHEN 4 THEN 2 
                                WHEN 5 THEN 3 
                                WHEN 2 THEN 4 
                                WHEN 3 THEN 5 
                                WHEN 8 THEN 6
                                WHEN 6 THEN 7
                                WHEN 7 THEN 8
                               END''' % str(story_id_tuple) )
    
    results = cursor.fetchall()
    cursor.close()
    
    '''
    Convert database result list of keyless tuples to keyed dictionary
    '''
    #
    # This is dict/zip-ping is messing with the order!
    #
    results_dict = [ dict( zip(('story_slug', 'image_priority_id', 'cms_picture_id', 'image_slug', 'caption'), result_item) ) for result_item in results ]
    
    '''
    Lookup Priority; translate from ID to string/label
    '''
    for result in results_dict:
         result['image_priority_id'] = settings.DT_MEDIA_STATUS[result['image_priority_id']]
    
    return render(request, 'turin/status.html', 
        {
            'results': results_dict, 
            'today': my_today, 
            'today_status': my_today_status, 
            'title': u'DTI Status page (linter)', 
            'story_id_list': story_id_list, 
            'settings': settings.DT_MEDIA_STATUS, 
            'results_dict_a': results_dict_a,
        })

def categories(request):
    connection = ODBC.DriverConnect('DSN=Dtnews')
    connection.encoding = 'utf-8'
    connection.stringformat = ODBC.NATIVE_UNICODE_STRINGFORMAT
    cursor = connection.cursor()
    cursor.execute('''SELECT categoryName, SubCategory.subCategoryName, SubCategory.subCategoryId from dbo.category, dbo.SubCategory where subcategory.categoryid= category.categoryid ORDER BY category.categoryName, SubCategory.subCategoryName''')
    results = cursor.fetchall()
    cursor.close()
    return render(request, 'turin/categories.html', {'results': results })

def updates(request):
    connection = ODBC.DriverConnect('DSN=Dtnews')
    connection.encoding = 'utf-8'
    connection.stringformat = ODBC.NATIVE_UNICODE_STRINGFORMAT
    cursor = connection.cursor()
    cursor.execute('''SELECT top 50 elementText, seoTitle, author, startDate, lastModTime, publishedToWebDate, unpublishedFromWebDate, storyName, story.subCategoryId, story.storyId, lastCheckedOutBy, subCategoryName, categoryName 
        FROM dbo.Story, dt_cms_schema.CMSStory, dt_cms_schema.CMSStoryPubTracking, dbo.StoryElement, dbo.subCategory, dbo.Category 
        WHERE dbo.story.id=cmsstory.story 
        AND storyElement.storyId = Story.storyId 
        AND story.priorityId=19531704 
        AND storyElement.storyElementId = 914892 
        AND subCategory.subCategoryId = story.subCategoryId 
        AND subcategory.CategoryId = category.categoryId 
        AND CMSStoryPubTracking.CMSStory = CMSStory.ID 
        ORDER BY lastModTime DESC''')
    results = cursor.fetchall()
    cursor.close()
    
    annotated_results = []
    for result in results:
        labels = (
            u'WebUpdateHeadline', 
            u'seoTitle', 
            u'author', 
            u'startDate', 
            u'lastModTime' , 
            u'publishedToWebDate', 
            u'unpublishedFromWebDate', 
            u'storyName', 
            u'subCategoryId', 
            u'storyId', 
            u'lastCheckedOutBy', 
            u'subCategoryName', 
            u'Category',
        )
        annotated_result = [zip(labels, result)]
        annotated_results += annotated_result
    
#     return render(request, 'turin/updates.html', {'results': results })
    return render(request, 'turin/updates.html', {'results': annotated_results })

def thumbnail(request, imageid):
    connection = ODBC.DriverConnect('DSN=Dtnews')
    connection.encoding = 'utf-8'
    connection.stringformat = ODBC.NATIVE_UNICODE_STRINGFORMAT
    cursor = connection.cursor()
    
    cursor.execute('''SELECT 
                        dbo.fileheader.Thumbnail 
                    FROM 
                        dbo.fileheader 
                    WHERE 
                        width > 0.0 
                    AND 
                        fileheaderId IN (%s)''' % imageid)
    
    results = cursor.fetchall()
    cursor.close()
    response = HttpResponse(results[0][0], mimetype='image/jpeg')
    return response
