from flask import Flask,request,session
from settings import *
from models import *
from utils import *
import traceback

app = Flask(__name__,static_folder="",static_url_path="")
app.config.from_object(MySQLConfig)
with app.app_context():
	db.init_app(app)
	db.create_all()


@app.before_request
def before():
	try:
		data = json.loads(request.get_data(as_text=True))
		request.form = data
	except:
		pass
	url = request.path #当前请求的URL
	passUrl = WHITE_NAME_LIST
	if url in passUrl:
		pass 
	elif "static" in url:
		pass
	elif "/api/goods/detail/" in url:
		pass 
	else:
		_id = session.get("_id",None)
		if not _id:
			return result(203,{"info":"未登录"})
		else:
			pass 

#登录接口。普通用户和管理员分开 
@app.route("/api/login",methods=["POST","GET"])
def login():

	if request.method == "POST":
		account = request.form["account"]
		password = request.form["password"]
		password = md5(password)
		_type = request.form["type"]
		if _type == "admin":
			admin = Admin.query.filter_by(account=account).first()
			if admin:
				if admin.password == password:
					session["_id"] = admin._id
					admin.loginTime = getNowDataTime()
					db.session.commit()
					return result(200)
				else:
					return result(202,{"info":"密码不正确"})
			else:
				return result(201,{"info":"无该管理员信息"})
		else:
			user = User.query.filter_by(account=account).first()
			if user:
				if user.password==password:
					session["_id"] = user._id
					user.loginTime = getNowDataTime()
					db.session.commit()
					return result(200)
				else:
					return result(202,{"info":"密码不正确"})
			else:
				return result(201,{"info":"无该用户信息"})
	if request.method == "GET":
		return result()

#退出系统
@app.route("/api/quit",methods=["POST"])
def quit():
	if request.method == "POST":
		_id = session["_id"]
		_type = request.form["type"]
		if _type == "admin":
			admin = Admin.query.get(_id)
			admin.logoutTime = getNowDataTime()
		else:
			user = User.query.get(_id)
			user.logoutTime = getNowDataTime()
		del session["_id"]
		return result(200)

#普通用户注册接口
@app.route("/api/regist",methods=["POST"])
def regist():
	if request.method=="POST":
		try:
			account = request.form["account"]
			password = request.form["password"]
			password = md5(password)
			user = User(account=account,password=password)
			try:
				db.session.add(user)
				db.session.commit()
			except:
				return result(205,{"info":"重复注册"})
			user = User.query.filter_by(account=account).first()
			court = Court(user_id=user._id)
			db.session.add(court)
			db.session.commit()
			session["_id"] = user._id 
			return result(200)
		except:
			return result(502,{"info":"数据有误"})
#获取个人地址
@app.route("/api/self/address",methods=["GET"])
def self_address():
	if request.method == "GET":
		sId = session['_id']
		addresses = Address.query.filter_by(user_id=sId)
		data = []
		for address in addresses:
			address = address.__dict__
			del address["_sa_instance_state"]
			data.append(address)
		return result(200,{"address":data})

#地址删除
@app.route("/api/address/delete",methods=["DELETE"])
def address_delete():
	if request.method=="DELETE":

		_id = request.form["id"]
		Address.query.filter_by(_id=_id).delete()
		db.session.commit()
		return result(200)

#用户个人地址添加
@app.route("/api/self/address/add",methods=["POST"])
def self_address_add():
	if request.method=="POST":
		sId = session['_id']
		form = request.form
		data = {
			"province":form["province"],
			"town":form["town"],
			"county":form["county"],
			"detail":form["detail"],
			"user_id":sId
		}
		address = Address(**data)
		db.session.add(address)
		db.session.commit()
		return result(200)
#地址添加
@app.route("/api/address/add",methods=["POST"])
def address_add():
	if request.method=="POST":

		form = request.form
		data = {
			"province":form["province"],
			"town":form["town"],
			"county":form["county"],
			"detail":form["detail"],
		}
		address = Address(**data)
		db.session.add(address)
		db.session.commit()
		return result(200)

#获取所有地址信息接口
@app.route("/api/address")
def address():
	if request.method == "GET":

		addresses = Address.query.filter_by(user_id=None)
		data = dict()
		data["data"]=[]
		for address in addresses:
			dic = address.__dict__
			del dic["_sa_instance_state"]
			data["data"].append(dic) 
		return result(200,data)

#商品分类删除
@app.route("/api/goods/type/delete",methods=["DELETE"])
def goods_type_delete():
	if request.method=="DELETE":

		_id = request.form["id"]
		GoodsType.query.filter_by(_id=_id).delete()
		db.session.commit()

		return result(200)

#商品分类的添加
@app.route("/api/goods/type/add",methods=["POST"])
def goods_type_add():
	if request.method=="POST":

		
		name = request.form["name"]
		_type = GoodsType(name=name)
		db.session.add(_type)
		db.session.commit()
		return result(200)

#商品分类的查询
@app.route("/api/goods/type")
def goods_type():
	if request.method == "GET":
		
		_types = GoodsType.query.all()
		data = dict()
		data["data"] = []
		for _type in _types:
			dic = _type.__dict__
			del dic["_sa_instance_state"]
			data["data"].append(dic) 

		return result(200,data)




#商品添加接口
@app.route("/api/goods/add",methods=["POST"])
def goods_add():
	if request.method == "POST":

		form = request.form
		image = request.files["image"]
		save_path = "./static/goods/"+getOrderNum()+image.filename
		image.save(save_path)
		data  = {
			"name":form["name"],
			"goodsType_id":form["goodsType"],
			"originPrice":form["originPrice"],
			"sellPrice":form["sellPrice"],
			"contains":form["contains"],
			"produceTime":form["produceTime"],
			"expireTime":form["expireTime"],
			"createTime":getNowDataTime(),
			"image":save_path,
			"createAddress_id":form["createAddress"],
			"sendAddress_id":form["sendAddress"],
			"intro":form["intro"]
		}
		goods = Goods(**data)
		db.session.add(goods)
		db.session.commit()
		return result(200)

#获取所有商品信息
@app.route("/api/goods",methods=["POST","GET"])
def goods():
	if request.method == "GET":

		nums = Goods.query.count()
		return result(200,{"nums":nums})

	if request.method == "POST":
		start = request.form["start"]
		nums = request.form["nums"]
		goods = Goods.query.offset(start).limit(nums)
		data = dict()
		data["data"] = []
		for good in goods:
			dic = good.__dict__
			del dic["_sa_instance_state"]
			dic['produceTime']=dic['produceTime'].strftime("%Y-%m-%d")
			dic['expireTime']=dic['expireTime'].strftime("%Y-%m-%d")
			dic['createTime']=dic['createTime'].strftime("%Y-%m-%d")
			dic["goodsType_id"] = GoodsType.query.get(dic["goodsType_id"]).name 
			createAddress = Address.query.get(dic["createAddress_id"])
			dic["createAddress_id"] = createAddress.province+createAddress.town + createAddress.county+createAddress.detail
			sendAddress = Address.query.get(dic["sendAddress_id"])
			dic["sendAddress_id"] = sendAddress.province+sendAddress.town + sendAddress.county+createAddress.detail
			
			data["data"].append(dic)
		return result(200,data)


#商品的删除
@app.route("/api/goods/delete",methods=["DELETE"])
def goods_delete():
	if request.method=="DELETE":

		_id = request.form["id"]
		Goods.query.filter_by(_id=_id).delete()
		return result(200)

#广告
@app.route("/api/ads/add",methods=["POST"])
def ads_add():
	if request.method=="POST":

		form = request.form
		image = request.files["image"]
		save_path = "./static/ads/"+image.filename
		image.save(save_path)
		data = {
			"content":form["content"],
			"createTime":getNowDataTime(),
			"displayTime":form["displayTime"],
			"endTime":form["endTime"],
			"image":save_path,
			"title":form["title"],
			"intro":form["intro"],
		}
		ad = Ad(**data)
		db.session.add(ad)
		db.session.commit()
		return result(200)

#获取所有广告
@app.route("/api/ads")
def ads():
	if request.method == "GET":
		ads = Ad.query.filter_by(displayTime>=getNowDataTime())
		data = dict()
		data["data"] = []
		for ad in ads:
			dic = ad.__dict__
			del dic["_sa_instance_state"]
			data["data"].append(dic) 

		return result(200,data)

#广告删除
@app.route("/api/ads/delete",methods=["DELETE"])
def ads_delete():
	if request.method=="DELETE":

		_id = request.form["id"]
		Ad.query.filter_by(_id=_id).delete()
		return result(200)

#VIP删除
@app.route("/api/vip/delete",methods=["DELETE"])
def vip_delete():
	if request.method=="DELETE":

		_id = request.form["id"]
		Vip.query.filter_by(_id=_id).delete()
		return result(200)
#VIP添加
@app.route("/api/vip/add",methods=["POST"])
def vip_add():
	if request.method == "POST":

		name = request.form["name"]
		level = request.form["level"]
		vip = Vip(name=name,level=level)
		db.session.add(vip)
		db.session.commit()
		return result()

#获取所有VIP信息
@app.route("/api/vip")
def vip():
	if request.method=="GET":
		vips = Vip.query.all()
		data = dict()
		data["data"] = []
		for vip in vips:
			dic = vip.__dict__
			del dic["_sa_instance_state"]
			data["data"].append(dic) 

		return result(200,data)

#添加管理员
@app.route("/api/admin/add",methods=["POST"])
def admin_add():
	if request.method == "POST":

		form = request.form
		data = {
			"name":form["name"],
			"account":form["account"],
			"password":md5(form["password"]),
			"createTime":getNowDataTime(),
			"level":form["level"]
		}
		admin = Admin(**data)
		db.session.add(admin)
		db.session.commit()
		return result(200)


#购买VIP
@app.route("/api/buy/vip",methods=["POST"])
def buy_vip():
	if request.method == "POST":
		form = request.form
		sId = session.get("_id",None)
		user = User.query.get(sId)
		if user.balance < form["payValue"]:
			return result(204,{"info":"余额不足"})
		try:
			user.balance = user.balance - form["payValue"]
			data = {
				"orderNum":getOrderNum(),
				"createTime":getNowDataTime(),
				"payValue":form["payValue"],
				"cutoffValue":form["cutoffValue"],
				"user_id":sId,
				"vipId":form["vipId"]
			}
			print(data)
			r = VipReceipt(**data)
			user.vip = form["vipId"]
			db.session.add(r)
			db.session.commit()
			return result(200)
		except:
			traceback.print_exc()
			return result(502,{"info":"服务端错误"})

#查看自己VIP购买情况
@app.route("/api/self/vip")
def self_vip():
	if request.method == "GET":

		vrs = VipReceipt.query.filter_by(user_id=sId)
		data = dict()
		data["data"] = []
		for vr in vrs:
			dic = vr.__dict__
			del dic["_sa_instance_state"]
			data["data"].append(dic)
		return result(200,data)

#购买商品生成订单
#ps ItemReceipt不能被删除
@app.route("/api/buy/goods",methods=["POST"])
def buy_goods():
	if request.method == "POST":
		sId = session.get("_id",None)
		form = request.form
		user = User.query.get(sId)
		if user.balance < form["payValue"]:
			return result(204,{"info":"余额不足"})
		user.balance = user.balance - form["payValue"]
		goodsList = request.form["goodsList"]
		itemIdList = [] 
		itemCount = ReceiptItem.query.count()
		#购物车清空
		court = Court.query.filter_by(user_id=sId).first()
		try:
			for goods in goodsList:
				item = ReceiptItem(goodsId=goods["id"],number=goods["number"])
				db.session.add(item)
				goods = Goods.query.get(goods["id"])
				court.goods.remove(goods)
				goods.buyTimes = goods.buyTimes + 1
				goods.contains = goods.contains - 1
				itemCount = itemCount + 1
				itemIdList.append(itemCount)
			data = {
				"orderNum":getOrderNum(),
				"createTime":getNowDataTime(),
				"payValue":form["payValue"],
				"cutoffValue":form["cutoffValue"],
				"user_id":sId,
				"itemId":str(itemIdList)
			}
			receipt = Receipt(**data)
			db.session.add(receipt)
			db.session.commit()
			return result(200)
		except:
			traceback.print_exc()
			return result(502,{"info":"服务器错误"})

#查看个人商品订单情况
@app.route("/api/self/receipt")
def self_receipt():
	if request.method == "GET":
		sId = session['_id']
		receipts = Receipt.query.filter_by(user_id=sId)
		data = dict()
		data["data"] = []
		try:
			for receipt in receipts:
				goodsIdList = receipt.get_goods_id_list()
				dic = receipt.__dict__
				del dic["_sa_instance_state"]
				dic["createTime"] = dic["createTime"].strftime("%Y-%m-%d")
				dic["goodsList"] = []
				for goodsId in goodsIdList:
					goods = Goods.query.get(goodsId)
					d = {
						"name":goods.name,
						"originPrice":goods.originPrice,
						"sellPrice":goods.sellPrice
					}
					print("="*30)
					print(d)
					print("="*30)
					dic["goodsList"].append(d)
				data["data"].append(dic)
			return result(200,data)
		except:
			traceback.print_exc()
			return result(502,{"info":"服务端错误"})

#查看所有人VIP订单订单情况
@app.route("/api/admin/vipreceipt/<int:start>/<int:nums>",methods=["POST","GET"])
def admin_vipreceipt(start,nums):
	if request.method == "GET":

		nums = VipReceipt.query.all().count()
		return result(200,{"nums":nums})

	if request.method == "POST":

		receipts = VipReceipt.query.offset(start).limit(nums)
		data = dict()
		data["data"] = []
		for receipt in receipts:
			dic = receipt.__dict__
			del dic["_sa_instance_state"]
			data["data"].append(dic)
		return result(200,data)



#查看所有人商品订单订单情况
@app.route("/api/admin/receipt/<int:start>/<int:nums>",methods=["POST","GET"])
def admin_receipt(start,nums):
	if request.method == "GET":

		nums = Receipt.query.all().count()
		return result(200,{"nums":nums})

	if request.method == "POST":

		receipts = Receipt.query.offset(start).limit(nums)
		data = dict()
		data["data"] = []
		for receipt in receipts:
			goodsIdList = receipt.get_goods_id_list()
			dic = receipt.__dict__
			del dic["_sa_instance_state"]
			dic["goodsList"] = []
			for goodsId in goodsIdList:
				goods = Goods.query.with_entities(Goods.name,Goods.originPrice,Goods.sellPrice).filter_by(_id=goodsId)
				d = goods.__dict__
				del d["_sa_instance_state"]
				dic["goodsList"].append(d)
			data["data"].append(dic)
		return result(200,data)

#用户充值     
@app.route("/api/balance",methods=["POST"])
def balance():
	if request.method=="POST":
		balance = request.form["balance"]
		sId = session.get("_id")
		user = User.query.get(sId)
		try:
			user.balance = user.balance + balance
		except:
			user.balance = balance
		db.session.commit()
		return result()

#获取自己购物车和商品信息
@app.route("/api/self/court")
def self_court():
	if request.method == "GET":
		sId = session.get("_id")
		court = Court.query.filter_by(user_id=sId).first()
		if court.number == 0:
			return result(200,{"goods":[]})
		goods = court.goods.all()
		data = dict()
		data["data"] = []
		for good in goods:
			dic = good.__dict__
			data["data"].append({
				"_id":good._id,
				"name":good.name,
				"originPrice":good.originPrice,
				"sellPrice":good.sellPrice,
				"image":good.image,
				"lookTimes":good.lookTimes,
				"likeTimes":good.likeTimes,
				"buyTimes":good.buyTimes,
				})

		return result(200,data)

#添加商品到购物车
@app.route("/api/add/goods/2/court",methods=["POST"])
def add_goods_2_court():
	if request.method == "POST":
		goodsId = request.form["goodsId"]
		sId = session["_id"]
		court = Court.query.filter_by(user_id=sId).first()
		court.number = court.number + 1
		goods = Goods.query.get(goodsId)
		goods.likeTimes = goods.likeTimes + 1
		court.goods.append(goods)
		db.session.commit()
		return result(200)

#移除购物车商品信息
@app.route("/api/remove/goods/from/court",methods=["POST"])
def remove_goods_from_court():
	if request.method == "POST":
		goodsId = request.form["goodsId"]
		sId = session["_id"]
		court = Court.query.filter_by(user_id=sId).first()
		goods = Goods.query.get(goodsId)
		if goods.likeTimes > 0:
			goods.likeTimes = goods.likeTimes - 1
		court.goods.remove(goods)
		db.session.commit()
		return result()

#用户评论商品
@app.route("/api/add/comment",methods=["POST"])
def add_comment():
	if request.method=="POST":
		sId = session["_id"]
		form = request.form
		image = request.files["image"]
		save_path = "./static/comments/"+image.filename
		image.save(save_path)
		data = {
			"createTime":getNowDataTime(),
			"content":form["content"],
			"points":form["points"],
			"user":sId,
			"good":form["goodsId"],
			"screenCut":save_path
		}
		db.session.add(Comment(**data))
		db.session.commit()
		return result()

#获取商品评论内容
@app.route("/api/comment/<int:goodsId>",methods=["GET","DELETE"])
def comment(goodsId):
	if request.method == "GET":
		comments = Comment.query.filter_by(good=goodsId)
		data = dict()
		data["data"] = []
		for comment in comments:
			dic = comment.__dict__
			del dic["_sa_instance_state"]
			data["data"].append(dic)
		return result(200,data)

#根据分类获取商品信息 分页
@app.route("/api/by/tag/goods",methods=["POST"])
def by_tag_goods():
	if request.method == "POST":
		tagId = request.form["tagId"]
		goods = Goods.query.filter_by(goodsType_id=tagId)
		data = dict()
		data["data"] = []
		for good in goods:
			data["data"].append({
				"id":good._id,
				"name":good.name,
				"originPrice":good.originPrice,
				"sellPrice":good.sellPrice,
				"image":good.image,
				"intro":good.intro
				})
		return result(200,data)

#用户搜索商品信息 最多返回50条
@app.route("/api/goods/search",methods=["POST"])
def goods_search():
	if request.method=="POST":
		keyWord = request.form["keyWord"]
		goods = Goods.query.filter_by(Goods.name.contains(keyWord)).limit(50)
		data = dict()
		data["data"] = []
		for good in goods:
			data["data"].append({
				"id":good._id,
				"name":good.name,
				"originPrice":good.originPrice,
				"sellPrice":good.sellPrice,
				"image":good.image,
				"lookTimes":good.lookTimes,
				"likeTimes":good.likeTimes,
				"buyTimes":good.buyTimes,
				})
		return result(200,data)
#热销的商品推荐 buyTimes 推荐
@app.route("/api/goods/recommend/buytimes")
def goods_recommend_buytime():
	if request.method=="GET":
		goods = Goods.query.order_by(db.desc(Goods.buyTimes)).limit(50)
		data = dict()
		data["data"] = []
		for good in goods:
			data["data"].append({
				"id":good._id,
				"name":good.name,
				"originPrice":good.originPrice,
				"sellPrice":good.sellPrice,
				"image":good.image,
				"lookTimes":good.lookTimes,
				"likeTimes":good.likeTimes,
				"buyTimes":good.buyTimes,
				})
		return result(200,data)
#添加购物车多的商品 likeTimes 推荐
@app.route("/api/goods/recommend/liketimes")
def goods_recommend_liketimes():
	if request.method=="GET":
		goods = Goods.query.order_by(db.desc(Goods.likeTimes)).limit(50)
		data = dict()
		data["data"] = []
		for good in goods:
			data["data"].append({
				"id":good._id,
				"name":good.name,
				"originPrice":good.originPrice,
				"sellPrice":good.sellPrice,
				"image":good.image,
				"lookTimes":good.lookTimes,
				"likeTimes":good.likeTimes,
				"buyTimes":good.buyTimes,
				})
		return result(200,data)
#获取商品的详细信息 更新 lookTimes 浏览次数
@app.route("/api/goods/detail/<int:goodsId>")
def goods_detail(goodsId):
	if request.method=="GET":
		goods = Goods.query.get(goodsId)
		goods.lookTimes = goods.lookTimes + 1
		db.session.commit()
		goods = Goods.query.get(goodsId)
		data= goods.__dict__
		del data["_sa_instance_state"]
		data['produceTime']=data['produceTime'].strftime("%Y-%m-%d")
		data['expireTime']=data['expireTime'].strftime("%Y-%m-%d")
		data['createTime']=data['createTime'].strftime("%Y-%m-%d")
		data["goodsType_id"] = GoodsType.query.get(data["goodsType_id"]).name 
		createAddress = Address.query.get(data["createAddress_id"])
		data["createAddress_id"] = createAddress.province+createAddress.town + createAddress.county+createAddress.detail
		sendAddress = Address.query.get(data["sendAddress_id"])
		data["sendAddress_id"] = sendAddress.province+sendAddress.town + sendAddress.county+createAddress.detail
			
		return result(200,data)

#查看用户个人信息
@app.route("/api/self",methods=["GET"])
def self_info():

	if request.method == "GET":
		sId = session['_id'] 
		user = User.query.get(sId)
		user = user.__dict__
		del user["_sa_instance_state"]
		del	user['createTime']
		del	user['loginTime']
		del	user['logoutTime']
		del	user['password']
		try:
			user['vip']=Vip.query.get(user['vip']).name
		except:
			user['vip'] = '暂无VIP'
		user['address'] = []
		try:
			addresses = Address.query.filter_by(user_id=sId)
			for address in addresses:
				address = address.__dict__
				del address["_sa_instance_state"]
				user['address'].append(address)
		except:
			pass

		if not user['name']:
			user['name'] = '未命名'

		return result(200,user)



@app.route("/api/users",methods=["POST","GET"])
def getUser():
	if request.method == "GET":

		nums = User.query.count()
		return result(200,{"nums":nums})

	if request.method == "POST":
		start = request.form["start"]
		nums = request.form["nums"]
		users = User.query.offset(start).limit(nums)
		data = dict()
		data["data"] = []
		for user in users:
			dic = user.__dict__
			del dic["_sa_instance_state"]
			
			
			data["data"].append(dic)
		return result(200,data)

if __name__ == '__main__':
	app.run(host="192.168.43.171")

