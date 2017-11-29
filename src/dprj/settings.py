# -*- coding: utf-8 -*-
""" Django settings for dprj project.
    http://djangoproject.jp/doc/ja/1.0/ref/settings.html
"""
import os
import settings_sub

__PRJ_NAME = settings_sub.PROJECT_NAME
__base_path = os.path.join(os.path.dirname(__file__))
DEBUG = settings_sub.IS_DEV
TEMPLATE_DEBUG = DEBUG

ADMINS = ( # ここはサイトのエラー画面で表示される連絡先を書く.
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

USE_TZ = True   # これTrueにしないとDateTimeをまともに使えない模様. djangoのmysqlバックエンドがおかしい.

DB_DEFAULT = 'default'
DB_READONLY = 'read_only'
DATABASES = {
     # デフォルト. マスターDB. 読み書きOK. default という名前を変更してはいけない.
     DB_DEFAULT: {
          'ENGINE': u'django_mysqlpool.backends.mysqlpool',
          'NAME': settings_sub.MYSQL_DATABASE_NAME,
          'USER': 'app_server',
          'PASSWORD': '#u9H!3wP',
          'HOST': settings_sub.MYSQL_MASTER_HOST,
          'PORT': '3306',
          'OPTIONS':{
                     'connect_timeout':1,
                     },
     },
     # スレーブ. 読み込み専用DB.
     DB_READONLY: {
          'ENGINE': u'django_mysqlpool.backends.mysqlpool',
          'NAME': settings_sub.MYSQL_DATABASE_NAME,
          'USER': 'app_server',
          'PASSWORD': '#u9H!3wP',
          'HOST': settings_sub.MYSQL_SLAVE_HOST,
          'PORT': '3306',
          'TEST_MIRROR': 'default',
     },
}
if getattr(settings_sub, 'MYSQL_BACKUP_HOST', None):
    # バックアップサーバにも接続する場合.
    DB_BACKUP = 'backup'
    DATABASES.update({
        DB_BACKUP : {
          'ENGINE': u'django_mysqlpool.backends.mysqlpool',
          'NAME': settings_sub.MYSQL_DATABASE_NAME,
          'USER': 'app_server',
          'PASSWORD': '#u9H!3wP',
          'HOST': settings_sub.MYSQL_BACKUP_HOST,
          'PORT': '3306',
        }
    })

DATABASE_POOL_ARGS = {'max_overflow': 0,'pool_size':settings_sub.MYSQL_POOL_SIZE, 'recycle':settings_sub.MYSQL_WAIT_TIMEOUT}
####################################
GADGET_TIMEOUT = 4.5 #timeout for mobile social gadget server 
####################################


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Asia/Tokyo'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'ja'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
#MEDIA_ROOT = os.path.join(__base_path, '../../media/')
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = os.path.join(__base_path, '/')

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'a@l2c9008li*x5)iisus(6v)uf2hfeenif8lcldt%hs16lgq4m'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#    'django.template.loaders.eggs.Loader.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
#    'django.middleware.transaction.TransactionMiddleware',
)

#SESSION_ENGINE = "django.contrib.sessions.backends.cache"

ROOT_URLCONF = __PRJ_NAME + '.urls'

PYLIBMC_BEHAVIORS = {'tcp_nodelay': True, 'ketama': True}

#sys.path.append(__base_path + '/platinumegg')
#sys.path.append(__base_path + '/platinumegg/lib')

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
#    'django/videostream/path/templates/',
)

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
#    'django.contrib.admin', # ←adminモジュールを追加
#    'videostream',
    # アプリ追加.
    'platinumegg.app.'+settings_sub.APP_NAME,
)

DEFAULT_CHARSET = 'utf-8'

FILE_UPLOAD_HANDLERS = ('django.core.files.uploadhandler.TemporaryFileUploadHandler',)
