import json
import os
from werkzeug import secure_filename

from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, current_user, login_required

from models import *

from models import User, Stock, Order, Product, Descriptor, Brand


DEBUG = True
PORT = 443
HOST = 'localhost'

app = Flask(__name__)
app.secret_key = 'mlskdjfisfwe[e20220i42mf2fra/aioh30mowgf0924mo2=gmvdVsv72v5v2vwvs5f3wef3wf83gf3v5esf1f3fw4vwvopw3ma31334ivlkwvog'
#login_manager = LoginManager()
#login_manager.init_app(app)
#login_manager.login_view = 'login'
'''
@login_manager.user_loader
def load_user(userid):
	return User.get(User.id==userid)
'''
@app.route('/register', methods=['POST', 'GET'])
def register():
	return render_template('register.html')

@app.route('/', methods=['POST', 'GET'])
#@login_required
def index():
	stocks = Stock.select().where(Stock.bought==False)
	stocks = [{'id': json.dumps(str(stock.id)) , 'stock': stock } for stock in stocks] # this will be used for adding listings to the homepage

	tags = [product.name for product in Product.select()]
	tags += [descriptor.description for descriptor in Descriptor.select()]
	tags += [brand.name for brand in Brand.select()]
	tags.sort()

	return render_template('buyer_dashboard.html', stocks=stocks, current_user=current_user,
		Order=Order, Stock=Stock, tags=tags, fn=fn)

@app.route('/login', methods=['POST', 'GET'])
def login():

	return render_template('login.html')

@app.route('/login-aunth', methods=['POST', 'GET'])
def login_aunth():
	try:
		email = dict(request.form.items())['email']
		password = dict(request.form.items())['password']

		user = User.get(User.email==email)

		if password != user.password:
			flash('Invalid login')
			return redirect(url_for('login'))
		else:
			#login_user(user)
			flash('Login successful')
			'''
			next = request.args.get('next')

			if not next_is_valid(next):
				return flask.abort(400)
			'''
			if user.account_type == 'buyer':
				return redirect(url_for('buyer'))
			elif user.account_type == 'supplier':
				return redirect(url_for('supplier'))
			else:
				redirect(url_for('shipping'))

	except KeyError: #some required fields blanks
		flash('Enter all details')
		return redirect(url_for('login'))
	except DoesNotExist: #user not found in database
		flash("Invalid login")
		return redirect(url_for('login'))

@app.route('/logout', methods=['POST', 'GET'])
#@login_required
def logout():
	#logout_user()
	return redirect(url_for('index'))

@app.route('/buyer/')
def buyer():
	stocks = Stock.select().where(Stock.bought==False)
	stocks = [{'id': json.dumps(str(stock.id)) , 'stock': stock } for stock in stocks] # this will be used for adding listings to the homepage

	tags = [product.name for product in Product.select()]
	tags += [descriptor.description for descriptor in Descriptor.select()]
	tags += [brand.name for brand in Brand.select()]
	tags.sort()

	return render_template('buyer_dashboard.html', stocks=stocks,
		Order=Order, Stock=Stock, tags=tags, fn=fn)

@app.route('/seller/')
def supplier():
	stocks = Stock.select().where(Stock.bought==False)
	stocks = [{'id': json.dumps(str(stock.id)) , 'stock': stock } for stock in stocks] # this will be used for adding listings to the homepage

	tags = [product.name for product in Product.select()]
	tags += [descriptor.description for descriptor in Descriptor.select()]
	tags += [brand.name for brand in Brand.select()]
	tags.sort()

	return render_template('supplier_dashboard.html', stocks=stocks, current_user=current_user,
		Order=Order, Stock=Stock, tags=tags, fn=fn)

@app.route('/shipping')
def shipping():

	tags = [product.name for product in Product.select()]
	tags += [descriptor.description for descriptor in Descriptor.select()]
	tags += [brand.name for brand in Brand.select()]
	tags.sort()

	return render_template('shipper_dashboard.html', Order=Order, Stock=Stock,
		tags=tags, fn=fn, current_user=current_user)

@app.route('/supplier/submit-product')
#@login_required
def submit_product():
	return render_template('supplier_submit_product.html', current_user=current_user)

@app.route('/order/<stock_id>/<quantity>')
def order(stock_id=None, quantity=''):
	quantity = int(quantity)

	if quantity != '' and quantity > 0: #validate the quantity given
		stock = Stock.get(Stock.id==stock_id)

		orders = Order.select(fn.sum(Order.quantity)).where(Order.stock==stock.id).scalar() #Get the current number of orders

		if orders == None: #I don't want a TypeError below
			orders = 0

		if quantity <= (stock.minimum_quantity - orders): #verify if quantity is less than or equal to the needed orders
			price = quantity * stock.price #calculate the amount the buyer has to pay
			Order.make_order(buyer=1, stock=stock, quantity=quantity, price=price)

			if stock.minimum_quantity == Order.select(fn.sum(Order.quantity)).where(Order.stock==stock.id).scalar(): #check if the target has been met
				stock.bought = True #update stock and set it to saved
				stock.save()
				orders = Stock.get(Stock.id==stock_id).orders

				for order in orders:
					order.ready = True
					order.save()

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

	return redirect(url_for('index'))

@app.route('/labs', methods=['POST'])
def labs():
	name = dict(request.form.items())['name']
	password = dict(request.form.items())['password']

	saved_name = 'tatenda'
	saved_password = 'tatenda as well'

	if saved_name == name:
		if saved_password == password:
			return 'success'
		else:
			return 'failed'
	else:
		return 'failed'

if __name__ == '__main__':
	app.run(debug=DEBUG, host=HOST, port=PORT)