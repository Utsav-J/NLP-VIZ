from fastapi import FastAPI
from typing import List
import uvicorn
from models import TextInput, NLPAnalysisOut, TokenOut, EntityOut
from nlp_engine import analyze_text

app = FastAPI(title="NLP Analysis API", version="0.1.0")


@app.get("/")
def root():
    return {"message": "NLP Analysis API is running"}

    
@app.post("/analyze", response_model=NLPAnalysisOut)
def analyze(input_data: TextInput) -> NLPAnalysisOut:
    return analyze_text(input_data.text)


def main():
    # Simple CLI entry point to keep compatibility if run directly
    import sys
    text = " ".join(sys.argv[1:]) or "Apple is buying a startup in the U.K."
    result = analyze_text(text)
    # Pretty print JSON
    import json
    print(json.dumps(result.model_dump(), indent=2))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
