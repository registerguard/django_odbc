import os, sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_odbc.settings')

# This application object is used by the development server
# as well as any WSGI server configured to use this file.
from django.core.wsgi import get_wsgi_application
# sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), '../django_odbc/django_odbc/'))
sys.path.append('/Users/jheasly/Development/django_odbc/django_odbc/')
sys.path.append('/Users/jheasly/.virtualenvs/django_odbc/lib/python2.7/site-packages/egenix_mxodbc_django-1.2.0-py2.7-macosx-10.5-x86_64.egg/')
application = get_wsgi_application()
