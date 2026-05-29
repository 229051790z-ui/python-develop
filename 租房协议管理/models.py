from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    real_name = db.Column(db.String(80))
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Property(db.Model):
    __tablename__ = 'properties'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(500), nullable=False)
    area = db.Column(db.Float, nullable=False)
    layout = db.Column(db.String(50))
    floor = db.Column(db.String(50))
    rent_amount = db.Column(db.Float, nullable=False)
    deposit = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='available')
    description = db.Column(db.Text)
    landlord_name = db.Column(db.String(80))
    landlord_phone = db.Column(db.String(20))
    landlord_id_card = db.Column(db.String(30))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    contracts = db.relationship('Contract', backref='property', lazy=True)


class Tenant(db.Model):
    __tablename__ = 'tenants'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    id_card = db.Column(db.String(30))
    wechat = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    contracts = db.relationship('Contract', backref='tenant', lazy=True)


class Contract(db.Model):
    __tablename__ = 'contracts'
    id = db.Column(db.Integer, primary_key=True)
    contract_no = db.Column(db.String(50), unique=True, nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    monthly_rent = db.Column(db.Float, nullable=False)
    deposit = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), default='月付')
    status = db.Column(db.String(20), default='active')
    special_terms = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
