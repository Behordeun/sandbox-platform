import os
import json
import logging
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import requests
import firebase_admin
from firebase_admin import credentials, firestore

# --- Configure Logging ---

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from the .env file
load_dotenv()

# --- Africa's Talking SDK Configuration ---
import africastalking

username = os.getenv("AT_USERNAME")
api_key = os.getenv("AT_API_KEY")
sender_id = os.getenv("AT_SENDER_ID")
webhook_url = os.getenv("WEBHOOK_URL")
print(webhook_url)
#print(username)
#print(api_key)
#print(sender_id)
# --- Firebase Admin SDK Configuration ---
__app_id = os.getenv('appId')
with open("firebase_service_acct.json", "r") as f:
    service_account_info = json.load(f)

if not all([username, api_key, sender_id]):
    raise EnvironmentError("AT_USERNAME, AT_API_KEY, and AT_SENDER_ID must be set in the .env file.")
if not __app_id:
    raise RuntimeError("The 'appID' environment variable is not set. Please add it to your .env file.")
'''if not __firebase_config_str:
    raise RuntimeError("The 'firebaseConfig' environment variable is not set. Please add the complete single-line JSON to your .env file.")
    '''

if not all([username, api_key, sender_id]):
    raise EnvironmentError("AT_USERNAME, AT_API_KEY, and AT_SENDER_ID must be set in the .env file.")


try:
    africastalking.initialize(username, api_key)
    sms_service = africastalking.SMS
    application_service = africastalking.Application
except Exception as e:
    logging.error(f"Failed to initialize Africa's Talking SDK: {e}")
    raise RuntimeError(f"Africa's Talking SDK could not be initialized. Error: {e}")

'''
def initialize_firebase():
    """Initializes the Firebase app if it hasn't been already."""
    try:
        if not firebase_admin._apps:
            logging.info("Initializing Firebase Admin SDK...")
            cred = credentials.Certificate(json.loads(__firebase_config_str))
            firebase_admin.initialize_app(cred)
            logging.info("Firebase Admin SDK initialized successfully.")
        return firestore.client()
    except Exception as e:
        logging.error(f"Failed to initialize Firebase: {e}")
        return None
'''
def initialize_firebase():
    """Initializes the Firebase app if it hasn't been already."""
    try:
        if not firebase_admin._apps:
            logging.info("Initializing Firebase Admin SDK...")
            # Use the service account info dict directly
            cred = credentials.Certificate(service_account_info)
            firebase_admin.initialize_app(cred)
            logging.info("Firebase Admin SDK initialized successfully.")
        return firestore.client()
    except Exception as e:
        logging.error(f"Failed to initialize Firebase: {e}")
        return None

db = initialize_firebase()

if not db:
    raise RuntimeError("Firestore database client could not be initialized. Cannot continue.")

# --- FastAPI App Setup ---
app = FastAPI(
    title="DPI/AI SMS Messaging and Webhook Service",
    description="A unified service for sending and receiving SMS messages and handling delivery reports."
)

# --- Pydantic Models for request body validation ---
class SendSMSRequest(BaseModel):
    to: str = Field(..., description="The phone number to send the SMS to. Must be in international format (e.g., +23480xxxxxxxx).")
    message: str = Field(..., description="The content of the SMS message.")

class SendBulkSMSRequest(BaseModel):
    to: List[str] = Field(..., description="A list of phone numbers to send the SMS to. Must be in international format.")
    message: str = Field(..., description="The content of the SMS message.")

# --- API Endpoints ---
@app.get("/health", status_code=status.HTTP_200_OK, tags=["Health"])
async def health_check():
    """
    Check the health of the SMS service by pinging the Africa's Talking API.
    """
    base_url = "https://api.africastalking.com/version1"
    url = f"{base_url}/messaging"
    
    headers = {
        "Accept": "application/json",
        "apiKey": api_key,
    }
    
    params = {
        "username": username,
    }

    try:
        response = await asyncio.to_thread(
            requests.get, url, headers=headers, params=params, timeout=10
        )
        
        if response.status_code == 200:
            return {"status": "healthy", "service": "Africa's Talking SMS API is up and reachable."}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"API responded with status code: {response.status_code}. Response body: {response.text}"
            )
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Request to Africa's Talking API failed: {e}"
        )

@app.post("/api/v1/sms/send", status_code=status.HTTP_200_OK, tags=["SMS"])
async def send_single_sms(request_body: SendSMSRequest):
    """
    Send a single SMS message.
    """
    try:
        response = await asyncio.to_thread(sms_service.send, request_body.message, [request_body.to])# senderId=sender_id)
        if "SMSMessageData" not in response or not response["SMSMessageData"]["Recipients"]:
            raise ValueError(response.get("errorMessage", "Unknown API error"))

        return {"status": "success", "message_id": response["SMSMessageData"]["Recipients"][0]["messageId"], "response": response}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Africa's Talking API Error: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {e}"
        )

@app.post("/api/v1/sms/send-bulk", status_code=status.HTTP_200_OK, tags=["SMS"])
async def send_bulk_sms(request_body: SendBulkSMSRequest):
    """
    Send a bulk SMS message.
    """
    if not request_body.to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The 'to' field cannot be an empty list."
        )

    try:
        response = await asyncio.to_thread(sms_service.send, request_body.message, request_body.to)#, senderId=sender_id)
        return {"status": "success", "response": response}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Africa's Talking API Error: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {e}"
        )

@app.get("/api/v1/sms/balance", status_code=status.HTTP_200_OK, tags=["Application"])
async def check_balance():
    """
    Check the current SMS balance on your account.
    """
    try:
        user_info = await asyncio.to_thread(application_service.fetch_application_data)
        balance = user_info["UserData"]["balance"]
        return {"status": "success", "balance": balance}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Africa's Talking API Error: {e}"
        )

@app.post("/delivery-report", status_code=status.HTTP_200_OK, tags=["Webhook"])
async def handle_delivery_report(request: Request):
    """
    Handles the incoming delivery report webhook from Africa's Talking.
    It processes the data and stores it in Firestore.
    """
    try:
        data = await request.json()
    except json.JSONDecodeError:
        try:
            data = await request.form()
            data = dict(data)
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid data received")

    logging.info("Received delivery report:")
    logging.info(json.dumps(data, indent=2))

    message_id = data.get('id')
    status_msg = data.get('status')
    phone_number = data.get('phoneNumber')
    
    if not message_id or not status_msg:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing required fields 'id' or 'status'")

    report_doc = {
        'message_id': message_id,
        'phone_number': phone_number,
        'status': status_msg,
        'timestamp': firestore.SERVER_TIMESTAMP
    }

    collection_path = f"artifacts/{__app_id}/public/data/delivery_reports"
    doc_ref = db.collection(collection_path).document(message_id)
    await asyncio.to_thread(doc_ref.set, report_doc)
    
    logging.info(f"Successfully stored delivery report for message_id: {message_id}")
    
    return {"message": "Delivery report received and stored successfully"}

@app.get("/api/v1/sms/status/{message_id}", status_code=status.HTTP_200_OK, tags=["SMS"])
async def get_message_status(message_id: str):
    """
    Check the delivery status of a message from the Firestore database.
    """
    try:
        collection_path = f"artifacts/{__app_id}/public/data/delivery_reports"
        doc_ref = db.collection(collection_path).document(message_id)
        doc = await asyncio.to_thread(doc_ref.get)

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
