from django.shortcuts import render
import mxodbc_django
import mx.ODBC.Manager as ODBC

def today(request):
    connection = ODBC.DriverConnect('DSN=Dtnews')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM Category', '')
    results = cursor.fetchall()
    cursor.close()
    return render(request, 'turin/base.html', {'list': results},)
