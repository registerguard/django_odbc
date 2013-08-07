import datetime, os
from django.shortcuts import render
import mxodbc_django
import mx.ODBC.Manager as ODBC

def today(request):
    today = datetime.date.today()
    eight_digit_date = today.strftime("%Y-%m-%d")
    connection = ODBC.DriverConnect('DSN=Dtnews')
    connection.encoding = 'utf-8'
    connection.stringformat = ODBC.NATIVE_UNICODE_STRINGFORMAT
    cursor = connection.cursor()
    cursor.execute('''SELECT sty.storyId, cmsStory.Id, sty.storyname, api.pagesetname, api.letter, api.pagenum, totalDepth, author, origin, subcategoryid, seourl 
        FROM dbo.addbpageinfo api, dbo.storypageelements spe, dbo.story sty, dt_cms_schema.CMSStory 
        WHERE api.logicalPageId = spe.logicalPagesId 
        AND sty.storyId = spe.storyId 
        AND subCategoryId <> 0 
        AND NOT api.code = 'TMC' 
        AND (sty.statusId = 1018 or sty.statusId = 1019 or sty.statusId = 10) 
        AND cast (rundate as date) = cast ('%s' as date) 
        AND (numLines > 1 or words > 5) 
        AND (SELECT sum(isOnLayout) FROM dbo.storyelement WHERE storyid = sty.storyId) > 0 
        AND story->storyid=sty.storyid 
        GROUP BY sty.Id ORDER BY api.letter, api.pageNum,totalDepth DESC''' % eight_digit_date, '')
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
    
    for update_item in updates_list:
        clean_update_item = update_item[4].split('\n')[6].split('<p/>')[1].rstrip('</text-nostyling>')
    
    cursor.close()
    
    return render(request, 'turin/base.html', {'list': fancy_list, 'update': clean_update_item},)

def getStory(request, storyid):
    connection = ODBC.DriverConnect('DSN=Dtnews')
    connection.encoding = 'utf-8'
    connection.stringformat = ODBC.NATIVE_UNICODE_STRINGFORMAT
    cursor = connection.cursor()
    cursor.execute('''SELECT channelText, xmlTagsId 
        FROM storyElement 
        WHERE storyId = %s 
        AND isOnLayout=1 
        AND xmltagsid IN (1, 2, 3, 4, 7, 11, 12, 13, 14, 16, 17, 18, 20, 21, 22, 23, 24, 430717) 
        AND ((SELECT count(*) FROM storyElement WHERE storyId = %s AND isOnLayout=1 AND xmltagsid =3) = 1)''' % (storyid, storyid))
    '''
    results = [("Blah blah blah ... ", 34), ("Lah lah lah ... ", 45)]
    '''
    results = cursor.fetchall()
    cursor.close()
    return render(request, 'turin/story.html', {'detail_list': results},)

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
