from flask import Flask, request, jsonify
import jwt
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)
SECRET_KEY = 'your_secret_key'

# MongoDB bağlantısı
client = MongoClient("mongodb+srv://canozgen:Sifreyok.11@cluster0.wgohfvg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["flask_db"]

users_collection = db["users"]
products_collection = db["products"]

# Bellekte veri tutma (örnek veri yapısı)
roles_permissions = {}


def load_permissions():
    global roles_permissions
    with open('roles_permissions.txt', 'r') as file:
        for line in file:
            user, *permissions = line.strip().split()
            roles_permissions[user] = permissions

load_permissions()

@app.route('/')
def home():
    return "Flask JWT Authentication Example"

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400

    username = data.get('username')
    password = data.get('password')

    user = users_collection.find_one({"username": username})
    if not user or not check_password_hash(user['password'], password):
        return jsonify({'message': 'Invalid credentials'}), 401

    token = create_token(username)
    return jsonify({'token': token})

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400

    username = data.get('username')
    password = data.get('password')

    if users_collection.find_one({"username": username}):
        return jsonify({'message': 'User already exists!'}), 400

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    users_collection.insert_one({"username": username, "password": hashed_password})
    return jsonify({'message': 'User created successfully!'}), 201

def create_token(username):
    payload = {
        'username': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['username']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization').split()[1]
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403
        try:
            username = verify_token(token)
            if not username:
                return jsonify({'message': 'Token is invalid or expired!'}), 403
        except Exception as e:
            return jsonify({'message': 'Token is invalid!'}), 403
        return f(username, *args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def check_permission(username, endpoint):
    user_permissions = roles_permissions.get(username, [])
    if endpoint not in user_permissions:
        return False
    return True

@app.route('/product', methods=['GET'])
@token_required
def get_product(username):
    if not check_permission(username, 'product'):
        return jsonify({'message': 'Permission denied!'}), 403
    product = products_collection.find_one({}, {"_id": 0})
    return jsonify({'product': product})

@app.route('/item', methods=['GET'])
@token_required
def get_item(username):
    if not check_permission(username, 'item'):
        return jsonify({'message': 'Permission denied!'}), 403
    item = products_collection.find_one({}, {"_id": 0})
    return jsonify({'item': item})

@app.route('/product', methods=['POST'])
@token_required
def add_product(username):
    if not check_permission(username, 'product'):
        return jsonify({'message': 'Permission denied!'}), 403
    data = request.get_json()
    products_collection.insert_one(data)
    return jsonify({'message': 'Product added successfully'})

@app.route('/item', methods=['POST'])
@token_required
def add_item(username):
    if not check_permission(username, 'item'):
        return jsonify({'message': 'Permission denied!'}), 403
    data = request.get_json()
    products_collection.insert_one(data)
    return jsonify({'message': 'Item added successfully'})

# Swagger Ayarları
SWAGGER_URL = '/docs'  # Swagger UI için URL
API_URL = '/static/swagger.json'  # Swagger dosyasının URL'si

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={  # Swagger UI yapılandırması
        'app_name': "Flask JWT Authentication Example"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

if __name__ == '__main__':
    app.run(debug=True)
