from __future__ import annotations
import asyncio
from typing import Optional

from googletrans import Translator, LANGUAGES

from models import TranslationOut


def get_supported_languages() -> dict[str, str]:
    """Get dictionary of supported language codes and names"""
    return LANGUAGES


def translate_text(text: str, target_language: str) -> TranslationOut:
    """
    Translate text to target language using Google Translate
    
    Args:
        text: Text to translate
        target_language: Target language code (e.g., 'es', 'fr', 'de')
    
    Returns:
        TranslationOut with translation results
    """
    if not text.strip():
        raise ValueError("Text cannot be empty")
    
    # Validate target language
    
    supported_langs = get_supported_languages()
    if target_language not in supported_langs:
        raise ValueError(f"Unsupported language code: {target_language}")
    
    try:
        translator = Translator()
        result = asyncio.run(translator.translate(text, dest=target_language))
        print(result)
        return TranslationOut(
            original_text=text,
            source_language=str(result.src),
            translated_text=str(result.text),
            target_language=str(result.dest),
            confidence=getattr(result, 'confidence', 0.0) or 0.0
        )
    except Exception as e:
        raise RuntimeError(f"Translation failed: {str(e)}") from e
