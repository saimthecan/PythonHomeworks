from flask import Flask, request, jsonify
import jwt
import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
SECRET_KEY = 'your_secret_key'

# Bellekte veri tutma (örnek veri yapısı)
users = {}
roles_permissions = {}
data_store = {
    "product": "initial product data",
    "item": "initial item data"
}

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

    if username not in users or not check_password_hash(users[username], password):
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

    if username in users:
        return jsonify({'message': 'User already exists!'}), 400

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    users[username] = hashed_password
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
    return jsonify({'product': data_store['product']})

@app.route('/item', methods=['GET'])
@token_required
def get_item(username):
    if not check_permission(username, 'item'):
        return jsonify({'message': 'Permission denied!'}), 403
    return jsonify({'item': data_store['item']})

if __name__ == '__main__':
    app.run(debug=True)
