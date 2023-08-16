from datetime import date, timedelta, datetime, time
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
# from dateutil.relativedelta import relativedelta
from flask_security import UserMixin, RoleMixin

class RolesUsers(db.Model):
    __tablename__ = 'roles_users'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column('user_id', db.Integer(), db.ForeignKey('user.id'))
    role_id = db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
    

class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=True)
    password = db.Column(db.String, nullable=False)
    first_name = db.Column(db.String, default="John")
    last_name = db.Column(db.String, default="Doe")
    email = db.Column(db.String, default="johdoe@lorem.lol")
    address = db.Column(db.String, nullable=False)
    contact_number = db.Column(db.Integer, nullable=False)
    active = db.Column(db.Boolean())
    authenticated = db.Column(db.Boolean())
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    roles = db.relationship('Role', secondary='roles_users',
                         backref=db.backref('users', lazy='dynamic'))
    orders = db.relationship('Transaction', backref='user', order_by='Transaction.timestamp.desc()')
    
    @property
    def is_authorised(self):
        return self.authenticated
    
   
class Product(db.Model):
    __tablename__ = 'product'
    product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_name = db.Column(db.String, unique=True)
    category_id = db.Column(db.Integer,
                            db.ForeignKey("category.category_id"),
                            nullable=False)
    stock = db.Column(db.Integer, default=100)
    unit = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, default=100, nullable=False)
    mfd = db.Column(db.DateTime, default=datetime.utcnow())
    # mfd = db.Column(db.Date, default=date.today())
    expd = db.Column(db.DateTime,
                     default=datetime.utcnow())# + relativedelta(months=6)))
    # expd = db.Column(db.Date, default=date.today() + timedelta(days=7))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow())
    __table_args__ = (db.CheckConstraint(stock >= 0, name='check_stock_min'), )

    def __init__(self,
                 product_name,
                 category_id,
                 category,
                 unit,
                 stock=100,
                 price=100,
                 mfd = datetime.fromisoformat(datetime.utcnow().isoformat()),
                 expd = datetime.fromisoformat(datetime.utcnow().isoformat()),# + relativedelta(months=6)),
                 last_updated = datetime.fromisoformat(datetime.utcnow().isoformat())):
        self.product_name = product_name
        self.category_id = category_id
        self.stock = stock
        self.unit = unit
        self.price = price
        self.mfd = mfd
        self.expd = expd
        self.last_updated = last_updated
        
class Category(db.Model):
	__tablename__ = 'category'
	category_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	category_name = db.Column(db.String, unique=True)
	products = db.relationship('Product', backref='category', order_by='Product.last_updated.desc()')

	def __init__(self, category_name):
		self.category_name = category_name
        

# class Cart(db.Model):
#     __tablename__ = 'cart'
#     user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
#     category_id = db.Column(db.Integer,
#                             db.ForeignKey("category.category_id"),
#                             nullable=False)
#     product_id = db.Column(db.Integer,
#                            db.ForeignKey("product.product_id"),
#                            nullable=False)
#     qty = db.Column(db.Integer, default=1)
#     unit_price = db.Column(db.Integer,
#                            db.ForeignKey("product.price"),
#                            nullable=False)
#     __table_args__ = (
#         db.PrimaryKeyConstraint('user_id', 'product_id', 'qty'),
#         db.CheckConstraint(qty >= 1, name='check_qty_min'),
#     )

#     # @property
#     # def unit_amount(self):
#     #     return self.qty * self.unit_price
#     def __init__(self, user_id, category_id, product_id, unit_price, qty=1):
#         self.user_id = user_id
#         self.category_id = category_id
#         self.product_id = product_id
#         self.qty = qty
#         self.unit_price = unit_price


class Transaction(db.Model):
    __tablename__ = 'transaction'
    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    order = db.Column(db.String, default="Empty")
    total_price = db.Column(db.Integer, nullable=False)

    # @property
    # def item_amount(self):
    #     return self.quantity * self.item_price
    def __init__(self, user_id, order, total_price, timestamp=datetime.fromisoformat(datetime.utcnow().isoformat())):
        self.timestamp = timestamp
        self.user_id = user_id
        self.order = order
        self.total_price = total_price