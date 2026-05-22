from flask import Blueprint, request
from models import db, User
from decorators import role_required

users_bp = Blueprint("users", __name__, url_prefix="/api/users")


@users_bp.route("", methods=["GET"])
@role_required("admin")
def list_users():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    per_page = min(per_page, 100)

    pagination = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return {
        "users": [u.to_dict() for u in pagination.items],
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages,
        "per_page": pagination.per_page,
    }, 200


@users_bp.route("/<int:user_id>", methods=["GET"])
@role_required("admin")
def get_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return {"error": "用户不存在"}, 404
    return {"user": user.to_dict()}, 200


@users_bp.route("/<int:user_id>/role", methods=["PUT"])
@role_required("admin")
def update_role(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return {"error": "用户不存在"}, 404

    data = request.get_json()
    if not data:
        return {"error": "请求体不能为空"}, 400

    new_role = data.get("role", "").strip()
    if new_role not in ("admin", "librarian", "member"):
        return {"error": "无效的角色，可选: admin, librarian, member"}, 400

    user.role = new_role
    db.session.commit()
    return {"message": "角色更新成功", "user": user.to_dict()}, 200
