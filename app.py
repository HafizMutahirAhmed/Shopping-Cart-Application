from abc import ABC, abstractmethod
import shutil
import os

class DataHandler:
    import sqlite3 as sql
    connect = sql.connect('CEP.sqlite', check_same_thread=False)
    cursor = connect.cursor()
    logged_in_user = None

    @staticmethod
    def remove_folder(directory_path):
        if os.path.exists(directory_path):
            shutil.rmtree(directory_path)

    @staticmethod
    def create_folder(directory_path):
        DataHandler.remove_folder(directory_path)
        os.mkdir(directory_path) 

    def load_database(self):
        DataHandler.create_folder('./static')
        DataHandler.create_folder('./product_images')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Products(
            id INTEGER PRIMARY KEY NOT NULL UNIQUE,
            product_name TEXT NOT NULL,
            product_price INTEGER NOT NULL,
            product_description TEXT NOT NULL,
            product_stock INTEGER NOT NULL,
            product_image BLOB
        )
    ''')
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users(
            id INTEGER PRIMARY KEY NOT NULL UNIQUE,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            address TEXT,
            user_type TEXT NOT NULL
        )
    ''')
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS ShoppingHistory(
            id INTEGER PRIMARY KEY NOT NULL UNIQUE,
            order_date TEXT NOT NULL,
            order_time TEXT NOT NULL,
            total_amount TEXT NOT NULL,
            product_name TEXT NOT NULL,
            product_quantity TEXT NOT NULL,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES Users(id)
        )
    ''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS CartProducts(
            id INTEGER PRIMARY KEY NOT NULL UNIQUE,
            cart_product_quantity INTEGER NOT NULL,
            user_id INTEGER,
            product_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES Users(id),
            FOREIGN KEY (product_id) REFERENCES Products(id)
        )
    ''')
        self.cursor.execute('SELECT * FROM Users')
        rows = self.cursor.fetchall()
        
        self.connect.commit()
       
    def load_users(self):
        self.cursor.execute('SELECT * FROM Users')
        all_users = self.cursor.fetchall()
        users = []
        for user in all_users:
            if user[6] == 'admin':
                users.append(Admin(user[1],user[2],user[3],user[4],user[5]))
            elif user[6] == 'customer':
                users.append(Customer(user[1],user[2],user[3],user[4],user[5]))
        self.connect.commit()
        
        return users
    
    def save_user(self, user):  
        
        self.cursor.execute('''
        INSERT INTO Users(username, password, first_name, last_name, address, user_type) 
        VALUES (?,?,?,?,?,?)''', 
        (user.username, user.password,user.first_name, user.last_name, user.address,user.user_type)
        )
        self.connect.commit()
        
    def delete_user_from_database(self, user_name): 
        self.cursor.execute('SELECT id FROM Users WHERE username = ?', (user_name,))
        deleted_user_id = self.cursor.fetchone()[0]
        self.clear_cart_from_database(user_name)
        self.delete_history(deleted_user_id)
        self.cursor.execute('DELETE FROM Users WHERE username = ?',(user_name,))
        
        self.connect.commit()
    @staticmethod    
    def writeTofile(data, filename):
        with open(filename, 'wb') as file:
            file.write(data)
        


    def load_products(self):
        self.cursor.execute('SELECT * FROM Products')
        all_products = self.cursor.fetchall()
        products = []
        for product in all_products:

            photoPath = "./static/" + str(product[1]) + ".jpg"
            
            DataHandler.writeTofile(product[5], photoPath)
            products.append(Product(product[1], product[3], product[2], product[4], product[5]))
        return products
    
    def delete_product_from_database(self, product_name):
        self.cursor.execute('SELECT id FROM Products WHERE product_name = ?', (product_name,) )
        deleted_product_id = self.cursor.fetchone()[0]
        self.cursor.execute('DELETE FROM Products WHERE product_name = ?',(product_name,))
        self.cursor.execute('DELETE FROM CartProducts WHERE product_id = ?', (deleted_product_id,))
        self.connect.commit()
        
    def save_product(self, product):
        self.cursor.execute('''
            INSERT INTO Products(product_name, product_price, product_description, product_stock, product_image) 
            VALUES (?,?,?,?,?)''', (product.name, product.price, product.description, product.stock, product.image)
        )
        self.connect.commit()
    def update_product(self, product):
        
        self.cursor.execute('SELECT id FROM Products WHERE product_name = ?', (product.name,) )
        updated_product_id = self.cursor.fetchone()[0]
        
        self.cursor.execute('''
            UPDATE Products 
            SET product_name = ?, product_price = ?, product_description = ?, product_stock = ?, product_image=? WHERE id = ?''', 
            (product.name, product.price, product.description, product.stock,product.image, updated_product_id)
        )

        self.cursor.execute('SELECT id FROM Products WHERE product_name = ?', (product.name,))
        selected_product_id = self.cursor.fetchone()[0]
       
        self.cursor.execute(
                'DELETE FROM CartProducts WHERE product_id = ?',(selected_product_id,)
            )
        self.connect.commit()
    def load_cart(self):
        self.cursor.execute('SELECT id FROM Users WHERE username = ?', (self.logged_in_user.username,) )
        logged_user_id = self.cursor.fetchone()[0]
        self.cursor.execute('''
    SELECT Products.product_name, 
           Products.product_price, 
           Products.product_description, 
           Products.product_stock, 
           CartProducts.cart_product_quantity,
           Products.product_image
    FROM Products 
    JOIN CartProducts ON CartProducts.product_id = Products.id 
    WHERE CartProducts.user_id = ?
''', (logged_user_id,))
        all_cart_products = self.cursor.fetchall()
        self.connect.commit()
        return all_cart_products

    def save_cart_product(self, product, quantity, mode_of_operation = None, old_set_quantity = 0):
        self.cursor.execute('SELECT id FROM Users WHERE username = ?', (self.logged_in_user.username,))
        logged_user_id = self.cursor.fetchone()[0]

        self.cursor.execute('SELECT id FROM Products WHERE product_name = ?', (product.name,))
        selected_product_id = self.cursor.fetchone()[0]

        self.cursor.execute('SELECT product_stock FROM Products WHERE id = ?', (selected_product_id,))
        selected_product_stock = self.cursor.fetchone()[0]
        
        if mode_of_operation == 'update':
            self.cursor.execute(
                'DELETE FROM CartProducts WHERE product_id = ? AND user_id = ?',(selected_product_id, logged_user_id)
            )
        if mode_of_operation != 'checkout':
            self.cursor.execute(
                'INSERT INTO CartProducts(cart_product_quantity, user_id, product_id) VALUES (?, ?, ?)',
                (quantity, logged_user_id, selected_product_id)
            )

        if mode_of_operation == 'checkout':
            self.cursor.execute(
                'SELECT user_id, cart_product_quantity FROM CartProducts WHERE product_id = ?', (selected_product_id,)
            )
            other_users_carts = self.cursor.fetchall()
            
            for user_id, cart_quantity in other_users_carts:
                if user_id != logged_user_id:
                    if cart_quantity > selected_product_stock - quantity:
                        new_quantity = selected_product_stock - quantity
                        self.cursor.execute(
                            'UPDATE CartProducts SET cart_product_quantity = ? WHERE product_id = ? AND user_id = ?',
                            (new_quantity, selected_product_id, user_id)
                        )
                    else:
                        new_quantity = cart_quantity
                        self.cursor.execute(
                            'UPDATE CartProducts SET cart_product_quantity = ? WHERE product_id = ? AND user_id = ?',
                            (new_quantity, selected_product_id, user_id)
                        )
                           
            if (selected_product_stock - quantity) ==0:
                self.cursor.execute(
                    'DELETE FROM CartProducts WHERE product_id = ?',(selected_product_id,)
                )
            self.cursor.execute(
                'UPDATE Products SET product_stock = ? WHERE id = ?',
                (selected_product_stock - quantity, selected_product_id)
            )
            
        self.connect.commit()
    def delete_cart_products(self, mode, product = None, removed_product_quantity = 0):
        if mode == 'all_products':
            for cart_product in self.load_cart():
                self.cursor.execute('SELECT id FROM Products WHERE product_name = ?', (cart_product[0],))
                selected_product_id = self.cursor.fetchone()[0]

                self.cursor.execute(
                    'UPDATE Products SET product_stock = ? WHERE id = ?',
                    (cart_product[3] + cart_product[4], selected_product_id)
                )           
        elif mode == 'checkout':
            pass
        elif mode == 'single_product':
            self.cursor.execute('SELECT id FROM Products WHERE product_name = ?', (product.name,))
            selected_product_id = self.cursor.fetchone()[0]

            self.cursor.execute('SELECT product_stock FROM Products WHERE id = ?', (selected_product_id,))
            selected_product_stock = self.cursor.fetchone()[0]

            self.cursor.execute('SELECT id FROM Users WHERE username = ?', (self.logged_in_user.username,))
            logged_user_id = self.cursor.fetchone()[0]
            self.cursor.execute('DELETE FROM CartProducts WHERE product_id = ? AND user_id = ?',(selected_product_id, logged_user_id))

        self.connect.commit()

    def clear_cart_from_database(self, user_name, mode=None):
        self.cursor.execute('SELECT id FROM Users WHERE username = ?', (user_name,))
        logged_user_id = self.cursor.fetchone()[0]
        if mode == 'checkout':
            self.delete_cart_products(mode)
        else:
            self.delete_cart_products('all_products')
        self.cursor.execute('DELETE FROM CartProducts WHERE user_id = ?', (logged_user_id,))
        self.connect.commit()

        
    def load_history(self):
        self.cursor.execute('SELECT id FROM Users WHERE username = ?', (self.logged_in_user.username,))
        logged_user_id = self.cursor.fetchone()[0]
        self.cursor.execute('SELECT * FROM ShoppingHistory WHERE user_id = ?', (logged_user_id,))
        shopping_history = self.cursor.fetchall()
        self.connect.commit()
        
        return shopping_history
        
    def save_history(self, order_date, order_time, order_cost, product_name_and_quantity):
        self.cursor.execute('SELECT id FROM Users WHERE username = ?', (self.logged_in_user.username,))
        logged_user_id = self.cursor.fetchone()[0]

        for product_name, product_quantity in product_name_and_quantity.items():
            self.cursor.execute('''
                INSERT INTO ShoppingHistory
                (order_date, order_time, total_amount, product_name, product_quantity, user_id) VALUES (?,?,?,?,?,?)''',
                (order_date, order_time, order_cost, product_name, product_quantity, logged_user_id)
            )
        self.connect.commit()
    def delete_history(self, deleted_user_id):
        self.cursor.execute('DELETE FROM ShoppingHistory WHERE user_id = ?',(deleted_user_id,))
        self.connect.commit()
    
class User(ABC):
    def __init__(self, username, password, first_name, last_name, address, user_type):
        self.username = username
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.address = address   
        self.user_type = user_type  
    
    
    @abstractmethod    
    def view_products(self):
        pass

class Product:
   def __init__(self, name, description, price, stock, image):
       self.name = name
       self.description = description
       self.price = price
       self.stock = stock
       self.image = image


class Admin(User, DataHandler):
    def __init__(self, username, password, first_name, last_name, address):
        super().__init__(username, password, first_name, last_name, address, 'admin')
        self.products = self.load_products() #storing the list of Product type Object

    def view_products(self):
        self.products = self.load_products()
        if self.products == []:
            return 'no product'
        return self.products
    def add_product(self, name, description, price, stock, image):
        new_product = Product(name, description.capitalize(), price, stock, image)
            
        if self.products !=[]:
            for product in self.products:
                if new_product.name.lower() == product.name.lower():
                    product_in_database = True
                    break
                else:
                    product_in_database = False

            if product_in_database:
                flash("Can't add new product! This product is already in the database!")
            else:
                self.products.append(new_product)
                self.save_product(new_product)
                flash(f'{new_product.name} is been added successfully to the database!', 'success')
        else:
            self.products.append(new_product)
            self.save_product(new_product)
            flash(f'{new_product.name} is been added successfully to the database!', 'success')
        
    def remove_product(self, product_name):
        if self.products != []:
            for product in self.products:
                if product_name.lower() == product.name.lower():
                    del self.products[self.products.index(product)]
                    self.delete_product_from_database(product.name)
                    wrong_product_name = False
                    break
                else:
                    wrong_product_name = True
            
            if wrong_product_name:
                flash('Kindly enter the name of the Product correctly!!')
            else:
                flash(f'{product_name} is been successfully deleted from database!', 'success')
        else:
            flash('There is no product in the database yet!')
    

    def update_product_to_database(self, name, description=None, price=None, stock=None, image= None):
        if self.products !=[]:
            for product in self.products:
                if name.lower() == product.name.lower():
                    product_in_database = True
                    if description is not None:
                        product.description = description
                    if price is not None:
                        product.price = price
                    if stock is not None:
                        product.stock = stock
                    if image is not None:
                        product.image = image
                    self.update_product(product)
                    
                    break
                else:
                    product_in_database = False

            if product_in_database:
                flash(f'{product.name} is been added successfully to the database!', 'success')
            else:
                flash(f'The product name you have entered does not exist in database!', 'success')

                
           
        else:
            flash('There is no product in database yet!')
         
    


class Checkout(ABC):
    @abstractmethod
    def clear_cart(self): #abstract method
        pass
    
class Customer(User, DataHandler, Checkout):
    def __init__(self, username, password, first_name, last_name, address):
        super().__init__(username, password, first_name, last_name, address, 'customer')
        self.shopping_cart = Cart()
        self.shopping_history = ShoppingHistory()
        self.products = self.load_products()
     
    def view_products(self):
        self.products = self.load_products()
        if self.products == []:
            return 'no product'
        self.load_products()
        return self.products
    

        
        
    
    #**********************SHOPPING HISTORY FUNCTIONS*****************************
    def shopping_history_status(self):
        if self.shopping_history.shopping_records == []:
            return 'empty history'
        else:
            return 'not empty'
    def check_out(self):
        from datetime import date
        import time
        
        current_date = str(date.today())
        current_time = str(time.strftime("%H:%M:%S"))
        total_cost = self.shopping_cart.get_total_price()
        cart_items = {}
        for cart_product in self.shopping_cart.cart_products:
            cart_items[cart_product.name] = cart_product.cart_product_quantity

        self.add_record_to_shopping_history(cart_items, current_date, current_time, total_cost)
        self.save_history(current_date, current_time, total_cost, cart_items)
        self.clear_cart('checkout')
        self.products = self.load_products()
    
    def add_record_to_shopping_history(self, cart_products, order_date, order_time, cart_cost):
        self.shopping_history.add_shopping_record(cart_products, order_date, order_time, cart_cost)

    def view_shopping_history(self):
        for i in range(len(self.shopping_history.shopping_records)):
            try:
               if (self.shopping_history.shopping_records[i].order_time == self.shopping_cart.shopping_records[i+1].order_time):
                    
                    del self.shopping_history.shopping_records[i+1]
            except:
                pass
        return (self.shopping_history.view_history())

    def load_history_from_database(self):
        self.shopping_history.load_shopping_history(self.load_history())

    def get_shopping_history_by_date(self, date):
        return self.shopping_history.get_history_by_date(date)

    #*****************CART FUNCTIONS***************************
    def load_cart_from_database(self):
        self.shopping_cart.load_cart_products(self.load_cart())

    def clear_cart(self, mode= None):
        for cart_product in self.shopping_cart.cart_products:
            self.save_cart_product(cart_product, cart_product.cart_product_quantity, 'checkout')
        self.shopping_cart.cart_products.clear()
        if mode == 'checkout':
            self.clear_cart_from_database(self.username, mode)
        else:
            self.clear_cart_from_database(self.username)
    def cart_status(self):
        if self.shopping_cart.cart_products == []:
            return 'empty cart'
        else:
            return 'not empty'
    def add_product_to_cart(self, selected_product_name, selected_product_quantity):
        selected_product_quantity = int(selected_product_quantity)
        if self.products != []:
            for product in self.products:
                if product.name.lower() == selected_product_name.lower() and product.stock >= (selected_product_quantity) and selected_product_quantity!=0:
                    correct_product_name = True
                    correct_product_quantity = True
                    selected_product = product
                    break
                else:
                    correct_product_name = False
                    correct_product_quantity = False

            if correct_product_name and correct_product_quantity:        
                if self.shopping_cart.add_product(selected_product, selected_product_quantity) == 'product already exists!':
                    
                    self.update_cart_product_quantity(selected_product_name, selected_product_quantity)

                else:
                    self.save_cart_product(selected_product, selected_product_quantity)
                    
            else:
                pass
        else:
            pass
    def remove_cart_product(self, selected_product_name):

        if self.shopping_cart.cart_products != []:
            for product in self.products:
                if selected_product_name.lower() == product.name.lower():
                    product_to_be_removed = product
                    wrong_product_name = False
                    product_name = product.name
                    break
                else:
                    wrong_product_name = True
            if wrong_product_name:
                pass
            else:
                quantity_to_be_removed = self.shopping_cart.get_product_quantity(product_to_be_removed)
                self.shopping_cart.remove_product(product_to_be_removed)
                self.delete_cart_products('single_product', product_to_be_removed, quantity_to_be_removed)
                flash(f'Product {product_name} is been deleted successfully!', 'success')
        else:
           pass

    def update_cart_product_quantity(self, selected_product_name, selected_product_quantity):
        
        if self.shopping_cart.cart_products != []:
            selected_product_quantity = int(selected_product_quantity)
            for product in self.shopping_cart.cart_products:
                if product.name.lower() == selected_product_name.lower() and product.stock >= selected_product_quantity and selected_product_quantity != 0:
                    correct_product_name = True
                    correct_product_quantity = True
                    selected_product = product
                    product_name = product.name
                    print('THE PRDOUCT STOCK IS:',product.stock,'THE SELECTED QUANTIYT IS:',selected_product_quantity)
                    break
                else:
                    correct_product_name = False
                    correct_product_quantity = False
            if correct_product_name and correct_product_quantity:
                old_quantity = self.shopping_cart.get_product_quantity(selected_product)
                self.shopping_cart.update_quantity(selected_product, selected_product_quantity, old_quantity)
                self.save_cart_product(selected_product, selected_product_quantity, 'update', old_quantity)
                flash(f'Product {product_name} is been updated successfully', 'success')
            
            else:
                flash('You have entered an invalid quantity!')
        else:
            pass
    def view_cart(self):
        return self.shopping_cart.view_cart_products()

    def get_individual_cart_products_price(self, product):
        print(self.shopping_cart.get_individual_product_price(product))
    
    def get_cart_price(self):
        return self.shopping_cart.get_total_price()
    
class AccountManager(DataHandler):
    def __init__(self):
        self.users = self.load_users()    #Storing object of Customer and Admin classes
        
    def create_account(self, user_type, username, password, first_name, last_name, address):
        if user_type.lower() == 'customer':
            new_user = Customer(username, password, first_name, last_name, address)
    
        elif user_type.lower() == 'admin':
            new_user = Admin(username, password, first_name, last_name, address)
            
        else:          
            return ("invalid user type")
        
        if self.users != []:
            for user in self.users:
                if user.username.lower() == new_user.username.lower():
                    user_in_database = True
                    break
                else:
                    user_in_database = False
            
            if user_in_database:
                return('user already exists')
            else:
                self.users.append(new_user)
                self.save_user(new_user)
                
                return ('account created successfully')
        else:
            self.users.append(new_user)
            self.save_user(new_user)
            
            return ('account created successfully')
        
    def remove_account(self, user_name, password):
            for user in self.users:
                if user.username == user_name and user.password == password:
                    correct_credentials = True
                    del self.users[self.users.index(user)]
                    break
                else:
                    correct_credentials = False
                    
            if correct_credentials:    
                self.delete_user_from_database(user_name)
                DataHandler.logged_in_user = None
                
            else:
                pass
        

    def validate_login(self, user_name, password):
        if self.users != []:
            for user in self.users:
                if (user.username == user_name and user.password == password):
                    login_success = True
                    break
                else:
                    login_success = False
            if login_success:
                    DataHandler.logged_in_user = user
                    
            else:
                DataHandler.logged_in_user = None
class CartProduct(Product):
    def __init__(self, name, quantity, description, price, stock, image):
        super().__init__(name, description, price, stock, image)
        self.cart_product_quantity = quantity


class Cart:
    def __init__(self):
        self.cart_products = []
 
    def load_cart_products(self, cart_products):
        for cart_product in cart_products:
            
            self.cart_products.append(
                CartProduct(cart_product[0], cart_product[4], cart_product[2], cart_product[1], cart_product[3], cart_product[5])
            )
    def add_product(self, product, quantity):
        if self.cart_products != []:
            for cart_product in self.cart_products: 
                
                if product.name.lower() == cart_product.name.lower():
                    old_quantity = cart_product.cart_product_quantity
                    product_already_exists = True
                    break
                else:
                    product_already_exists = False
            if product_already_exists:
                return 'product already exists!'
            else:
                self.cart_products.append(
                    CartProduct(product.name, quantity, product.description, product.price, product.stock, product.image)
                )
        else:
            self.cart_products.append(
                    CartProduct(product.name, quantity, product.description, product.price, product.stock, product.image)
                )
    def remove_product(self, product):
        for cart_product in self.cart_products: 
            if product.name.lower() == cart_product.name.lower():
                del self.cart_products[self.cart_products.index(cart_product)]
                correct_product_name = True
                break
            else:
                correct_product_name = False
        if correct_product_name:
           pass
        else:
           pass

    def update_quantity(self, product, quantity, old_quantity):
        for cart_product in self.cart_products:
            if cart_product.name.lower() == product.name.lower():
                cart_product.cart_product_quantity = quantity
        
        
    def view_cart_products(self):
        
        if self.cart_products == []:
            return 'empty cart'
        

        return self.cart_products

    def get_individual_product_price(self, product):
        for cart_product in self.cart_products:
            if cart_product.name.lower() == product.name.lower():
                return f"The total cost of {cart_product.name} is: {int(product.description) * int(cart_product.cart_product_quantity)}"
    def get_total_price(self):
        total_cost = 0
        for cart_product in self.cart_products:
            total_cost += (int(cart_product.price)*int(cart_product.cart_product_quantity))
           
        return total_cost
    def get_product_quantity(self, product):
        for cart_product in self.cart_products:
            if cart_product.name.lower() == product.name.lower():
                return cart_product.cart_product_quantity

class ShoppingHistory:
    def __init__(self):
        self.shopping_records = []
    
    def load_shopping_history(self, shopping_history):
     for database_record in shopping_history:
        found = False  

        if self.shopping_records:
            for record in self.shopping_records:
                if (database_record[2] == record.order_time) and (str(database_record[1]) == str(record.order_date)):
                    record.add_items(database_record[4], database_record[5])
                    found = True  
                    break  

        if not found:
           
            self.shopping_records.append(
                ShoppingRecord(
                    {database_record[4]: database_record[5]}, 
                    database_record[1], 
                    database_record[2], 
                    database_record[3]
                )
            )
                
            
                
    
        
        
    def view_history(self):
        return self.shopping_records
    
    def get_total_spent(self):
        total_spent = 0
        for single_record in self.shopping_records:
            total_spent += single_record.total_amount 
        return total_spent

    def get_history_by_date(self, date):
        records_by_date = []
        for single_record in self.shopping_records:
            if str(single_record.order_date) == date:
                
                records_by_date.append(single_record)
        return records_by_date
            
    def add_shopping_record(self, cart_products, order_date, order_time, total_amount):
        self.shopping_records.append(ShoppingRecord(cart_products, order_date, order_time, total_amount))

    
        
class ShoppingRecord:
    def __init__(self, cart_products, order_date, order_time, total_amount):
        self.order_items = cart_products #dict of product name to quantity
        self.order_date = order_date
        self.order_time = order_time    
        self.total_amount = total_amount
        
    def add_items(self, product_name, product_quantity):
        self.order_items[product_name] = product_quantity
      















































from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)

app.secret_key = 'supersecretkey'

DataHandler().load_database()
account_manager = AccountManager()
logged_user = None
@app.route('/')
def index():
    if logged_user is None:
        return render_template('login.html')
    return redirect(url_for('products'))    

@app.route('/login', methods=['GET','POST'])
def login():
    
    if request.method == 'POST':
        global logged_user
        username = request.form['username']
        password = request.form['password']
        
        
        account_manager.validate_login(username, password) 
        
        
        logged_user = account_manager.logged_in_user  
       
        if isinstance(logged_user, Customer):
            
            logged_user.load_cart_from_database()
            logged_user.load_history_from_database()
            return redirect(url_for('products'))
        elif isinstance(logged_user, Admin):
            return redirect(url_for('admin_dashboard'))
        message = 'invalid credentials!'
        return render_template('login.html', message = message)
    
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])

def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        address = request.form['address']
        user_type = request.form['user_type']
        
        account_creation_status = account_manager.create_account(user_type, username, password, first_name, last_name, address)
        if account_creation_status == 'account created successfully':
            account_manager.validate_login(username, password)
            global logged_user  
            logged_user = account_manager.logged_in_user
            if isinstance(logged_user, Customer):
                logged_user.load_cart_from_database()
                logged_user.load_history_from_database()
                return redirect(url_for('products'))
            elif isinstance(logged_user, Admin):
                return redirect(url_for('admin_dashboard'))
            
            
        elif account_creation_status == 'invalid user type':
            message = 'Invalid user type! Kindly write Admin or Customer'
            return render_template('signup.html', message=message)
        elif account_creation_status == 'user already exists':
            message = 'This user is already exists! Try logging in!'
            return render_template('signup.html', message=message)  
        
    return render_template('signup.html')


@app.route('/products',methods=['GET', 'POST'])
def products():
    if logged_user is None:
        return redirect(url_for('login'))
    if request.method == 'GET':
        products = logged_user.view_products()
        try:
            for product in products:
                product.image_url = url_for('static', filename=str(product.name)+'.jpg')
        except:
            pass
        
        return render_template('products.html', products=products, user = logged_user)

@app.route('/logout')
def logout():
    global logged_user
    logged_user = None
    DataHandler().load_database()
    global account_manager
    account_manager = AccountManager()
    
    
    return redirect(url_for('login'))

@app.route('/add_to_cart/<product_name>', methods=['GET', 'POST'])
def add_to_cart(product_name):
    if logged_user is None:
        return redirect(url_for('login'))
    if request.method == 'POST': 
        user = logged_user
    
        product_quantity = request.form['qty']
    
        
        user.add_product_to_cart(product_name, product_quantity)
        flash(f'Product {product_name} is been added successfully to cart!', 'success')
        return redirect(url_for('products'))
    

@app.route('/cart', methods=['GET', 'POST'])
def cart(): 
    if logged_user is None:
        return redirect(url_for('login'))
    user = logged_user 
    
    cart_items = user.view_cart()
    try:
        for product in cart_items:
            product.image_url = url_for('static', filename=str(product.name)+'.jpg')
    except:
        pass
    total_amount = user.get_cart_price()
    if request.method == 'POST': 
        product_quantity = request.form['qty']
        product_name = request.form['product_name']
        user.update_cart_product_quantity(product_name, product_quantity)
    return render_template('cart.html', cart=cart_items, total = total_amount, user = logged_user)

@app.route('/delete_product', methods=['POST'])
def delete_product():
    if logged_user is None:
        return redirect(url_for('login'))
    user = logged_user
    product_name = request.form['deleted_product_name']
    
    user.remove_cart_product(product_name)
    
    return redirect(url_for('cart'))

@app.route('/update_cart', methods=['POST'])
def update_cart():
    if logged_user is None:
        return redirect(url_for('login'))
    user = logged_user
    product_name = request.form['updated_product_name']
    product_quantity = request.form['updated_quantity']
  
    user.update_cart_product_quantity(product_name, product_quantity)
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if logged_user is None:
        return redirect(url_for('login'))
    
    if request.method == 'POST' and request.form.get('checkout_access') == 'allowed':
        user = logged_user
        user.check_out()
        return render_template('checkout.html', user = logged_user)
    
    return redirect(url_for('cart'))


@app.route('/remove_account')
def remove_account():
    if logged_user is None:
        return redirect(url_for('login'))
    return render_template('remove_account.html', user = logged_user)


@app.route('/confirm_remove_account', methods=['POST'])
def confirm_remove_account():
    
    global logged_user
    if logged_user is None:
        return redirect(url_for('login'))
    confirm = request.form.get('confirm')
    
    if confirm == 'yes':
        account_manager.remove_account(logged_user.username, logged_user.password)
     
        
        logged_user = None
        return redirect('/')
    else:
     
        return redirect('/remove_account')

@app.route('/history', methods=['GET', 'POST'])
def history():
    if logged_user is None:
        return redirect(url_for('login'))
    user = logged_user
    history = user.view_shopping_history()
    if request.method == 'POST':
        search_date = request.form['search_date']
        history_by_date = user.get_shopping_history_by_date(search_date)
        
        return render_template('history.html', history=history_by_date, search_performed=True, user = logged_user)
    return render_template('history.html', history=history,search_performed=False, user = logged_user)
    


def convertToBinaryData(filename):
    with open(filename, 'rb') as file:
        blobData = file.read()
    return blobData


@app.route('/admin_dashboard', methods=['POST', 'GET'])
def admin_dashboard():
    if logged_user is None:
        return redirect(url_for('login'))
    user = logged_user
    if request.method == 'POST': 
        name = request.form['name']
        
        stock = int(request.form['stock'])
        price = float(request.form['price'])
  
        description = request.form['description']

        import os
        file1 = request.files['image_url']
        path = os.path.join('product_images', file1.filename)
        file1.save(path)


        image_blob = convertToBinaryData(path)

        user.add_product(name, description, price, stock, image_blob)
            
        

   
    return render_template('admin_dashboard.html', user= logged_user)

@app.route('/admin/remove', methods=['POST'])
def remove_product():
    if logged_user is None:
        return redirect(url_for('login'))
    user = logged_user
    name = request.form['name']
    user.remove_product(name)
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/update', methods=['POST'])
def update_product():
    if logged_user is None:
        return redirect(url_for('login'))
    name = request.form['name']
    user = logged_user
    stock = None
    price = None
    description = None
    image_blob = None
    if request.form['stock']:
        stock = int(request.form['stock'])
    if request.form['price']:
        price = float(request.form['price'])
    if request.files['image_url']:
        file1 = request.files['image_url']
        import os
        file1 = request.files['image_url']
        path = os.path.join('product_images', file1.filename)
        file1.save(path)
        image_blob = convertToBinaryData(path)
    if request.form['description']:
        description = request.form['description']
    user.update_product_to_database(name, description, price, stock, image_blob)
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
