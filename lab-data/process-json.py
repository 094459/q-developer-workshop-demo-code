import json
import pandas as pd

def generate_sql_from_json():
    # Read the JSON file
    with open('sample-product.json', 'r') as file:
        data = json.load(file)

    # Create SQL statements for products table
    products_sql = []
    vendors_sql = []
    details_sql = []

    # Create table definitions
    create_products_table = """
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        name VARCHAR(255),
        vendor_id INTEGER,
        requires_shipping BOOLEAN,
        sku VARCHAR(50),
        taxable BOOLEAN,
        status VARCHAR(50),
        price INTEGER,
        FOREIGN KEY (vendor_id) REFERENCES vendors(id)
    );
    """

    create_vendors_table = """
    CREATE TABLE IF NOT EXISTS vendors (
        id INTEGER PRIMARY KEY,
        name VARCHAR(255)
    );
    """

    create_details_table = """
    CREATE TABLE IF NOT EXISTS track_details (
        track_id INTEGER PRIMARY KEY,
        name VARCHAR(255),
        album_id INTEGER,
        media_type_id INTEGER,
        genre_id INTEGER,
        composer VARCHAR(255),
        milliseconds INTEGER,
        bytes INTEGER,
        unit_price DECIMAL(10,2),
        FOREIGN KEY (album_id) REFERENCES products(id)
    );
    """

    # Generate INSERT statements
    for product in data:
        # Product insert
        products_sql.append(
            f"""INSERT INTO products (id, name, vendor_id, requires_shipping, sku, taxable, status, price) VALUES ({product['id']}, '{product['name'].replace("'", "''")}', {product['vendor_id']}, {product['requires_shipping']}, '{product['sku']}', {product['taxable']}, '{product['status']}', {product['price']});"""
        )

        # Vendor insert (avoiding duplicates)
        vendor = product['vendor']
        vendor_insert = f"""INSERT INTO vendors (id, name) VALUES ({vendor['id']}, '{vendor['name'].replace("'", "''")}');"""
        if vendor_insert not in vendors_sql:
            vendors_sql.append(vendor_insert)

        # Details/tracks insert
        for detail in product['details']:
            composer = 'NULL' if detail['composer'] is None else f"""'{detail['composer'].replace("'", "''")}'"""
            details_sql.append(
                f"""INSERT INTO track_details (track_id, name, album_id, media_type_id, genre_id, composer, milliseconds, bytes, unit_price) VALUES ({detail['track_id']}, '{detail['name'].replace("'", "''")}', {detail['album_id']}, {detail['media_type_id']}, {detail['genre_id']}, {composer}, {detail['milliseconds']}, {detail['bytes']}, {detail['unit_price']});"""
            )

    # Write SQL to file
    with open('output.sql', 'w') as f:
        # Write create tables
        f.write(create_vendors_table + '\n')
        f.write(create_products_table + '\n')
        f.write(create_details_table + '\n')
        
        # Write inserts
        f.write('\n-- Vendor inserts\n')
        f.write('\n'.join(vendors_sql))
        
        f.write('\n\n-- Product inserts\n')
        f.write('\n'.join(products_sql))
        
        f.write('\n\n-- Track details inserts\n')
        f.write('\n'.join(details_sql))

if __name__ == "__main__":
    generate_sql_from_json()
