import bcrypt
from flask import Blueprint, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from models import db, User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data:
        return {"error": "请求体不能为空"}, 400

    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    role = data.get("role", "member").strip()

    if not username or not password:
        return {"error": "用户名和密码不能为空"}, 400
    if len(password) < 6:
        return {"error": "密码至少6位"}, 400
    if role not in ("admin", "librarian", "member"):
        return {"error": "无效的角色"}, 400

    if User.query.filter_by(username=username).first():
        return {"error": "用户名已存在"}, 409

    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    user = User(username=username, password_hash=pw_hash, role=role)
    db.session.add(user)
    db.session.commit()

    return {"message": "注册成功", "user": user.to_dict()}, 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return {"error": "请求体不能为空"}, 400

    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    user = User.query.filter_by(username=username).first()
    if not user or not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
        return {"error": "用户名或密码错误"}, 401

    token = create_access_token(
        identity=str(user.id),
        additional_claims={"username": user.username, "role": user.role},
    )
    return {"token": token, "user": user.to_dict()}, 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return {"error": "用户不存在"}, 404
    return {"user": user.to_dict()}, 200
