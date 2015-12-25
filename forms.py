from flask_wtf import Form
from wtforms import (StringField, PasswordField, SelectField, DecimalField, 
					 SubmitField, TextAreaField, IntegerField, HiddenField)
from wtforms.validators import (DataRequired, Regexp, ValidationError, Email,
								 Length, EqualTo, Optional, NumberRange)
from flask.ext.login import (LoginManager, login_user, logout_user,
							 login_required, current_user)

import models

def account_exists(form, field):
	if (models.User.get(models.User.id==current_user.id).accounts
				   .where(models.Account.name==field.data)
				   .exists()):
		raise ValidationError("Account already exists")

def name_exists(form, field):
	if models.User.select().where(models.User.username == field.data).exists():
		raise ValidationError("Username already exists")

def email_exists(form, field):
	if models.User.select().where(models.User.email == field.data).exists():
		raise ValidationError("Email already exists")

def invalid_login(form, field):
	if models.User.select().where(models.User.email == form.email.data).exists:
		if models.User.get(models.User.email==form.email.data).password != form.password.data:
			raise ValidationError('Email or password does not match')
	else:
		raise ValidationError('Email or password does not match')

def getuser():
	my_list = [('', '')]
	users = models.User.select()
	for user in users:
		my_list.append((user.id, user.username))
	return my_list

class RegisterForm(Form):
	email = StringField(
						'Your Email',
			   			   validators = [
			   			   				 DataRequired(),
			   			   				 Email(),
			   			   				 email_exists
			])

	password = PasswordField(
							 'Password',
				   			 validators = [
				   			 				DataRequired(),
				   			   				Length(min=8),
				   			   				EqualTo('confirm_password', message='Passwords must match')
			   ])
			   
	confirm_password = PasswordField(
									 'Confirm Password',
									 validators = [
									 				DataRequired()
									 ]
						)
	
	phone = IntegerField(
			   			   'Contact Phone Number',
			   			   validators = [
			   			   					DataRequired(),
											NumberRange(min=263710000000, message='Invalid phone number. Correct format: 263712345678')
			   	])

	address = TextAreaField(
			   			   'Delivery Address',
			   			   validators = [
			   			   					DataRequired()
			   	])

class OrderForm(Form):
	quantity = IntegerField(
					'Order Quantity',
			   		validators = [
			   			DataRequired(),
			   			NumberRange(min=100, message='The Minimum Order Quantity (MOQ) is 100')
			   	])


class LoginForm(Form):
    email = StringField('Email', validators=[DataRequired(), Email(), invalid_login])
    password = PasswordField('Password', validators=[DataRequired(), invalid_login])

class IncomeForm(Form):
	name = StringField('Account name',
								validators = [
								DataRequired(), 
								Regexp(r'^[a-zA-Z_ ]+$',
								message = ('Account name should be '
			   			   				 					'letters and under_scores')
			   			   		),
			   			   		account_exists
								])
								
class ExpenseForm(Form):
	name = StringField('Account name',
								validators = [
								DataRequired(), 
								Regexp(r'^[a-zA-Z_ ]+$',
								message = ('Account name should be '
			   			   				 					'letters and under_scores')
			   			   		),
			   			   		account_exists
								])

class EquityForm(Form):
	name = StringField('Account name',
								validators = [
								DataRequired(), 
								Regexp(r'^[a-zA-Z0-9_,. ]+$',
								message = ('Account name has invalid symbols')
			   			   		),
			   			   		account_exists
								])

class AssetForm(Form):
	name = StringField('Account name',
								validators = [
								DataRequired(), 
								Regexp(r'^[a-zA-Z_ ]+$',
								message = ('Account name should be '
			   			   				 					'letters and under_scores')
			   			   		),
			   			   		account_exists
								])
	asset_type = SelectField('Asset Type',
							 choices=[('current asset', 'Current Asset'), 
									  ('noncurrent asset', 'Noncurrent Asset')
									 ],
								validators=[DataRequired()]
							)

class LiabilityForm(Form):
	name = StringField('Account name',
								validators = [
								DataRequired(), 
								Regexp(r'^[a-zA-Z_ ]+$',
								message = ('Account name should be '
			   			   				 					'letters and under_scores')
			   			   		),
			   			   		account_exists
								])
	liability_type = SelectField('Liability Type',
								 choices=[('current liability', 'Current Liability'), 
										  ('noncurrent liability', 'Noncurrent Liability')
										 ],
								validators=[DataRequired()]
							)

class JournalEntryForm(Form):
	first_debit = DecimalField('DEBIT', 
								places=2,
								validators=[
								Optional(),
								NumberRange(min=0, message='Invalid input. LINE 1')
								]
							  )

	first_credit = DecimalField('CREDIT', 
								places=2, 
								validators=[
								Optional(),
								NumberRange(min=0, message='Invalid input. LINE 1')
								]
							  )
	
	first_account = SelectField(u'Account')

	second_debit = DecimalField('DEBIT', 
								places=2, 
								validators=[
								Optional(),
								NumberRange(min=0, message='Invalid input. LINE 2')
								]
							  )
							  
	second_credit = DecimalField('CREDIT', 
								places=2, 
								validators=[
								Optional(),
								NumberRange(min=0, message='Invalid input. LINE2')
								]
							  )
	
	second_account = SelectField(u'Account')
	
	third_debit = DecimalField('DEBIT', 
								places=2, 
								validators=[
								Optional(),
								NumberRange(min=0, message='Invalid input. LINE 3')
								]
							  )
	
	third_credit = DecimalField('CREDIT', 
								places=2, 
								validators=[
								Optional(),
								NumberRange(min=0, message='Invalid input. LINE 3')
								]
							  )
	
	third_account = SelectField(u'Account')
	
	fourth_debit = DecimalField('DEBIT', 
								places=2, 
								validators=[
								Optional(),
								NumberRange(min=0, message='Invalid input. LINE 4')
								]
							  )
	
	fourth_credit = DecimalField('CREDIT', 
								places=2, 
								validators=[
								Optional(),
								NumberRange(min=0, message='Invalid input. LINE 4')
								]
							  )
	fourth_account = SelectField(u'Account')

