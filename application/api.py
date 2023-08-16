
from datetime import date, datetime, timedelta, time
from flask_restful import Resource, Api
from flask_restful import fields, marshal_with
from flask_restful import reqparse
from models import *

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, or_
from flask import current_app as app
from flask import request



section_parser = reqparse.RequestParser()
section_parser.add_argument('category_id', type=str)
section_parser.add_argument('category_name', type=str, required=True, help='category_name is required')
# section_parser = reqparse.add_argument('image_loc')


product_parser = reqparse.RequestParser()
product_parser.add_argument('product_id', type=str)
product_parser.add_argument('product_name', type=str, required=True, help='product_name is required')
product_parser.add_argument('category_id', type=str, required=True, help='category_id is required')
product_parser.add_argument('stock', type=str)
product_parser.add_argument('unit', type=str)
product_parser.add_argument('price', type=str)
product_parser.add_argument('mfd', type=str)
product_parser.add_argument('expd', type=str)
product_parser.add_argument('last_updated', type=str)
# product_parser = reqparse.add_argument('image_loc')

product_fields = {
	'product_id': fields.Integer,
	'product_name': fields.String,
	'category_id': fields.Integer,
	'stock': fields.Integer,
	'unit': fields.String,
	'price': fields.Integer,
	'mfd': fields.DateTime(dt_format='iso8601'),
	'expd': fields.DateTime(dt_format='iso8601'),
	'last_updated': fields.DateTime(dt_format='iso8601'),
}

category_fields = {
	'category_id': fields.Integer,
	'category_name': fields.String,
	'products': fields.List(fields.Nested(product_fields))
}

class SectionAPI(Resource):
	@marshal_with(category_fields)
	def get(self, category_id):
		if category_id =="all":
			sections = Category.query.all()
			return  sections, 200   
		section = Category.query.filter_by(category_id=category_id).first()
		if section:
			return section, 200
		return "Not Found", 404
	
	def post(self,category_id):
		args = section_parser.parse_args()
		# category_id = args.get('category_id', "New")
		category_name = args.get('category_name', "Unnamed")
		with app.app_context():
			section = Category.query.filter_by(category_name=category_name).first()
			if section:
				return 'Duplicate', 400
			new_section = Category(category_name=category_name)
			db.session.add(new_section)
			db.session.commit()
		return 'OK', 200

	# @marshal_with(category_fields)
	def put(self, category_id):
		args = section_parser.parse_args()
		# category_id = args.get('category_id', None)
		category_name = args.get('category_name',None)
		with app.app_context():
			section1 = Category.query.filter_by(category_id=category_id).first()
			section2 = Category.query.filter(and_(Category.category_name==category_name, Category.category_id!=category_id)).first()
			if section2:
				return 'Duplicate', 400
			if section1:
				section1.category_name = category_name
				db.session.commit()
				return 'Done', 200
			else:
				return "Invalid Category", 404

	def delete(self, category_id):
		with app.app_context():
			section = Category.query.filter_by(category_id=category_id).first()
			if section:
				products = Product.query.filter_by(category_id=category_id).all()
				for product in products:
					db.session.delete(product)
				db.session.delete(section)
				db.session.commit()
				return 'Done', 200
		return 'Not Found', 404


class ProductAPI(Resource):
	@marshal_with(product_fields)
	def get(self, product_id):
		if product_id == "all":
      
			parser = reqparse.RequestParser()
			parser.add_argument('name', location = 'args')
			parser.add_argument('expd', location = 'args')
			parser.add_argument('mfd', location = 'args')
			parser.add_argument('maxPrice', location = 'args')
			parser.add_argument('minPrice', location = 'args')
			parser.add_argument('qSection', location = 'args')
			args = parser.parse_args()
			name = args.get('name')
			expd = args.get('expd')
			# expd = args.get('expd', date.today() + timedelta(days=7))
			mfd = args.get('mfd', datetime.utcnow().isoformat())
			# mfd = args.get('mfd', date.today())
			maxPrice = args.get('maxPrice',1000000)
			minPrice = args.get('minPrice',0)
			qSection = args.get('qSection','%')

			if name == None or name == '':
				name = ''
				# print('hi')
			if expd == None or expd == '':
				expd = datetime.combine(date=date(2024,7,1), time=time(0,0,0)).isoformat()
				# print('hi')
			else:
				expd = datetime.fromisoformat(expd).isoformat()
			if mfd == None or mfd == '':
				mfd = datetime.combine(date=date(2023,7,1), time=time(0,0,0)).isoformat()
				# print('hi')
			else:
				mfd = datetime.fromisoformat(mfd).isoformat()
			if maxPrice == None or maxPrice == '':
				maxPrice = 1000000
				# print('hi')
			if minPrice == None or minPrice == '':
				minPrice = 0
				# print('hi')
			if qSection == None or qSection == '':
				qSection = '%'
				# print('hi')
			


			products = Product.query.filter(and_(Product.product_name.like(f'%{name}%'), Product.expd <= datetime.fromisoformat(expd), Product.mfd >= datetime.fromisoformat(mfd), Product.price <= maxPrice, Product.price >= minPrice, Product.category_id.like(f'{qSection}'))).order_by(Product.last_updated.desc()).all()
			# products = Product.query.filter(Product.product_name.like(f'%{name}%')).order_by(Product.last_updated).all()
			return  products, 200
   
   
			products = Product.query.order_by(Product.last_updated).all()
			return  products, 200
			
		else:			
			product = Product.query.filter_by(product_id=product_id).first()
			if product:		
				return product, 200
			else:
				return 'Not Found', 404

	def post(self,product_id):
		args = product_parser.parse_args()
		# product_id = args.get('product_id', "New")
		product_name = args.get('product_name', "Unnamed")
		category_id = args.get('category_id', None)
		stock = args.get('stock', '10')
		unit = args.get('unit', None)
		price = args.get('price', '100')
		try:
			stock = int(stock)
			price = int(price)
			mfd = datetime.fromisoformat(args.get('mfd', datetime.utcnow().isoformat()))
			# mfd = date.fromisoformat(args.get('mfd', date.today().isoformat()))
			expd = datetime.fromisoformat(args.get('expd', datetime.utcnow().isoformat()))
			# expd = date.fromisoformat(args.get('mfd', (date.today()+timedelta(days=7)).isoformat()))
		except Exception as e:
			return "Validation Error", 403
		last_updated = datetime.fromisoformat(datetime.utcnow().isoformat())
		with app.app_context():
			product = Product.query.filter_by(product_name=product_name).first()
			if product:
				return 'Duplicate', 400
			section = Category.query.filter_by(category_id=category_id).first()
			if section:
				new_product = Product(product_name=product_name,
					category_id=category_id,
					stock=stock,
					unit=unit,
					price=price,
					mfd=mfd,
					expd=expd, 
					last_updated=last_updated,
					category=section)
				db.session.add(new_product)	
				db.session.commit()
				return 'OK', 200
			else:
				return "Invalid Category", 404

    
	# @marshal_with(product_fields)
	def put(self,product_id):
		args = product_parser.parse_args()
		# product_id = args.get('product_id', None)
		product_name = args.get('product_name', None)
		category_id = args.get('category_id', None)
		with app.app_context():
			product1 = Product.query.filter_by(product_id=product_id).first()	
			product2 = Product.query.filter(and_(Product.product_name==product_name, Product.product_id!=product_id)).first()	
			section = Category.query.filter_by(category_id=category_id).first()
			try:
				stock = int(args.get('stock', str(product1.stock)))
				unit = args.get('unit', product1.unit)
				price = int(args.get('price', str(product1.price)))
				mfd = datetime.fromisoformat(args.get('mfd', product1.mfd))
				# mfd = date.fromisoformat(args.get('mfd', product1.mfd))
				expd = datetime.fromisoformat(args.get('expd', product1.expd))
				# expd = date.fromisoformat(args.get('expd', product1.expd))
			except Exception as e:
				return "Validation Error", 403
			last_updated = datetime.fromisoformat(datetime.utcnow().isoformat())
			if product2:
				return 'Duplicate', 400
			if section:
				if product1:
					product1.product_name = product_name
					product1.category_id = category_id
					product1.stock = stock
					product1.unit = unit
					product1.price = price
					product1.mfd = mfd
					product1.expd = expd
					product1.last_updated = last_updated
					db.session.commit()
					return "Done", 200 
				return 'Not Found', 404
		return "Invalid Category", 404	

	def delete(self, product_id):
		with app.app_context():		
			product = Product.query.filter_by(product_id=product_id).first()
			if product:
					db.session.delete(product)
					db.session.commit()
					return 'Done', 200
		return 'Not Found', 404