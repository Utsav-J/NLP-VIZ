from fastapi import FastAPI, HTTPException
from typing import Dict
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from models import TextInput, NLPAnalysisOut, TranslationInput, TranslationOut, POSAnalysisOut, NERAnalysisOut
from nlp_engine import analyze_text, analyze_pos, analyze_ner
from translation_engine import translate_text, get_supported_languages

app = FastAPI(title="NLP Analysis API", version="0.1.0")
app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
)
@app.get("/")
def root():
    return {"message": "NLP Analysis API is running"}

@app.post("/analyze", response_model=NLPAnalysisOut)
def analyze(input_data: TextInput) -> NLPAnalysisOut:
    """Analyze text for both POS tagging and NER (combined endpoint - kept for backward compatibility)"""
    return analyze_text(input_data.text)


@app.post("/pos", response_model=POSAnalysisOut)
def pos_tagging(input_data: TextInput) -> POSAnalysisOut:
    """Analyze text for POS tagging only using TRF model"""
    return analyze_pos(input_data.text)


@app.post("/ner", response_model=NERAnalysisOut)
def named_entity_recognition(input_data: TextInput) -> NERAnalysisOut:
    """Analyze text for Named Entity Recognition only using small model"""
    return analyze_ner(input_data.text)


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
