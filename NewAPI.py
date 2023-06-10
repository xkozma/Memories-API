from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from io import BytesIO

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

# Image model
class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    data = db.Column(db.LargeBinary, nullable=False)
    lat = db.Column(db.Double(100))
    lon = db.Column(db.Double(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, name, description, data,lat,lon, user_id):
        self.name = name
        self.description = description
        self.data = data
        self.lat = lat
        self.lon = lon
        self.user_id = user_id

# API endpoints
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = data['password']

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists'})

    user = User(username, password)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']

    user = User.query.filter_by(username=username, password=password).first()

    if user:
        return jsonify({'message': 'Login successful','logged_id':user.id})
    else:
        return jsonify({'message': 'Invalid credentials'})

@app.route('/upload', methods=['POST'])
def upload():
    name = request.form.get('name')
    description = request.form.get('description')
    file = request.files.get('data')
    lat = request.form.get('lat')
    lon = request.form.get('lon')
    user_id = request.form.get('user_id')

    if not all([name, description, file,lat,lon, user_id]):
        return jsonify({'message': 'Invalid request'})

    file_data = file.read()
    file_data_bytes = bytearray(file_data)

    image = Image(name, description, file_data_bytes,lat,lon, user_id)
    db.session.add(image)
    db.session.commit()

    return jsonify({'message': 'Image uploaded successfully'})

@app.route('/images', methods=['GET'])
def get_images():
    user_id = request.form.get('user_id')

    images = Image.query.filter_by(user_id=user_id).all()

    image_list = []
    for image in images:
        image_data = {
            'name': image.name,
            'description': image.description,
            'lat': image.lat,
            'lon': image.lon,
            'image_url': f"/images/{image.id}"  # Provide a URL or reference to the image file
        }
        image_list.append(image_data)

    return jsonify({'images': image_list})

@app.route('/images/<int:image_id>', methods=['GET'])
def get_image(image_id):
    image = Image.query.get(image_id)

    if not image:
        return jsonify({'message': 'Image not found'})

    return send_file(BytesIO(image.data), mimetype='image/jpeg')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)