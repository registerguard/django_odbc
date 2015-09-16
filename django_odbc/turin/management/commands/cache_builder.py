import mxodbc_django
import mx.ODBC.Manager as ODBC
import pprint
from settings import SUBCATEGORIES_TO_IGNORE
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = u'Requests subcategory indexes pages in order to build a cache.'

    def handle(self, *args, **options):
        connection = ODBC.DriverConnect('DSN=Dtnews')
        connection.encoding = 'utf-8'
        connection.stringformat = ODBC.NATIVE_UNICODE_STRINGFORMAT
        cursor = connection.cursor()

        cursor.execute('''SELECT subCategoryName, subCategoryId FROM SubCategory WHERE subCategoryName NOT IN %s''' % (str(SUBCATEGORIES_TO_IGNORE)))
        results = cursor.fetchall()
        subcategory_count_list = []
        for result in results:
            # ('Reviews', '153')
            print result[0], result[1]
            cursor.execute('''SELECT COUNT(*) FROM dbo.Story WHERE Story.subCategoryId=%s AND Story.deskId <> 11''' % str(result[1]))
            # [(1,)]
            story_count = cursor.fetchall()
            self.stdout.write('%s stories in SubCategory %s' % (story_count[0][0], result[0]) )
            subcategory_count_list.append(result.append(list(story_count[0][0])))


        # cursor.execute('''SELECT COUNT(*) FROM dbo.Story WHERE Story.subCategoryId=6 AND Story.deskId <> 11''')
        # results = cursor.fetchall()
        #
        # self.stdout.write('Hi there!')
        # self.stdout.write(str(results))

        cursor.close()
        pprint.pprint(subcategory_count_list)
