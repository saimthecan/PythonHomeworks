from flask import Flask, request, jsonify
import jwt
import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
SECRET_KEY = 'your_secret_key'

# Bellekte veri tutma (örnek veri yapısı)
users = {}
data_store = {
    "data": "initial data"
}

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

@app.route('/protected', methods=['GET'])
@token_required
def protected(username):
    return jsonify({'message': f'Welcome {username}!'})

@app.route('/update', methods=['PUT'])
@token_required
def update_data(username):
    data = request.get_json()
    if 'data' in data:
        data_store['data'] = data['data']
        return jsonify({'message': 'Data has been updated!', 'user': username, 'data': data_store['data']})
    return jsonify({'message': 'No data provided!'}), 400

@app.route('/delete', methods=['DELETE'])
@token_required
def delete_data(username):
    data_store['data'] = ""
    return jsonify({'message': 'Data has been deleted!', 'user': username})

@app.route('/data', methods=['GET'])
@token_required
def get_data(username):
    return jsonify({'data': data_store['data'], 'user': username})

if __name__ == '__main__':
    app.run(debug=True)
