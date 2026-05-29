from flask import Flask, render_template, redirect, url_for, flash, request, make_response
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from models import db, User, Property, Tenant, Contract
from datetime import datetime
import io
from xhtml2pdf import pisa

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# === 登录注册 ===
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('登录成功', 'success')
            return redirect(url_for('index'))
        flash('用户名或密码错误', 'error')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        real_name = request.form.get('real_name', '').strip()
        phone = request.form.get('phone', '').strip()

        if not username or not password:
            flash('用户名和密码不能为空', 'error')
            return render_template('register.html')

        if User.query.filter_by(username=username).first():
            flash('用户名已存在', 'error')
            return render_template('register.html')

        user = User(
            username=username,
            password=generate_password_hash(password),
            real_name=real_name,
            phone=phone
        )
        db.session.add(user)
        db.session.commit()
        flash('注册成功，请登录', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# === 首页 ===
@app.route('/')
@login_required
def index():
    total_properties = Property.query.count()
    available_properties = Property.query.filter_by(status='available').count()
    total_contracts = Contract.query.count()
    active_contracts = Contract.query.filter_by(status='active').count()
    return render_template('index.html',
                           total_properties=total_properties,
                           available_properties=available_properties,
                           total_contracts=total_contracts,
                           active_contracts=active_contracts)


# === 房源管理 ===
@app.route('/properties')
@login_required
def properties():
    props = Property.query.order_by(Property.created_at.desc()).all()
    return render_template('properties.html', properties=props)


@app.route('/property/add', methods=['GET', 'POST'])
@login_required
def property_add():
    if request.method == 'POST':
        prop = Property(
            title=request.form.get('title', '').strip(),
            address=request.form.get('address', '').strip(),
            area=float(request.form.get('area', 0)),
            layout=request.form.get('layout', '').strip(),
            floor=request.form.get('floor', '').strip(),
            rent_amount=float(request.form.get('rent_amount', 0)),
            deposit=float(request.form.get('deposit', 0)),
            description=request.form.get('description', '').strip(),
            landlord_name=request.form.get('landlord_name', '').strip(),
            landlord_phone=request.form.get('landlord_phone', '').strip(),
            landlord_id_card=request.form.get('landlord_id_card', '').strip(),
        )
        db.session.add(prop)
        db.session.commit()
        flash('房源添加成功', 'success')
        return redirect(url_for('properties'))
    return render_template('property_form.html', property=None)


@app.route('/property/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def property_edit(id):
    prop = db.session.get(Property, id)
    if not prop:
        flash('房源不存在', 'error')
        return redirect(url_for('properties'))
    if request.method == 'POST':
        prop.title = request.form.get('title', '').strip()
        prop.address = request.form.get('address', '').strip()
        prop.area = float(request.form.get('area', 0))
        prop.layout = request.form.get('layout', '').strip()
        prop.floor = request.form.get('floor', '').strip()
        prop.rent_amount = float(request.form.get('rent_amount', 0))
        prop.deposit = float(request.form.get('deposit', 0))
        prop.description = request.form.get('description', '').strip()
        prop.landlord_name = request.form.get('landlord_name', '').strip()
        prop.landlord_phone = request.form.get('landlord_phone', '').strip()
        prop.landlord_id_card = request.form.get('landlord_id_card', '').strip()
        db.session.commit()
        flash('房源更新成功', 'success')
        return redirect(url_for('properties'))
    return render_template('property_form.html', property=prop)


@app.route('/property/delete/<int:id>', methods=['POST'])
@login_required
def property_delete(id):
    prop = db.session.get(Property, id)
    if prop:
        if prop.contracts:
            flash('该房源有关联合同，无法删除', 'error')
        else:
            db.session.delete(prop)
            db.session.commit()
            flash('房源已删除', 'success')
    return redirect(url_for('properties'))


# === 租客管理 ===
@app.route('/tenants')
@login_required
def tenants():
    tenant_list = Tenant.query.order_by(Tenant.created_at.desc()).all()
    return render_template('tenants.html', tenants=tenant_list)


@app.route('/tenant/add', methods=['POST'])
@login_required
def tenant_add():
    tenant = Tenant(
        name=request.form.get('name', '').strip(),
        phone=request.form.get('phone', '').strip(),
        id_card=request.form.get('id_card', '').strip(),
        wechat=request.form.get('wechat', '').strip(),
    )
    db.session.add(tenant)
    db.session.commit()
    flash('租客添加成功', 'success')
    return redirect(url_for('tenants'))


@app.route('/tenant/edit/<int:id>', methods=['POST'])
@login_required
def tenant_edit(id):
    tenant = db.session.get(Tenant, id)
    if tenant:
        tenant.name = request.form.get('name', '').strip()
        tenant.phone = request.form.get('phone', '').strip()
        tenant.id_card = request.form.get('id_card', '').strip()
        tenant.wechat = request.form.get('wechat', '').strip()
        db.session.commit()
        flash('租客信息已更新', 'success')
    return redirect(url_for('tenants'))


@app.route('/tenant/delete/<int:id>', methods=['POST'])
@login_required
def tenant_delete(id):
    tenant = db.session.get(Tenant, id)
    if tenant:
        if tenant.contracts:
            flash('该租客有关联合同，无法删除', 'error')
        else:
            db.session.delete(tenant)
            db.session.commit()
            flash('租客已删除', 'success')
    return redirect(url_for('tenants'))


# === 合同管理 ===
@app.route('/contracts')
@login_required
def contracts():
    contract_list = Contract.query.order_by(Contract.created_at.desc()).all()
    return render_template('contracts.html', contracts=contract_list)


@app.route('/contract/add', methods=['GET', 'POST'])
@login_required
def contract_add():
    if request.method == 'POST':
        prop = db.session.get(Property, int(request.form.get('property_id', 0)))
        contract = Contract(
            contract_no=request.form.get('contract_no', '').strip(),
            property_id=int(request.form.get('property_id', 0)),
            tenant_id=int(request.form.get('tenant_id', 0)),
            start_date=datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date(),
            end_date=datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date(),
            monthly_rent=float(request.form.get('monthly_rent', 0)),
            deposit=float(request.form.get('deposit', 0)),
            payment_method=request.form.get('payment_method', '月付'),
            special_terms=request.form.get('special_terms', '').strip(),
        )
        if prop:
            prop.status = 'rented'
        db.session.add(contract)
        db.session.commit()
        flash('合同创建成功', 'success')
        return redirect(url_for('contracts'))

    properties_list = Property.query.order_by(Property.created_at.desc()).all()
    tenants_list = Tenant.query.order_by(Tenant.created_at.desc()).all()
    return render_template('contract_form.html',
                           contract=None,
                           properties=properties_list,
                           tenants=tenants_list)


@app.route('/contract/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def contract_edit(id):
    contract = db.session.get(Contract, id)
    if not contract:
        flash('合同不存在', 'error')
        return redirect(url_for('contracts'))
    if request.method == 'POST':
        contract.contract_no = request.form.get('contract_no', '').strip()
        contract.property_id = int(request.form.get('property_id', 0))
        contract.tenant_id = int(request.form.get('tenant_id', 0))
        contract.start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
        contract.end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
        contract.monthly_rent = float(request.form.get('monthly_rent', 0))
        contract.deposit = float(request.form.get('deposit', 0))
        contract.payment_method = request.form.get('payment_method', '月付')
        contract.special_terms = request.form.get('special_terms', '').strip()
        db.session.commit()
        flash('合同更新成功', 'success')
        return redirect(url_for('contracts'))

    properties_list = Property.query.order_by(Property.created_at.desc()).all()
    tenants_list = Tenant.query.order_by(Tenant.created_at.desc()).all()
    return render_template('contract_form.html',
                           contract=contract,
                           properties=properties_list,
                           tenants=tenants_list)


@app.route('/contract/delete/<int:id>', methods=['POST'])
@login_required
def contract_delete(id):
    contract = db.session.get(Contract, id)
    if contract:
        prop = db.session.get(Property, contract.property_id)
        if prop:
            prop.status = 'available'
        db.session.delete(contract)
        db.session.commit()
        flash('合同已删除', 'success')
    return redirect(url_for('contracts'))


@app.route('/contract/terminate/<int:id>', methods=['POST'])
@login_required
def contract_terminate(id):
    contract = db.session.get(Contract, id)
    if contract:
        contract.status = 'terminated'
        prop = db.session.get(Property, contract.property_id)
        if prop:
            prop.status = 'available'
        db.session.commit()
        flash('合同已终止', 'success')
    return redirect(url_for('contracts'))


# === PDF导出 ===
@app.route('/contract/<int:id>/pdf')
@login_required
def contract_pdf(id):
    contract = db.session.get(Contract, id)
    if not contract:
        flash('合同不存在', 'error')
        return redirect(url_for('contracts'))

    html = render_template('contract_pdf.html', contract=contract)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode('utf-8')), result)
    if pdf.err:
        flash('PDF生成失败', 'error')
        return redirect(url_for('contracts'))

    response = make_response(result.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=contract_{contract.contract_no}.pdf'
    return response


# === 初始化数据库 ===
def init_db():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                password=generate_password_hash('admin123'),
                real_name='管理员',
                phone='13800000000'
            )
            db.session.add(admin)
            db.session.commit()
            print('默认管理员账号已创建: admin / admin123')


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
