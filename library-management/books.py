from flask import Blueprint, request
from models import db, Book
from decorators import role_required

books_bp = Blueprint("books", __name__, url_prefix="/api/books")


@books_bp.route("", methods=["GET"])
def list_books():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    per_page = min(per_page, 100)

    q = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()

    query = Book.query
    if q:
        query = query.filter(
            db.or_(Book.title.ilike(f"%{q}%"), Book.author.ilike(f"%{q}%"))
        )
    if category:
        query = query.filter(Book.category == category)

    query = query.order_by(Book.updated_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return {
        "books": [b.to_dict() for b in pagination.items],
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages,
        "per_page": pagination.per_page,
    }, 200


@books_bp.route("/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = db.session.get(Book, book_id)
    if not book:
        return {"error": "图书不存在"}, 404
    return {"book": book.to_dict()}, 200


@books_bp.route("", methods=["POST"])
@role_required("admin", "librarian")
def create_book():
    data = request.get_json()
    if not data:
        return {"error": "请求体不能为空"}, 400

    title = data.get("title", "").strip()
    author = data.get("author", "").strip()
    isbn = data.get("isbn", "").strip()

    if not title or not author or not isbn:
        return {"error": "书名、作者和ISBN不能为空"}, 400

    if Book.query.filter_by(isbn=isbn).first():
        return {"error": "ISBN已存在"}, 409

    stock = max(1, data.get("stock", 1))
    book = Book(
        title=title,
        author=author,
        isbn=isbn,
        publisher=data.get("publisher", "").strip(),
        category=data.get("category", "").strip(),
        stock=stock,
        available=stock,
    )
    db.session.add(book)
    db.session.commit()

    return {"message": "添加成功", "book": book.to_dict()}, 201


@books_bp.route("/<int:book_id>", methods=["PUT"])
@role_required("admin", "librarian")
def update_book(book_id):
    book = db.session.get(Book, book_id)
    if not book:
        return {"error": "图书不存在"}, 404

    data = request.get_json()
    if not data:
        return {"error": "请求体不能为空"}, 400

    if "title" in data:
        book.title = data["title"].strip()
    if "author" in data:
        book.author = data["author"].strip()
    if "isbn" in data:
        new_isbn = data["isbn"].strip()
        existing = Book.query.filter(Book.isbn == new_isbn, Book.id != book_id).first()
        if existing:
            return {"error": "ISBN已被其他图书使用"}, 409
        book.isbn = new_isbn
    if "publisher" in data:
        book.publisher = data["publisher"].strip()
    if "category" in data:
        book.category = data["category"].strip()
    if "stock" in data:
        new_stock = max(1, data["stock"])
        borrowed = book.stock - book.available
        if new_stock < borrowed:
            return {"error": f"库存不能小于已借出数量({borrowed})"}, 400
        book.available += new_stock - book.stock
        book.stock = new_stock

    db.session.commit()
    return {"message": "更新成功", "book": book.to_dict()}, 200


@books_bp.route("/<int:book_id>", methods=["DELETE"])
@role_required("admin")
def delete_book(book_id):
    book = db.session.get(Book, book_id)
    if not book:
        return {"error": "图书不存在"}, 404

    active = book.borrow_records.filter_by(status="borrowed").count()
    if active > 0:
        return {"error": f"该书有{active}条未归还记录，无法删除"}, 400

    db.session.delete(book)
    db.session.commit()
    return {"message": "删除成功"}, 200
