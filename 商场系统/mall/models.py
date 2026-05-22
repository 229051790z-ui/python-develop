from flask_sqlalchemy import SQLAlchemy 

db = SQLAlchemy()

class User(db.Model):

	__tablename__ = "user"
	__table_args__ = {'mysql_collate':'utf8_general_ci'}

	_id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(30))
	account = db.Column(db.String(11),unique=True)
	password = db.Column(db.String(64))
	avatar = db.Column(db.String(256))
	age = db.Column(db.Integer)
	idCard = db.Column(db.String(18))
	gneder = db.Column(db.String(2))
	createTime = db.Column(db.DateTime)
	loginTime = db.Column(db.DateTime)
	logoutTime = db.Column(db.DateTime)
	balance = db.Column(db.Float(10),default=0)

	vip = db.Column(db.Integer,db.ForeignKey("vip._id"))

	def __repr__(self):
		return "User:%s"%self.name

goodsCourt = db.Table("goodsCourt",
	db.Column("goods_id",db.Integer,db.ForeignKey("goods._id")),
	db.Column("court_id",db.Integer,db.ForeignKey("court._id"))
	)

class Court(db.Model):

	__tablename__ = "court"
	__table_args__ = {'mysql_collate':'utf8_general_ci'}
	_id = db.Column(db.Integer,primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user._id'))
	number = db.Column(db.Integer,default=0)#记录商品种类
	goods = db.relationship("Goods",secondary=goodsCourt,backref=db.backref("court",lazy="dynamic"),lazy="dynamic")


class Address(db.Model):

	__tablename__ = "address"
	__table_args__ = {'mysql_collate':'utf8_general_ci'}
	_id = db.Column(db.Integer,primary_key=True)
	province = db.Column(db.String(18))
	town = db.Column(db.String(18))
	county = db.Column(db.String(18))
	detail = db.Column(db.String(200))
	user_id = db.Column(db.Integer,db.ForeignKey("user._id"))

	def __repr__(self):
		return "Address:%s"%self.detail

class Vip(db.Model):

	__tablename__ = "vip"
	__table_args__ = {'mysql_collate':'utf8_general_ci'}
	_id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(50))
	level = db.Column(db.Integer,default=0)

	def __repr__(self):
		return "Vip:%s"%self.name 
	 
class Ad(db.Model):

	__tablename__ = "ad"
	__table_args__ = {'mysql_collate':'utf8_general_ci'}
	_id = db.Column(db.Integer,primary_key=True)
	content = db.Column(db.String(50))
	createTime = db.Column(db.DateTime)
	displayTime = db.Column(db.DateTime)
	endTime = db.Column(db.DateTime)
	image = db.Column(db.String(256))
	video = db.Column(db.String(256))
	title = db.Column(db.String(100))
	intro = db.Column(db.String(500))

	def __repr__(self):
		return "Ad:%s"%self.content 
	 
class Admin(db.Model):

	__tablename__ = "admin"
	__table_args__ = {'mysql_collate':'utf8_general_ci'}
	_id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(30))
	account = db.Column(db.String(11))
	password = db.Column(db.String(64))
	createTime = db.Column(db.DateTime)
	loginTime = db.Column(db.DateTime)
	logoutTime = db.Column(db.DateTime)
	level = db.Column(db.Integer,default=0)

	def __repr__(self):
		return "Admin:%s"%self.name 
	 
class GoodsType(db.Model):

	__tablename__ = "goodsType"
	__table_args__ = {'mysql_collate':'utf8_general_ci'}
	_id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(50))
	number = db.Column(db.Integer,default=0)

	def __repr__(self):
		return "GoodsType:%s"%self.name

class Goods(db.Model):

	__tablename__ = "goods"
	__table_args__ = {'mysql_collate':'utf8_general_ci'}
	_id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(100))
	goodsType_id = db.Column(db.Integer,db.ForeignKey("goodsType._id"))
	originPrice = db.Column(db.Float(10))
	sellPrice = db.Column(db.Float(10))
	contains = db.Column(db.Integer,default=0)
	produceTime = db.Column(db.DateTime)
	expireTime = db.Column(db.DateTime)
	createTime = db.Column(db.DateTime)
	image = db.Column(db.String(256))
	createAddress_id = db.Column(db.Integer,db.ForeignKey("address._id"))
	sendAddress_id = db.Column(db.Integer,db.ForeignKey("address._id"))
	intro = db.Column(db.String(500))
	lookTimes = db.Column(db.Integer,default=0)
	buyTimes = db.Column(db.Integer,default=0)
	likeTimes = db.Column(db.Integer,default=0)

	def __repr__(self):
		return "Goods:%s"%self.name

class VipReceipt(db.Model):
	__tablename__ = "vip_receipt"
	__table_args__ = {'mysql_collate':'utf8_general_ci'}
	_id = db.Column(db.Integer,primary_key=True)
	orderNum = db.Column(db.String(30))
	createTime = db.Column(db.DateTime)
	payValue = db.Column(db.Float(10))
	cutoffValue = db.Column(db.Float(10))
	user_id = db.Column(db.Integer,db.ForeignKey("user._id"))
	vipId = db.Column(db.Integer)

	def __repr__(self):
		return "VipReceipt:%s"%self.orderNum

class ReceiptItem(db.Model):

	__tablename__ = "receipt_item"
	__table_args__ = {'mysql_collate':'utf8_general_ci'}
	_id = db.Column(db.Integer,primary_key=True)
	goodsId = db.Column(db.Integer)
	number = db.Column(db.Integer,default=0)
	

class Receipt(db.Model):

	__tablename__ = "receipt"
	__table_args__ = {'mysql_collate':'utf8_general_ci'}
	_id = db.Column(db.Integer,primary_key=True)
	orderNum = db.Column(db.String(30))
	createTime = db.Column(db.DateTime)
	payValue = db.Column(db.Float(10))
	cutoffValue = db.Column(db.Float(10))
	user_id = db.Column(db.Integer,db.ForeignKey("user._id"))
	itemId = db.Column(db.String(100),default="[]")

	def get_goods_id_list(self):
		idStrList = self.itemId[1:-1].split(',')
		idList = []
		for item in idStrList:
			idList.append(int(item))
		return idList

	def __repr__(self):
		return "Receipt:%s"%self.orderNum

class Comment(db.Model):

	__tablename__ = "comment"
	__table_args__ = {'mysql_collate':'utf8_general_ci'}
	_id = db.Column(db.Integer,primary_key=True)
	createTime = db.Column(db.DateTime)
	content = db.Column(db.String(500))
	points = db.Column(db.Integer,default=5)
	screenCut = db.Column(db.String(256))
	user = db.Column(db.Integer,db.ForeignKey("user._id"))
	good = db.Column(db.Integer,db.ForeignKey("goods._id"))

	def __repr__(self):
		return "Comment:%s"%self.content

