import json
import os
from werkzeug import secure_filename

from flask import Flask, render_template, session, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, current_user, login_required

from models import *

import forms


#DEBUG = True
#PORT = 3000
#HOST = 'localhost'
UPLOAD_FOLDER = 'static/img/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.secret_key = 'mlskdjfisfwe[e20220i42mf2fra/aioh30mowgf0924mo2=gmvdVsv72v5v2vwvs5f3wef3wf83gf3v5esf1f3fw4vwvopw3mviosvmwpvp3ma31334ivlkwvog'
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@login_manager.user_loader
def load_user(userid):
	return User.get(User.id==userid)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/register', methods=['POST', 'GET'])
def register():
	register_form = forms.RegisterForm()

	if register_form.validate_on_submit():
		User.create_user(
			username='unknown', 
			email=register_form.email.data,
			password=register_form.password.data,
			address=register_form.address.data,
			account_type='buyer',
			phone=register_form.phone.data)
		
		user = User.get(User.email==register_form.email.data)

		login_user(user)

		if user.account_type == 'buyer':
			return redirect(url_for('buyer'))
		elif user.account_type == 'supplier':
			return redirect(url_for('supplier'))
		else:
			return redirect(url_for('shipping'))
	
	return render_template('register.html', form=register_form)

@app.route('/supplier-register', methods=['POST', 'GET'])
def supplier_register():
	try:
		email = dict(request.form.items())['email']
		password = dict(request.form.items())['password']
		address = dict(request.form.items())['address']
		account_type = dict(request.form.items())['account_type']
		code = dict(request.form.items())['code']
		phone = dict(request.form.items())['phone']

		phone = int(str(code) + str(phone))

		User.create_user(username='unknown', email=email, password=password, address=address,
			account_type=account_type, phone=phone)

		user = User.get(User.email==email)

		login_user(user)

		if user.account_type == 'buyer':
			return redirect(url_for('buyer'))
		elif user.account_type == 'supplier':
			return redirect(url_for('supplier'))
		else:
			redirect(url_for('shipping'))

	except KeyError:
		flash('Please fill all fields')
		return render_template('supplier-register.html')

@app.route('/', methods=['POST', 'GET'])
def index():
	products = Product.select().limit(10)

	return render_template('index.html', products=products)

@app.route('/login', methods=['POST', 'GET'])
def login():
	login_form = forms.LoginForm()

	if login_form.validate_on_submit():
		try:
			user = User.get(User.email == login_form.email.data)

			if user.password == login_form.password.data:
				login_user(user)

				if user.account_type == 'buyer':
					return redirect(url_for('buyer'))
				elif user.account_type == 'supplier':
					return redirect(url_for('supplier'))
				else:
					redirect(url_for('shipping'))
			else:
				pass
		except DoesNotExist:
			pass

	return render_template('login.html', form=login_form)

@app.route('/logout', methods=['POST', 'GET'])
def logout():
	logout_user()
	return redirect(url_for('index'))

@app.route('/buyer')
@login_required
def buyer():
	stocks = Stock.select().where(Stock.bought==False)
	my_orders = current_user.orders.order_by(Order.date_ordered.desc())

	return render_template('buyer-dashboard.html', stocks=stocks,
		Order=Order, Stock=Stock, fn=fn, my_orders=my_orders, list=list)


@app.route('/buyer/feed', methods=['POST', 'GET'])
@app.route('/buyer/feed/<product>/<page>')
@app.route('/buyer/feed/<page>')
@login_required
def buyer_feed(product=None, page=None):
	feeds_per_page = 5

	if page == None:
		page = 1

	if product == None:
		stocks = Stock.select().where(Stock.bought==False).paginate(int(page), feeds_per_page)
	else:
		stocks = Product.get(Product.name==product).in_stock.where(Stock.bought==False).paginate(int(page), feeds_per_page)

	stocks = [{'id': json.dumps(str(stock.id)) , 'stock': stock, 'form': forms.OrderForm() } for stock in stocks] # this will be used for adding listings to the homepage

	stock_ids = [stock['id'] for stock in stocks ]

	for stock in stocks:	
		if stock['form'].validate_on_submit():
			quantity = order_form.quantity.data
			stock_id = dict(request.form.items())['stock_id']
			stock = Stock.get(Stock.id==stock_id)

			orders = Order.select(fn.sum(Order.quantity)).where(Order.stock==stock.id).scalar() #Get the current number of orders

			if orders == None: #I don't want a TypeError below
				orders = 0

			needed = stock.minimum_quantity - orders

			if quantity <= needed: #verify if quantity is less than or equal to the needed orders
				price = quantity * stock.price #calculate the amount the buyer has to pay
				Order.make_order(buyer=current_user.id, stock=stock, quantity=quantity, price=price)

				if stock.minimum_quantity == Order.select(fn.sum(Order.quantity)).where(Order.stock==stock.id).scalar(): #check if the target has been met
					stock.bought = True #update stock and set it to saved
					stock.save()
					orders = Stock.get(Stock.id==stock_id).orders

					for order in orders:
						order.ready = True
						order.save()
			else:
				flash('Your order exceeds the needed quantity of {}'.format(needed), 'error')

	tags = [product.name for product in Product.select()]
	tags += [descriptor.description for descriptor in Descriptor.select()]
	tags += [brand.name for brand in Brand.select()]
	tags.sort()

	return render_template('buyer-feed.html', stocks=stocks, current_user=current_user,
		Order=Order, Stock=Stock, tags=tags, fn=fn, int=int)

@app.route('/buyer/how-it-works', methods=['POST', 'GET'])
@login_required
def buyer_how_it_works():
	stocks = Stock.select().where(Stock.bought==False)
	stocks = [{'id': json.dumps(str(stock.id)) , 'stock': stock } for stock in stocks] # this will be used for adding listings to the homepage
	units = Unit.select()

	return render_template('buyer-how-it-works.html', stocks=stocks, Order=Order,
			current_user=current_user, Stock=Stock, fn=fn, units=units)


@app.route('/buyer/make-suggestion', methods=['POST', 'GET'])
@login_required
def buyer_make_suggestion():
	stocks = Stock.select().where(Stock.bought==False)
	stocks = [{'id': json.dumps(str(stock.id)) , 'stock': stock } for stock in stocks] # this will be used for adding listings to the homepage
	units = Unit.select()

	try:
		suggestion = dict(request.form.items())['suggestion']
		#scale = int(dict(request.form.items())['scale']) removed for now

		Suggestion.make_suggestion(suggestion=suggestion, scale=0, user=current_user.id)
		flash('Suggestion submitted. Thank you!', 'success')
		return redirect(url_for('buyer_make_suggestion'))
	except KeyError: #some required fields blanks
		return render_template('buyer-make-suggestion.html', stocks=stocks,
			current_user=current_user, Order=Order, Stock=Stock, fn=fn, units=units
		)
	except ValueError: #scale was text not number
		flash('Invalid entry. Please try again', 'error')
		return redirect(url_for('buyer_make_suggestion'))


@app.route('/seller')
@login_required
def supplier():
	stocks = Stock.select().where(Stock.bought==False)
	stocks = [{'id': json.dumps(str(stock.id)) , 'stock': stock } for stock in stocks] # this will be used for adding listings to the homepage
	my_stocks = current_user.products

	tags = [product.name for product in Product.select()]
	tags += [descriptor.description for descriptor in Descriptor.select()]
	tags += [brand.name for brand in Brand.select()]
	tags.sort()

	return render_template('supplier_dashboard.html', stocks=stocks, current_user=current_user,
		Order=Order, Stock=Stock, tags=tags, fn=fn, my_stocks=my_stocks, list=list)

@app.route('/seller/feed')
@login_required
def supplier_feed():
	stocks = Stock.select().where(Stock.bought==False)
	stocks = [{'id': json.dumps(str(stock.id)) , 'stock': stock } for stock in stocks] # this will be used for adding listings to the homepage

	tags = [product.name for product in Product.select()]
	tags += [descriptor.description for descriptor in Descriptor.select()]
	tags += [brand.name for brand in Brand.select()]
	tags.sort()

	return render_template('supplier-feed.html', stocks=stocks, current_user=current_user,
		Order=Order, Stock=Stock, tags=tags, fn=fn)

@app.route('/seller/add-product', methods=['POST', 'GET'])
@login_required
def seller_add_product():
	stocks = Stock.select().where(Stock.bought==False)
	stocks = [{'id': json.dumps(str(stock.id)) , 'stock': stock } for stock in stocks] # this will be used for adding listings to the homepage
	units = Unit.select()
	brands = Brand.select()
	descriptions = Descriptor.select()
	products = Product.select()
	prices = Stock.select(Stock.price)

	try:
		product = dict(request.form.items())['product']		
		brand = dict(request.form.items())['brand']
		description = dict(request.form.items())['description']
		quantity = dict(request.form.items())['quantity']
		price = dict(request.form.items())['price']
		unit = dict(request.form.items())['unit']
		target = dict(request.form.items())['target']
		
		image =  request.files['image']
		if image and allowed_file(image.filename):
			filename = secure_filename(image.filename)
			image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                
		product, created = Product.create_or_get(name=product)
		brand, created = Brand.create_or_get(name=brand, image=image.filename)
		description, created = Descriptor.create_or_get(description=description)
		unit = Unit.get(Unit.short_name==unit)

		#create stock
		stock, created = Stock.get_or_create(product=product, brand=brand, first_description=description,
				quantity=quantity, price=price, unit=unit, supplier=current_user.id,
				minimum_quantity=target)

		if created == False:
			flash('Stock item already exists', 'error')
		else:
			flash('Stock item successfully added.', 'success')
		return redirect(url_for('seller_add_product'))

	except IntegrityError:
		flash('Stock item already exists', 'error')
		return redirect(url_for('seller_add_product'))

	except KeyError:
		flash('Please fill in all fields', 'info')
		return render_template('seller-add-product.html', stocks=stocks,
			current_user=current_user, brands=brands, Order=Order,
			Stock=Stock, fn=fn, descriptions=descriptions, units=units,
			products=products, prices=prices)

@app.route('/seller/make-suggestion', methods=['POST', 'GET'])
@login_required
def seller_make_suggestion():
	stocks = Stock.select().where(Stock.bought==False)
	stocks = [{'id': json.dumps(str(stock.id)) , 'stock': stock } for stock in stocks] # this will be used for adding listings to the homepage
	units = Unit.select()

	try:
		suggestion = dict(request.form.items())['suggestion']
		#scale = int(dict(request.form.items())['scale']) removed for now

		Suggestion.make_suggestion(suggestion=suggestion, scale=0, user=current_user.id)
		flash('Suggestion submitted. Thank you!', 'success')
		return redirect(url_for('seller_make_suggestion'))
	except KeyError: #some required fields blanks
		return render_template('seller-make-suggestion.html', stocks=stocks,
			current_user=current_user, Order=Order, Stock=Stock, fn=fn, units=units
		)
	except ValueError: #scale was text not number
		flash('Invalid entry. Please try again', 'error')
		return redirect(url_for('seller_make_suggestion'))

@app.route('/shipping')
def shipping():

	tags = [product.name for product in Product.select()]
	tags += [descriptor.description for descriptor in Descriptor.select()]
	tags += [brand.name for brand in Brand.select()]
	tags.sort()

	return render_template('shipper_dashboard.html', Order=Order, Stock=Stock,
		tags=tags, fn=fn, current_user=current_user)

@app.route('/supplier/submit-product')
@login_required
def submit_product():
	return render_template('supplier_submit_product.html', current_user=current_user)

@app.route('/order', methods=['POST'])
@login_required
def order():
	try:
		quantity = int(dict(request.form.items())['quantity'])
		stock_id = dict(request.form.items())['stock_id']
		stock = Stock.get(Stock.id==stock_id)

		orders = Order.select(fn.sum(Order.quantity)).where(Order.stock==stock.id).scalar() #Get the current number of orders

		if orders == None: #I don't want a TypeError below
			orders = 0

		needed = stock.minimum_quantity - orders

		if (quantity <= needed and quantity >= stock.minimum_quantity/10) or quantity == needed: #verify if quantity is less than or equal to the needed orders
			price = quantity * stock.price #calculate the amount the buyer has to pay
			Order.make_order(buyer=current_user.id, stock=stock, quantity=quantity, price=price)

			if stock.minimum_quantity == Order.select(fn.sum(Order.quantity)).where(Order.stock==stock.id).scalar(): #check if the target has been met
				stock.bought = True #update stock and set it to saved
				stock.save()
				orders = Stock.get(Stock.id==stock_id).orders

				for order in orders:
					order.ready = True
					order.save()

				'''
				#replace the old stock with a fresh one with no orders yet
				new_stock = Stock.enter_stock(product=stock.product, first_description=stock.first_description,
					second_description=stock.second_description, third_description=stock.third_description,
					unit=stock.unit, quantity=stock.quantity, minimum_quantity=stock.minimum_quantity,
					brand=stock.brand, supplier=stock.supplier, price=stock.price)

				#send SMS's to shippers notifying them of ready deliveries
				for order in stock.orders:
					shippers = Courier.select()

					for shipper in shippers:
						# Account Sid and Auth Token from twilio.com/user/account
						account_sid = "AC7c8362f62f825e5184fe40e25958623d"
						auth_token  = "834c6ea95160009d251b3f06893768b2"
						client = TwilioRestClient(account_sid, auth_token)

						message = client.messages.create(body="Shipping: {} to {}. Reply with your price".format(order.stock.supplier.address, order.buyer.address),
						    to='+{}'.format(str(shipper.phone)),
						    from_="+14782885892")
						print(message.sid)
				'''
		else:
			flash('Your order exceeds the needed quantity of {}'.format(needed), 'error')

	except KeyError:
		pass

	return redirect(url_for('buyer_feed'))

@app.route('/labs', methods=['POST', 'GET'])
def labs():
	import requests
	import json

	send_url = 'http://freegeoip.net/json'
	r = requests.get(send_url)
	j = json.loads(r.text)
	lat = j['latitude']
	lon = j['longitude']

	return render_template('mapbox.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_errror(e):
    return render_template('500.html'), 500

@app.route('/about')
def about():
	return render_template('about-roundshopper.html')
	

if __name__ == '__main__':
	app.run()
	#app.run(debug=DEBUG, host=HOST, port=PORT)
