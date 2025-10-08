from fastapi import FastAPI, HTTPException
from typing import List, Dict
import uvicorn
from models import TextInput, NLPAnalysisOut, TokenOut, EntityOut, TranslationInput, TranslationOut
from nlp_engine import analyze_text
from translation_engine import translate_text, get_supported_languages

app = FastAPI(title="NLP Analysis API", version="0.1.0")

@app.get("/")
def root():
    return {"message": "NLP Analysis API is running"}

@app.post("/analyze", response_model=NLPAnalysisOut)
def analyze(input_data: TextInput) -> NLPAnalysisOut:
    return analyze_text(input_data.text)


@app.post("/translate", response_model=TranslationOut)
def translate(input_data: TranslationInput) -> TranslationOut:
    try:
        return translate_text(input_data.text, input_data.target_language)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/languages", response_model=Dict[str, str])
def get_languages() -> Dict[str, str]:
    """Get list of supported translation languages"""
    return get_supported_languages()


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
