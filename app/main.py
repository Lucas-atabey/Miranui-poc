import os
import traceback
import boto3
from flask import Flask, request, jsonify
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from flask_cors import CORS


load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

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
    return jsonify({"message": "Hello world"}), 200

@app.route("/list", methods=["GET"])
def list_buckets():
    response = s3_client.list_buckets()
    result = ""
    for bucket in response['Buckets']:
        print(bucket['Name'])
        result = bucket['Name']
    return jsonify({"message": f"{result} is a bucket"}), 200

@app.route("/upload", methods=["OPTIONS"])
def options_upload():
    print("oui")
    return 'Oui', 200

@app.route("/upload", methods=["POST"])
def upload():
    print("Upload route called 1")
    try:
        print("Upload route called 2")
        if "file" not in request.files:
            print("Upload route called 3")
            return jsonify({"error": "No file part"}), 400

        print("Upload route called 4")
        file = request.files["file"]
        print("Upload route called 5")
        filename = secure_filename(file.filename)

        s3_client.upload_fileobj(file, BUCKET, filename)
        print("Upload route called 6")
        return jsonify({"message": f"{filename} uploaded"}), 200
    except ClientError as e:
        # Erreur liée à boto3
        print(f"ClientError: {e}")
        return jsonify({"error": f"ClientError: {str(e)}"}), 500
    except Exception as e:
        # Attrape toute autre erreur pour mieux diagnostiquer
        tb = traceback.format_exc()
        print(f"Unexpected error during upload:\n{tb}")
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

@app.route("/download/<filename>", methods=["GET"])
def download(filename):
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET, 'Key': filename},
            ExpiresIn=3600
        )
        return jsonify({"url": url}), 200
    except ClientError as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
