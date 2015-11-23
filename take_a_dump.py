import csv, sqlite3 # Will use these to dump database contents to csv file
import os

from models import (DB, Buyer, Supplier, Product, Staff, Courier, Unit, Descriptor,
	Brand, Stock, Order)

from peewee import *
try:
	os.mkdir('csv')
except FileExistsError:
	pass


db = sqlite3.connect('peewee.db')

for table in DB.get_tables():
	with open('csv/{}s.csv'.format(table), 'w') as csv_file:
		try :
			writer = csv.writer(csv_file)
			cur = db.cursor()
			cur.execute('SELECT * FROM {}'.format(table)) 
			
			writer.writerow([description[0] for description in cur.description])
			writer.writerows(cur)
		except sqlite3.OperationalError:
			pass

print('Dump taken with much success')