import datetime
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
    results = cursor.fetchall()
    cursor.close()
    return render(request, 'turin/story.html', {'detail_list': results},)