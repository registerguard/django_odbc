import datetime, os
from django.shortcuts import render
import mxodbc_django
import mx.ODBC.Manager as ODBC

def today(request):
    today = datetime.date.today()
    eight_digit_date = today.strftime("%Y-%m-%d")
    connection = ODBC.DriverConnect('DSN=Dtnews')
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
    cursor.close()
    
    im_connection = ODBC.DriverConnect('DSN=Dtnews')
    im_connection.encoding = 'utf-8'
    im_connection.stringformat = ODBC.NATIVE_UNICODE_STRINGFORMAT
    im_cursor = im_connection.cursor()
    for story_goods in results:
        im_cursor.execute('''SELECT image, fhdr.fileHeaderName FROM dt_cms_schema.CMSPicture pict, dbo.ForeignDbLink dblk, dbo.FileHeader fhdr, dbo.Story stry
            WHERE pict.fileheaderId = dblk.fileHeaderId 
            AND pict.fileheaderId = fhdr.fileHeaderId 
            AND dblk.foreignId = stry.storyId 
            AND pict.TheCMSPictureVersion = 16
            AND stry.storyId = %s''' % story_goods[0])
        im_results = im_cursor.fetchall()
        for im_result in im_results:
            if im_result[0] and not os.path.isfile('/Users/jheasly/Downloads/dtphotos/%s.jpg' % im_result[1]):
                # im_result[0] binary ooze; im_result[1] filename string
                art  = open('/Users/jheasly/Downloads/dtphotos/%s.jpg' % im_result[1], 'wb')
                art.write(im_result[0])
                art.close()
    
    return render(request, 'turin/base.html', {'list': results},)

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