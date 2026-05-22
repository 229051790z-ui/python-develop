"""初始化数据库：创建管理员账户和示例数据"""
import bcrypt
from app import create_app
from models import db, User, Book

app = create_app()

with app.app_context():
    db.create_all()

    # 创建默认管理员
    if not User.query.filter_by(username="admin").first():
        pw_hash = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
        db.session.add(User(username="admin", password_hash=pw_hash, role="admin"))

    # 创建示例图书管理员
    if not User.query.filter_by(username="librarian").first():
        pw_hash = bcrypt.hashpw("lib123456".encode(), bcrypt.gensalt()).decode()
        db.session.add(User(username="librarian", password_hash=pw_hash, role="librarian"))

    # 创建普通成员
    if not User.query.filter_by(username="reader").first():
        pw_hash = bcrypt.hashpw("reader123".encode(), bcrypt.gensalt()).decode()
        db.session.add(User(username="reader", password_hash=pw_hash, role="member"))

    db.session.commit()

    # 添加示例图书
    sample_books = [
        {"title": "Python编程:从入门到实践", "author": "Eric Matthes", "isbn": "978-7-115-54608-1", "publisher": "人民邮电出版社", "category": "编程", "stock": 5},
        {"title": "流畅的Python", "author": "Luciano Ramalho", "isbn": "978-7-115-45415-7", "publisher": "人民邮电出版社", "category": "编程", "stock": 3},
        {"title": "百年孤独", "author": "加西亚·马尔克斯", "isbn": "978-7-5442-5399-4", "publisher": "南海出版公司", "category": "文学", "stock": 4},
        {"title": "三体", "author": "刘慈欣", "isbn": "978-7-5364-7268-4", "publisher": "重庆出版社", "category": "科幻", "stock": 6},
        {"title": "算法导论", "author": "Thomas H. Cormen", "isbn": "978-7-111-40701-0", "publisher": "机械工业出版社", "category": "计算机", "stock": 2},
    ]

    for b in sample_books:
        if not Book.query.filter_by(isbn=b["isbn"]).first():
            db.session.add(Book(**b, available=b["stock"]))

    db.session.commit()
    print("数据库初始化完成！")
    print("  管理员: admin / admin123")
    print("  图书管理员: librarian / lib123456")
    print("  普通读者: reader / reader123")
