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
        for result in results:
            print result

        cursor.execute('''SELECT COUNT(*) FROM dbo.Story WHERE Story.subCategoryId=6 AND Story.deskId <> 11''')
        results = cursor.fetchall()

        self.stdout.write('Hi there!')
        self.stdout.write(str(results))

        cursor.close()
