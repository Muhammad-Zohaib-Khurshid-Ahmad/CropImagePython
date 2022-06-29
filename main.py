from fastapi import FastAPI, File, UploadFile
import cv2
import numpy as np
import base64
import datetime
import os

app = FastAPI()

def trim(frame):
    if not np.sum(frame[0]):
        return trim(frame[1:])
    elif not np.sum(frame[-1]):
        return trim(frame[:-2])
    elif not np.sum(frame[:,0]):
        return trim(frame[:,1:]) 
    elif not np.sum(frame[:,-1]):
        return trim(frame[:,:-2])    
    return frame

@app.get("/")
def read_root():
    return "Welcome"

@app.post("/cropBlackEdges")
async def upload(file: UploadFile = File(...)):
    try:
        file_name = str(datetime.datetime.now()).replace(" ", "").replace(".", "").replace(":", "").replace("-", "")+'.'+str(file.filename).partition('.')[1:][1]
        file_location = f"images/{file_name}"
        with open(file_location, 'wb') as f:
            f.write(await file.read())
    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        await file.close()
        img = cv2.imread(file_location)   
        thold = (img>120)*img
        trimmedImage = trim(thold)
        cv2.imwrite(file_location,trimmedImage)
        encoded = base64.b64encode(open(file_location, "rb").read())
        imageURI = 'data:image/png;base64,'+str(encoded)[2:][:-1]
        os.remove(file_location)
        return {
            'statusCode': 200,
            "message": "Image Cropped Successfuly",
            'successData': {'imageURI':imageURI}
           }

