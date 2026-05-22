from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="member")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    borrow_records = db.relationship("BorrowRecord", back_populates="user", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role,
            "created_at": self.created_at.isoformat(),
        }


class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(20), unique=True, nullable=False, index=True)
    publisher = db.Column(db.String(100), default="")
    category = db.Column(db.String(50), default="")
    stock = db.Column(db.Integer, nullable=False, default=1)
    available = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    borrow_records = db.relationship(
        "BorrowRecord", back_populates="book", lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "publisher": self.publisher,
            "category": self.category,
            "stock": self.stock,
            "available": self.available,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class BorrowRecord(db.Model):
    __tablename__ = "borrow_records"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)
    borrow_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    due_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="borrowed")

    user = db.relationship("User", back_populates="borrow_records")
    book = db.relationship("Book", back_populates="borrow_records")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_name": self.user.username,
            "book_id": self.book_id,
            "book_title": self.book.title,
            "borrow_date": self.borrow_date.isoformat(),
            "due_date": self.due_date.isoformat(),
            "return_date": self.return_date.isoformat() if self.return_date else None,
            "status": self.status,
        }
