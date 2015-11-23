from peewee import *

from models import *

product = Product.select()[1]
desc = Descriptor.select()[1]
unit = Unit.select()[0]
brand = Brand.select()[0]
supplier = Supplier.select()[0]

Stock.enter_stock(product=product, first_description=desc, unit=unit, brand=brand,
	supplier=supplier, price=4.43, minimum_quantity=20, quantity=10)