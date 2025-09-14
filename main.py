from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
api = Api(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

reqparser = reqparse.RequestParser()
reqparser.add_argument('name', type=str, help='Name of the item is required', required=True)
reqparser.add_argument('description', type=str, help='Description of the item')
reqparser.add_argument('item', type=str, help='Name of the item is required', required=True)
reqparser.add_argument('price', type=float, help='Price of the item', required=True)
reqparser.add_argument('quantity', type=int, help='Quantity of the item', required=True)
reqparser.add_argument('category', type=str, help='Category of the item')
reqparser.add_argument('date_added', type=str, help='Date of expense in YYYY-MM-DD format')


resource_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String,
    'item': fields.String,
    'price': fields.Float,
    'quantity': fields.Integer,
    'category': fields.String,
    'date_added': fields.String
}


@app.route("/")
def index():
    return render_template("index.html")

# ✅ Get all items
@app.route("/items", methods=["GET"])
def get_all_items():
    items = ItemModel.query.all()
    return jsonify([
        {
            'id': item.id,
            'name': item.name,
            'description': item.description,
            'price': item.price,
            'quantity': item.quantity,
            'category': item.category,
            'date_added': item.date_added
        }
        for item in items
    ])

# ✅ Chart data route
@app.route("/chart-data")
def chart_data():
    items = ItemModel.query.all()
    category_totals = {}
    for item in items:
        total_price = item.price * item.quantity
        category_totals[item.category] = category_totals.get(item.category, 0) + total_price

    labels = list(category_totals.keys())
    values = list(category_totals.values())
    return jsonify({"labels": labels, "values": values})


class ItemModel(db.Model):
    __tablename__ = "items" 

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    item = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date_added = db.Column(db.String(10), nullable=False)

    def __init__(self, name, description, item, price, quantity, category):
        self.name = name
        self.description = description
        self.item = item
        self.price = price
        self.quantity = quantity
        self.category = category
        self.date_added = date_added


    def __repr__(self):
        return f"Item(name={self.name}, price={self.price}, quantity={self.quantity})"


class Item(Resource):
    @marshal_with(resource_fields)
    def get(self, item_id):
        item = ItemModel.query.get(item_id)
        if not item:
            abort(404, message="Item not found")
        return marshal_with(resource_fields)(item)

    @marshal_with(resource_fields)
    def post(self, ):
        args = reqparser.parse_args()
        item = ItemModel( name=args['name'], description=args['description'], price=args['price'], quantity=args['quantity'])
        db.session.add(item)
        db.session.commit()
        return marshal_with(resource_fields)(item), 201
    
    @marshal_with(resource_fields)
    def put(self, item_id):
        args = reqparser.parse_args()
        item = ItemModel.query.get(item_id)
        if not item:
            abort(404, message="Item not found")
        item.name = args['name']
        item.description = args['description']
        item.price = args['price']
        item.quantity = args['quantity']
        db.session.commit()
        return (item)
    

    @marshal_with(resource_fields)
    def patch(self, item_id):
        item = ItemModel.query.get(item_id)
        if not item:
            abort(404, message="Item not found")
        args = reqparser.parse_args()
        if args['name']: item.name = args['name']
        if args['description']: item.description = args['description']
        if args['price']: item.price = args['price']
        if args['quantity']: item.quantity = args['quantity']
        db.session.commit()
        return item


    @marshal_with(resource_fields)
    def delete(self, item_id):
        item = ItemModel.query.get(item_id)
        if not item:
            abort(404, message="Item not found")
        db.session.delete(item)
        db.session.commit()
        return marshal_with(resource_fields)(item)

api.add_resource(Item, '/item/<int:item_id>')


if __name__ == '__main__':
    # with app.app_context():
    #     db.create_all()   # tables create ho jaayenge
    app.run(debug=True)    # phir server start karo

