from datetime import datetime, timedelta, timezone
from flask import Blueprint, request
from models import db, Book, BorrowRecord
from decorators import role_required, get_current_user_id, get_current_user_role

borrow_bp = Blueprint("borrow", __name__, url_prefix="/api/borrow")


@borrow_bp.route("", methods=["POST"])
@role_required("admin", "librarian", "member")
def borrow_book():
    data = request.get_json()
    if not data:
        return {"error": "请求体不能为空"}, 400

    book_id = data.get("book_id")
    if not book_id:
        return {"error": "book_id不能为空"}, 400

    book = db.session.get(Book, book_id)
    if not book:
        return {"error": "图书不存在"}, 404

    if book.available <= 0:
        return {"error": "该书已全部借出"}, 400

    user_id = get_current_user_id()

    already = BorrowRecord.query.filter_by(
        user_id=user_id, book_id=book_id, status="borrowed"
    ).first()
    if already:
        return {"error": "你已借了该书，请先归还"}, 400

    record = BorrowRecord(
        user_id=user_id,
        book_id=book_id,
        due_date=datetime.now(timezone.utc) + timedelta(days=30),
    )
    book.available -= 1
    db.session.add(record)
    db.session.commit()

    return {"message": "借阅成功", "record": record.to_dict()}, 201


@borrow_bp.route("/<int:record_id>/return", methods=["POST"])
@role_required("admin", "librarian", "member")
def return_book(record_id):
    record = db.session.get(BorrowRecord, record_id)
    if not record:
        return {"error": "借阅记录不存在"}, 404

    if record.status != "borrowed":
        return {"error": "该书已归还"}, 400

    user_id = get_current_user_id()
    if record.user_id != user_id:
        return {"error": "只能归还自己借的书"}, 403

    record.status = "returned"
    record.return_date = datetime.now(timezone.utc)
    record.book.available += 1
    db.session.commit()

    return {"message": "归还成功", "record": record.to_dict()}, 200


@borrow_bp.route("/records", methods=["GET"])
@role_required("admin", "librarian", "member")
def list_records():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    per_page = min(per_page, 100)
    status = request.args.get("status", "").strip()

    user_id = get_current_user_id()
    role = get_current_user_role()

    if role in ("admin", "librarian"):
        query = BorrowRecord.query
    else:
        query = BorrowRecord.query.filter_by(user_id=user_id)

    if status:
        query = query.filter(BorrowRecord.status == status)

    query = query.order_by(BorrowRecord.borrow_date.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return {
        "records": [r.to_dict() for r in pagination.items],
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages,
        "per_page": pagination.per_page,
    }, 200


@borrow_bp.route("/records/<int:record_id>", methods=["GET"])
@role_required("admin", "librarian", "member")
def get_record(record_id):
    record = db.session.get(BorrowRecord, record_id)
    if not record:
        return {"error": "借阅记录不存在"}, 404

    user_id = get_current_user_id()
    role = get_current_user_role()

    if role not in ("admin", "librarian") and record.user_id != user_id:
        return {"error": "无权查看他人的借阅记录"}, 403

    return {"record": record.to_dict()}, 200
