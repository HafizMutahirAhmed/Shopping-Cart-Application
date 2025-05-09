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
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY,
            rating INTEGER CHECK (rating BETWEEN 1 AND 5),
            comments TEXT,
            prod_id INTEGER NOT NULL,
            order_id INTEGER NOT NULL,
            customer_id INTEGER NOT NULL,
            FOREIGN KEY (prod_id) REFERENCES Products(id) ON DELETE CASCADE,
            FOREIGN KEY (order_id) REFERENCES Orders(id) ON DELETE CASCADE,
            FOREIGN KEY (customer_id) REFERENCES Users(id) ON DELETE CASCADE
        );

    ''')
        
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Cart (
            id INTEGER PRIMARY KEY NOT NULL UNIQUE,
            cart_product_quantity INTEGER NOT NULL,
            user_id INTEGER,
            product_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES Users(id),
            FOREIGN KEY (product_id) REFERENCES Products(id)
        )
    ''')
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Orders (
            id INTEGER PRIMARY KEY,
            order_date TEXT DEFAULT (DATE('now')),
            order_time TEXT DEFAULT (TIME('now')),
            total_amount INTEGER NOT NULL CHECK(total_amount >= 0),
            address TEXT NOT NULL,
            customer_id INTEGER NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('DELIVERED', 'PENDING')),
            FOREIGN KEY (customer_id) REFERENCES Users(id) ON DELETE CASCADE
        );

    ''')
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS OrderDetails (
            order_id INTEGER NOT NULL,
            prod_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            PRIMARY KEY (order_id, prod_id),
            FOREIGN KEY (order_id) REFERENCES Orders(id) ON DELETE CASCADE,
            FOREIGN KEY (prod_id) REFERENCES Products(id) ON DELETE CASCADE
        );
    ''')        
        self.cursor.execute('SELECT * FROM Users')
        rows = self.cursor.fetchall()
        
        self.connect.commit()
      