import json
import logging
import os
from fastapi import FastAPI, Request, HTTPException, status
from typing import Dict, Any
import firebase_admin
from firebase_admin import credentials, firestore

# Global variables for Firebase configuration, provided by the environment
__app_id = os.environ.get('appId')
__firebase_config = os.environ.get('firebaseConfig')

# Configure basic logging to see incoming data in the console
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Firebase app using credentials from the environment
def initialize_firebase():
    """Initializes the Firebase app if it hasn't been already."""
    try:
        if not firebase_admin._apps:
            logging.info("Initializing Firebase Admin SDK...")
            cred = credentials.Certificate(json.loads(__firebase_config))
            firebase_admin.initialize_app(cred)
            logging.info("Firebase Admin SDK initialized successfully.")
        return firestore.client()
    except Exception as e:
        logging.error(f"Failed to initialize Firebase: {e}")
        return None

db = initialize_firebase()

# A simple check to ensure the Firestore client is ready
if not db:
    raise RuntimeError("Firestore database client could not be initialized. Cannot continue.")

app = FastAPI(
    title="Africa's Talking Webhook Service",
    description="A service to receive and store SMS delivery reports in Firestore."
)

@app.post("/delivery-report", status_code=status.HTTP_200_OK)
async def handle_delivery_report(request: Request):
    """
    This function handles the incoming delivery report webhook from Africa's Talking.
    It processes the data and stores it in Firestore.
    """
    try:
        data = await request.json()
    except json.JSONDecodeError:
        try:
            # Fallback for form data if content-type is not application/json
            data = await request.form()
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid data received")

    logging.info("Received delivery report:")
    logging.info(json.dumps(data, indent=2))

    # Extract key information from the delivery report
    message_id = data.get('id')
    status_msg = data.get('status')
    phone_number = data.get('phoneNumber')
    
    if not message_id or not status_msg:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing required fields 'id' or 'status'")

    # Create a document to store in Firestore
    report_doc = {
        'message_id': message_id,
        'phone_number': phone_number,
        'status': status_msg,
        'timestamp': firestore.SERVER_TIMESTAMP
    }

    # Store the delivery report in a Firestore collection
    collection_path = f"artifacts/{__app_id}/public/data/delivery_reports"
    doc_ref = db.collection(collection_path).document(message_id)
    doc_ref.set(report_doc)
    
    logging.info(f"Successfully stored delivery report for message_id: {message_id}")
    
    return {"message": "Delivery report received and stored successfully"}

@app.get("/api/v1/sms/status/{message_id}", status_code=status.HTTP_200_OK)
def get_message_status(message_id: str):
    """
    Check the delivery status of a message from the Firestore database.
    """
    try:
        # Retrieve the document from the Firestore collection
        collection_path = f"artifacts/{__app_id}/public/data/delivery_reports"
        doc_ref = db.collection(collection_path).document(message_id)
        doc = doc_ref.get()

        if doc.exists:
            status_data = doc.to_dict()
            return {
                "message_id": message_id,
                "status": status_data.get('status'),
                "phone_number": status_data.get('phone_number'),
                "timestamp": status_data.get('timestamp').isoformat() if status_data.get('timestamp') else None
            }
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No delivery report found for message ID: {message_id}")

    except Exception as e:
        logging.error(f"Error retrieving message status: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
