import datetime
import time
import jwt

from io import BytesIO
from backend.g_drive_service import GoogleDriveService
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, status
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from googleapiclient.http import MediaIoBaseUpload
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


import os
from typing import List  

app = FastAPI()
security = HTTPBearer()

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can specify the exact origins instead of "*" for security
    #allow_credentials=True,
    allow_methods=["*"],  # You can specify the allowed methods (e.g., "GET", "POST")
    allow_headers=["*"],  # You can specify the allowed headers
)

service=GoogleDriveService().build()

ROOT_FOLDER_ID = f'{os.getenv("FOLDER_ID")}'

def get_key():
    file_path = "./secret.key"  # Path to the file on the server
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return file.read()  # Read the content and remove any trailing newline characters
    raise FileNotFoundError("Secret key file not found.")

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    SECRET_KEY = get_key()
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        print("Token has expired")  # Log expiration
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        print(f"Invalid token: {str(e)}")  # Log invalid token details
        raise HTTPException(status_code=401, detail="Invalid token")


@app.post("/upload")
async def upload_photos(
    files: List[UploadFile] = File(...),
    token: dict = Depends(verify_token)
):
    time.sleep(10)
    # Extract user_id from the token payload
    user_id = token.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID nije pronadjen!")
    
    # Parse the user_id (which is in "dd.mm.yyyy" format) to a date object
    try:
        user_date = datetime.datetime.strptime(user_id, "%d.%m.%Y").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Datum nije validan!")

    # Get the current date
    current_date = datetime.datetime.now().date()
    

    # Compare the parsed date with the current date
    if current_date != user_date:
        raise HTTPException(status_code=400, detail="Dalje neces moci!")
    else:
        for file in files:
            # Read file content
            file_content = await file.read()
            
            buffer_memory = BytesIO(file_content)

            mime = file.content_type
            media_body=MediaIoBaseUpload(buffer_memory, mimetype=mime, resumable=True)

            created_at= datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            file_metadata={
                    "name":f"{file.filename} ({created_at})",
                    "parents": [ROOT_FOLDER_ID]
                }
            returned_fields="id, name, mimeType, webViewLink, exportLinks"

            upload_response=service.files().create(
                    body = file_metadata, 
                    media_body=media_body,  
                    fields=returned_fields
                ).execute()

        return JSONResponse(content={"detail": "Uspeh!"})
    

@app.get('/gdrive-files')
def getFileListFromGDrive():
    selected_fields="files(id,name,webViewLink)"
    g_drive_service=GoogleDriveService().build()
    list_file=g_drive_service.files().list(fields=selected_fields).execute()
    return {"files":list_file.get("files")}

@app.get("/")
def read_root():
    return {"message": "Welcome to the Photo Upload API"}
