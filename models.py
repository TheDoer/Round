import datetime

from peewee import *
from flask.ext.login import UserMixin


DB = SqliteDatabase('peewee.db')

class BaseModel(Model):
	class meta:
		database = DB

class User(BaseModel, UserMixin):
	username = CharField()
	phone = IntegerField()
	email = CharField(unique=True, max_length=140)
	password = CharField(max_length=50)
	profile = TextField() 
	account_type = CharField(max_length=50)
	address = TextField()
	longitude = DoubleField(null=True)
	latitude = DoubleField(null=True)
	rating = DoubleField(default=0)
	date_joined = DateTimeField(default=datetime.datetime.now)

	@classmethod
	def create_user(cls, username='tatenda', phone=775527640, email='tatendazimba@gmail.com', account_type='buyer',
		password='tatenda',	address='77 Quorn Avenue, Mount Pleasant, Harare, Zimbabwe', profile='default.png'):

		cls.create(username=username, phone=phone, email=email, profile=profile, account_type=account_type,
			password=password, address=address)

class Suggestion(BaseModel):
	suggestion = TextField()
	user = ForeignKeyField(User, related_name="suggestions")
	date = DateTimeField(default=datetime.datetime.now)	
	scale = IntegerField()

	@classmethod
	def make_suggestion(cls, suggestion, user, scale):
		cls.create(suggestion=suggestion, user=user, scale=scale)


class Product(BaseModel):
	name = CharField(unique=True)
	date_created = DateTimeField(default=datetime.datetime.now)

	@classmethod
	def create_product(cls, name):
		cls.create(name=name)

class Unit(BaseModel):
	long_name = CharField(max_length=50, unique=True)
	short_name = CharField(max_length=10, unique=True)

	@classmethod
	def create_unit(cls, long_name, short_name):
		cls.create(long_name=long_name, short_name=short_name)

class Descriptor(BaseModel):
	description = CharField(max_length=140, unique=True)

	@classmethod
	def create_description(cls, description):
		cls.create(description=description)

class Brand(BaseModel):
	name = CharField(max_length=140, unique=True)
	image = TextField()

	@classmethod
	def create_brand(cls, name, image='shop-placeholder.png'):
		cls.create(name=name, image=image)

class Stock(BaseModel):
	product = ForeignKeyField(Product, related_name='in_stock')
	first_description = ForeignKeyField(Descriptor, related_name='in_stock_first')
	second_description = ForeignKeyField(Product, related_name='in_stock_second', null=True)
	third_description = ForeignKeyField(Product, related_name='in_stock_third', null=True)
	unit = ForeignKeyField(Unit, related_name='in_stock')
	quantity = IntegerField() #this is the quantity of units above. e.g 9kg 9 is the quantity, kg is the units
	minimum_quantity = IntegerField() # this is the seller's target
	brand = ForeignKeyField(Brand, related_name='in_stock')
	supplier = ForeignKeyField(User, related_name='products')
	price = DoubleField()
	bought = BooleanField(default=False)

	@classmethod
	def enter_stock(cls, product, first_description, unit, brand, supplier, price, 
		minimum_quantity=minimum_quantity, quantity=quantity, 
		second_description=None, third_description=None):

		cls.create(product=product, first_description=first_description,
			second_description=second_description, third_description=third_description,
			unit=unit, quantity=quantity, minimum_quantity=minimum_quantity, brand=brand,
			supplier=supplier, price=price)

class Order(BaseModel):
	buyer = ForeignKeyField(User, related_name='orders')
	stock = ForeignKeyField(Stock, related_name='orders')
	quantity = IntegerField()
	price = DoubleField()
	payment = DoubleField(default=0)
	ready = BooleanField(default=False)
	fulfilled = BooleanField(default=False)
	date_ordered = DateTimeField(default=datetime.datetime.now)

	@classmethod
	def make_order(cls, buyer, stock, quantity, price):

		cls.create(buyer=buyer, stock=stock, quantity=quantity, price=price)

if __name__ == '__main__':
	DB.create_tables([User, Product, Unit, Descriptor, Brand, Stock, Order, Suggestion], safe=True)
	print('Database successfully created!')
