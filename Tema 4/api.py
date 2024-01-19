from flask import Flask, request, jsonify
from flask_cors import CORS

import sqlite3

app = Flask("main_api")
CORS(app, resources=r'/api/*')

database = "productsdb.db"
#  Pydantic validation
# Pydantic flask
@app.route("/api/v1/add-product", methods=["POST"])
def create_product():
    body = request.json
    try:
        connection = sqlite3.connect(database)
        cursor = connection.cursor()
        query = "INSERT INTO products (name, price, stock) VALUES (?, ?, ?)"
        cursor.execute(query, (body['name'], body['price'], body['stock']))
        
        connection.commit()
        connection.close()

        return jsonify({'message': 'Product added successfully'}), 201
    except Exception as e:
        response = {
            "message": f"Something went wrong. Cause: {e}."
        }
        response = jsonify(response)
        return response, 500

@app.route("/api/v1/read-products", methods=["GET"])
def read_product():
    try:
        connection = sqlite3.connect(database)
        cursor = connection.cursor()

        query = """SELECT id, name, price, stock FROM products"""
        cursor.execute(query)
        products = cursor.fetchall()
        response_data = []
        for product in products:
            product_dict = {
                "id": product[0],
                "name": product[1],
                "price": product[2],
                "stock": product[3]
            }
            response_data.append(product_dict)
        connection.close()
        return jsonify({"data": response_data}), 200
    except Exception as e:
        response = {
            "message": f"Something went wrong. Cause: {e}."
        }
        response = jsonify(response)
        return response, 500
    
@app.route("/api/v1/update-product/<product_id>", methods=["PUT"])
def update_product(product_id):
    body = request.json
    try:
        connection = sqlite3.connect(database)
        cursor = connection.cursor()
        check_query = "SELECT * FROM products WHERE id = ?"
        cursor.execute(check_query, (product_id,))
        existing_product = cursor.fetchone()

        if not existing_product:
            raise Exception('Product not found!')
        
        update_query = """UPDATE products SET name=?, price=?, stock=? WHERE id=?"""
        cursor.execute(update_query, (body['name'], body['price'], body['stock'], product_id))
        connection.commit()
        connection.close()
        return jsonify({'message': 'Product succesfully updated.'}), 200
    except Exception as e:
        response = {
                "message": f"Something went wrong. Cause: {e}."
            }
        response = jsonify(response)
        return response, 500

@app.route("/api/v1/delete-product/<product_id>", methods=["DELETE"])
def delete_product(product_id):
    body = request.json
    try:
        connection = sqlite3.connect(database)
        cursor = connection.cursor()
        check_query = "SELECT * FROM products WHERE id = ?"
        cursor.execute(check_query, (product_id,))
        existing_product = cursor.fetchone()
        if not existing_product:
            raise Exception('Product not found!')
        delete_query = "DELETE FROM products WHERE id = ?"
        cursor.execute(delete_query, (product_id,))
        connection.commit()
        connection.close()
        return jsonify({'message': 'Product succesfully deleted.'}), 200
    except Exception as e:
        response = {
                "message": f"Something went wrong. Cause: {e}."
            }
        response = jsonify(response)
        return response, 500
if __name__ == "__main__":
    app.run(debug=True, port=5001)