#mysql settings
class MySQLConfig(object):

	DEBUGE = True
	SECRET_KEY = "123.com"
	SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{username}:{password}@{ipaddress}:{port}/{database}".format(username="root",password="123456",ipaddress="127.0.0.1",port="3306",database="mall")
	SQLALCHEMY_TRACK_MODIFICATIONS = True#动态追踪修改设置
	SQLALCHEMY_ECHO = True 

WHITE_NAME_LIST = ["/api/login","/api/regist","/api/goods/type","/api/by/tag/goods"]