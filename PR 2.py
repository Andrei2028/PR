from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
socketio = SocketIO(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String(50))

db.create_all()

@app.route('/products', methods=['POST'])
def create_product():
    data = request.json
    product = Product(name=data['name'], price=data['price'], color=data.get('color', ''))
    db.session.add(product)
    db.session.commit()
    return jsonify({'id': product.id}), 201

@app.route('/products', methods=['GET'])
def get_products():
    offset = request.args.get('offset', 0, type=int)
    limit = request.args.get('limit', 10, type=int)
    products = Product.query.offset(offset).limit(limit).all()
    return jsonify([{'id': p.id, 'name': p.name, 'price': p.price, 'color': p.color} for p in products])

@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.json
    product = Product.query.get_or_404(product_id)
    product.name = data['name']
    product.price = data['price']
    product.color = data.get('color', product.color)
    db.session.commit()
    return jsonify({'message': 'Updated successfully'}), 200

@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Deleted successfully'}), 200

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'message': 'No file uploaded'}), 400
    file = request.files['file']
    if file.filename.endswith('.json'):
        file.save(os.path.join('uploads', file.filename))
        return jsonify({'message': 'File uploaded successfully'}), 201
    return jsonify({'message': 'Invalid file type'}), 400

@socketio.on('message')
def handle_message(data):
    emit('response', data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)
