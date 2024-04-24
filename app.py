from flask import Flask, render_template, jsonify
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Retrieve the connection string from an environment variable
AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sas_token')
def generate_sas_token():
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    container_name = 'thelegaltruthdb'
    blob_name = 'thelegaltruth-cont' 
    sas_token = generate_blob_sas(
        account_name=blob_service_client.account_name,
        container_name=container_name,
        blob_name=blob_name,
        account_key=blob_service_client.credential.account_key,
        permission=BlobSasPermissions(write=True),
        expiry=datetime.utcnow() + timedelta(hours=1)  # Token valid for 1 hour
    )
    return jsonify({'sas_token': sas_token, 'blob_name': blob_name})

if __name__ == '__main__':
    app.run(debug=True)