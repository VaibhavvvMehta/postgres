import psycopg2
import random
from faker import Faker

fake = Faker()

conn = psycopg2.connect(
    host="localhost",
    database="e-commerce",
    user="admin",
    password="admin123",
    port=5432
)

cursor = conn.cursor()

# ---------------------
# Insert Categories
# ---------------------

categories = ["Electronics", "Clothing", "Books", "Sports", "Home"]

for c in categories:
    cursor.execute(
        """
        INSERT INTO categories (name)
        VALUES (%s)
        ON CONFLICT DO NOTHING
        """,
        (c,)
    )

conn.commit()

# ---------------------
# Get Category IDs
# ---------------------

cursor.execute("SELECT id FROM categories")
category_ids = [row[0] for row in cursor.fetchall()]

# ---------------------
# Insert Customers
# ---------------------

for _ in range(10000):

    name = fake.name()
    email = fake.unique.email()

    cursor.execute(
        """
        INSERT INTO customers (name, email)
        VALUES (%s, %s)
        ON CONFLICT (email) DO NOTHING
        """,
        (name, email)
    )

conn.commit()

cursor.execute("SELECT id FROM customers")
customer_ids = [row[0] for row in cursor.fetchall()]

# ---------------------
# Insert Products
# ---------------------

for _ in range(20000):

    name = fake.word().capitalize()
    description = fake.sentence()
    price = round(random.uniform(10, 2000), 2)

    category_id = random.choice(category_ids)

    cursor.execute(
        """
        INSERT INTO products (name, description, price, category_id)
        VALUES (%s, %s, %s, %s)
        """,
        (name, description, price, category_id)
    )

conn.commit()

cursor.execute("SELECT id FROM products")
product_ids = [row[0] for row in cursor.fetchall()]

# ---------------------
# Insert Orders
# ---------------------

for _ in range(50000):

    customer_id = random.choice(customer_ids)
    total_amount = round(random.uniform(20, 3000), 2)

    cursor.execute(
        """
        INSERT INTO orders (customer_id, status, total_amount)
        VALUES (%s, 'completed', %s)
        RETURNING id
        """,
        (customer_id, total_amount)
    )

conn.commit()

cursor.execute("SELECT id FROM orders")
order_ids = [row[0] for row in cursor.fetchall()]

# ---------------------
# Insert Order Items
# ---------------------

for _ in range(100000):

    order_id = random.choice(order_ids)
    product_id = random.choice(product_ids)

    quantity = random.randint(1, 5)
    price = round(random.uniform(10, 2000), 2)

    cursor.execute(
        """
        INSERT INTO order_items (order_id, product_id, quantity, price_at_purchase)
        VALUES (%s, %s, %s, %s)
        """,
        (order_id, product_id, quantity, price)
    )

conn.commit()

# ---------------------
# Insert Reviews
# ---------------------

review_pairs = set()

for _ in range(30000):

    customer_id = random.choice(customer_ids)
    product_id = random.choice(product_ids)

    if (customer_id, product_id) in review_pairs:
        continue

    review_pairs.add((customer_id, product_id))

    rating = random.randint(1, 5)
    comment = fake.sentence()

    cursor.execute(
        """
        INSERT INTO reviews (customer_id, product_id, rating, comment)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (customer_id, product_id) DO NOTHING
        """,
        (customer_id, product_id, rating, comment)
    )

conn.commit()

cursor.close()
conn.close()

print("Test data inserted successfully!")