# Social Support Eligibility System (AI-Powered Case Study)

This project demonstrates an **AI-powered eligibility screening system** for social support programs.  

It simulates how government or NGO caseworkers can process applicant documents, auto-extract key fields, validate data, run eligibility checks using ML, and provide explanations with an LLM chatbot.

## Features

- **Semi-Automated Data Validation**  
  Applicants upload documents → AI extracts info → pre-fills form → user validates/edits.

- **Document Processing**  
  Supports Bank Statements, Emirates ID, Resumes, Credit Reports, and Assets/Liabilities Excel sheets.

- **ML-Based Eligibility**  
  Uses a trained **scikit-learn pipeline** (saved as `models/eligibility_v1.joblib`) to predict eligibility.

- **Explainable Decisions**  
  Uses **Gemini 2.0 Flash** to explain decisions in plain language and answer applicant queries.

- **Persistent Records**  
  Each `/predict` response is stored in `data/saved_applicants/` for future lookup and chatbot queries.

- **Chatbot Interface**  
  Applicants can ask follow-up questions referencing their `app_id`.

---

## Project Structure

```
.
├── app/                      # Streamlit frontend
│   └── app.py
├── backend/                  # FastAPI backend
│   ├── agents.py             # DataExtraction, Validation, Eligibility, Explanation agents
|   ├── orchestrator.py
│   └── main.py               # API endpoints (/extract, /predict, /explain)
├── scripts/                  # Utility scripts
│   ├── preprocess_raw_data.py
│   └── train_eligibility_model.py
├── data/
│   ├── raw/                  # Uploaded applicant documents
│   ├── processed/            # Cleaned data (JSON/CSV)
│   └── saved_applications/           # saved predictions
├── models/
│   └── eligibility_v1.joblib # Trained scikit-learn pipeline
├──data_creation.py         # Sample data creation
├── requirements.txt
└── README.md
```

## Installation

1. **Clone repository**  
   ```bash
   git clone https://github.com/ashishagarwal02042001/ai_case_study.git
   ```

2. **Create virtual environment**  
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
   ```

3. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

   Key dependencies:
   - `fastapi`
   - `uvicorn`
   - `streamlit`
   - `pandas`, `numpy`, `scikit-learn`
   - `pdfplumber`, `pillow`, `pytesseract` (for OCR)
   - `google-generativeai` (Gemini API)

4. **Environment variables**  
   Create a `.env` file:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=your_selected_gemini_model
   ```

## Running the Project

### Preprocess Raw Data
Generate structured CSV/JSON from applicant documents:
```bash
python scripts/preprocess_raw_data.py
```

### Train Eligibility Model
```bash
python scripts/train_eligibility_model.py
```
This creates `models/eligibility_v1.joblib`.

### Start Backend (FastAPI)
```bash
uvicorn backend.main:app --reload --port 8000
```
API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### Start Frontend (Streamlit)
```bash
streamlit run app/app.py
```
Frontend: [http://localhost:8501](http://localhost:8501)

## Workflow Demo

1. **Upload Documents**  
   Applicant uploads Bank Statement, Emirates ID, Resume, Credit Report, Assets/Liabilities.

2. **Auto-Extract Fields**  
   Backend parses docs → returns pre-filled form in frontend.

3. **Review & Submit**  
   Applicant validates/edits fields and submits.

4. **Eligibility Check**  
   ML model + validation rules return decision + confidence.

5. **Save Response**  
   Decision is saved as JSON under `data/processed/app_xxxx.json`.

6. **Chatbot Queries**  
   Applicant enters `app_id` and asks questions → Gemini answers with context from saved JSON.

## Example Output

### `/predict` response
```json
{
  "app_id": "app_a1b2c3d4",
  "decision": "reject",
  "confidence": 0.85,
  "reasons": ["income_above_threshold"],
  "recommendations": [],
  "explanation": "Your reported income exceeds the program threshold."
}
```

Saved as `data/saved_applications/app_a1b2c3d4.json`.

### `/explain` response
> *"Your application was rejected because your income is higher than the eligibility threshold. You may reapply if your circumstances change."*

## Known Limitations

- OCR quality depends on Tesseract installation.  
- Eligibility logic is based on a simple ML model (can be improved with richer training data).  
- Currently only JSON persistence — embedding/semantic search can be added for large-scale retrieval.  

## Next Steps

- Add **embedding storage** (ChromaDB / FAISS) for semantic Q&A across multiple applicants.  
- Improve **data extraction** with advanced OCR/NLP pipelines.  
- Extend **Admin Dashboard** to review all processed applications.  
- Deploy backend (FastAPI) + frontend (Streamlit) on cloud (e.g., GCP, AWS, Render).  

## Authors

- Developed by **Ashish Agarwal** as part of an **AI Case Study**  
- Powered by **FastAPI, Streamlit, Scikit-Learn, and Gemini 2.0 Flash**
