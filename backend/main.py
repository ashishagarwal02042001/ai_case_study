from fastapi import FastAPI, UploadFile, File, Form, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
import uvicorn
import uuid
import shutil
import os
import json
from backend.orchestrator import Orchestrator
from backend.agents import DataExtractionAgent

app = FastAPI(title = "Social Support Interface API")
app.add_middleware(
    CORSMiddleware,
    allow_origins = ['*'],
    allow_credentials = True,
    allow_methods = ['*'],
    allow_headers = ['*'],
    )

router = APIRouter()
extractor = DataExtractionAgent()

os.makedirs('data/raw', exist_ok=True)
path = Path("data/saved_applications")
path.mkdir(parents=True,exist_ok=True)

orchestrator = Orchestrator()
class PredictResponse(BaseModel):
    app_id: Optional[str] = None
    decision: str
    score: float
    reasons: List[str]
    recommendations: List[str]
    explanation: str

@app.get('/health')
async def health():
    return {'status':'ok'}

@app.post('/predict',response_model=PredictResponse)
async def predict(
    name:str = Form(...),
    dob:str = Form(...),
    address:str = Form(...),
    family_size:int = Form(...),
    income:float = Form(...),
    files:Optional[List[UploadFile]]=File(None),):
    
    app_id = f'app_{uuid.uuid4().hex[:8]}'
    app_dir = os.path.join('data/raw', app_id)
    os.makedirs(app_dir, exist_ok=True)
    saved_files = []
    if files:
        for f in files:
            file_path = os.path.join(app_dir, f.filename)
            with open(file_path,'wb') as out:
                shutil.copyfileobj(f.file, out)
            saved_files.append(file_path)
    application = {
        'app_id':app_id,
        'name':name,
        'dob':dob,
        'address':address,
        'family_size':family_size,
        'reported_income':income,
        'files':saved_files,
    }

    try:
        result = orchestrator.process_application(application)
        with open(path/f"{app_id}.json","w") as f:
            json.dump(result, f , indent=2)
        print(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return PredictResponse(**result)

@app.post('/explain')
async def explain(query:dict):
    q = query.get('query')
    app_id = query.get('app_id')
    if not q:
        raise HTTPException(status_code=400, detail="Missing query in request body")
    answer = orchestrator.explain_query(q, app_id=app_id)
    return {'answer':answer}

@app.post('/extract')
async def extract_fields(files: list[UploadFile] = File(...)):
    file_paths = []
    for f in files:
        save_path = f'data/uploads/{f.filename}'
        with open(save_path, 'wb') as buffer:
            buffer.write(await f.read())
        file_paths.append(save_path)
    parsed_docs = extractor.extract({'files':file_paths})

    fields = {
        "name": parsed_docs['app_form'].get("name"),
        "dob": parsed_docs['app_form'].get("dob"),
        "address": parsed_docs['app_form'].get("address"),
        "family_size": parsed_docs['app_form'].get("family_size"),
        "reported_income": parsed_docs['app_form'].get("reported_income"),
    }
    # print(fields)

    return {"fields":fields, "documents":parsed_docs["documents"]}

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)