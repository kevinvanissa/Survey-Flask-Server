import os

basedir = os.path.abspath(os.path.dirname(__file__))

MAX_CONTENT_LENGTH = 1 * 1024 * 1024

# pagination
ITEMS_PER_PAGE = 10

CRSF_ENABLED = True

# SQLALCHEMY_DATABASE_URI='sqlite:////home/kevin/Programming/xsertraining/xsert/xsert.db'
# SQLALCHEMY_DATABASE_URI='mysql://root:@localhost/xsert?charset=utf8'
SQLALCHEMY_DATABASE_URI='mysql+pymysql://cartUser:cartT00L@192.168.64.5:3306/cart'

#MYSQL_DATABASE_USER = 'root'
#MYSQL_DATABASE_PASSWORD = '1234'
#MYSQL_DATABASE_DB = 'xsert'
#MYSQL_DATABASE_HOST = 'localhost'
#SQLALCHEMY_ECHO = True
SECRET_KEY='mysecretkey'
UPLOAD_FOLDER = basedir+'/app/static/uploads'
ALLOWED_EXTENSIONS = set(['jpg','png','jpeg'])
