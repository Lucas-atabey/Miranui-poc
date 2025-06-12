import os
import boto3
import urllib.parse 
from datetime import timedelta

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask import Flask, request, jsonify
from flask_cors import CORS

from botocore.exceptions import ClientError
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


username = urllib.parse.quote_plus(os.getenv("DB_USERNAME", ""))
dbpassword = urllib.parse.quote_plus(os.getenv("DB_PASSWORD", ""))
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT", 3306)
database = os.getenv("DB_NAME")

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{username}:{dbpassword}@{host}:{port}/{database}"
app.config['SECRET_KEY'] = 'supersecret'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(256), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

with app.app_context():
    db.create_all()

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    if not data or not data.get("username") or not data.get("password"):
        return jsonify({"msg": "Username et mot de passe requis"}), 400
    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"msg": "Utilisateur déjà existant"}), 400
    hashed_pw = generate_password_hash(data["password"])
    user = User(username=data["username"], password=hashed_pw)
    db.session.add(user)
    db.session.commit()
    access_token = create_access_token(identity=str(user.id))
    return jsonify(access_token=access_token)

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    if not data or not data.get("username") or not data.get("password"):
        return jsonify({"msg": "Username et mot de passe requis"}), 400
    user = User.query.filter_by(username=data["username"]).first()
    if not user or not check_password_hash(user.password, data["password"]):
        return jsonify({"msg": "Identifiants invalides"}), 401
    access_token = create_access_token(identity=str(user.id))
    return jsonify(access_token=access_token)

s3_client = boto3.client(
    's3',
    endpoint_url=os.getenv("S3_ENDPOINT"),
    aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("S3_SECRET_KEY"),
    region_name="us-east-1",  # Ionos supporte généralement 'us-east-1'
)

BUCKET = os.getenv("S3_BUCKET")

@app.route("/", methods=["GET"])
def hello_word():
    result = [os.getenv("S3_BUCKET"), os.getenv("S3_ENDPOINT"), os.getenv("S3_ACCESS_KEY"), os.getenv("S3_SECRET_KEY")]
    print(result)
    return jsonify({"message": f"test os envs: {str(result)}"}), 200

@app.route("/list", methods=["GET"])
def list_buckets():
    response = s3_client.list_buckets()
    result = []
    for bucket in response['Buckets']:
        print(bucket['Name'])
        result.append(bucket['Name'])
    return jsonify({"message": f"{str(result)} is a bucket"}), 200

@app.route("/upload", methods=["POST"])
@jwt_required()
def upload():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"msg": "Utilisateur non trouvé"}), 404

    username = user.username
    print(user_id)
    if "file" not in request.files:
        return jsonify({"msg": "Fichier manquant"}), 400
    file = request.files["file"]
    filename = secure_filename(file.filename)
    key = f"{username}/{filename}"
    print(file)
    print(filename)
    # Upload dans S3
    print(f"user_id (type {type(user_id)}):", user_id)
    # S'assurer que user_id est une string
    if not isinstance(user_id, str):
        user_id = str(user_id)

    try:
        s3_client.upload_fileobj(file, BUCKET, key)
    except ClientError as e:
        return jsonify({"error": str(e)}), 500
    # Sauvegarde en base
    file_db = File(filename=filename, user_id=user_id)
    db.session.add(file_db)
    db.session.commit()
    return jsonify({"msg": f"{filename} uploadé"}), 200

@app.route("/files", methods=["GET"])
@jwt_required()
def list_files():
    user_id = get_jwt_identity()
    user_files = File.query.filter_by(user_id=user_id).all()
    # Retourne juste les noms (ou d'autres métadonnées si besoin)
    results = [{"filename": f.filename} for f in user_files]
    return jsonify(files=results)

@app.route("/download/<filename>", methods=["GET"])
@jwt_required()
def download(filename):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "Utilisateur non trouvé"}), 404

    username = user.username
    # Vérifier que le fichier appartient bien à l'utilisateur
    file = File.query.filter_by(user_id=user_id, filename=filename).first()
    if not file:
        return jsonify({"msg": "Fichier non trouvé ou accès refusé"}), 404
    key = f"{username}/{filename}"
    try:
        url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": BUCKET, "Key": key},
            ExpiresIn=3600,
        )
    except ClientError as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({"url": url})

if __name__ == "__main__":
    # créer la DB si elle n'existe pas
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)
