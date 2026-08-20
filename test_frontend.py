import json
from bs4 import BeautifulSoup
from pprint import pprint

# check customers.js
with open('app/assets/www/js/customers.js') as f:
    print("CUSTOMERS.JS:")
    print("renderCustomers inside customers.js:", "renderCustomers(" in f.read())

