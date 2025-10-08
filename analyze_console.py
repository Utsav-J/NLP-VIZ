import argparse
import json
import sys
import os
sys.path.append(os.path.dirname(__file__))
from nlp_engine import analyze_text


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze text with spaCy (POS & NER)")
    parser.add_argument("text", nargs="+", help="Text to analyze")
    args = parser.parse_args()
    text = " ".join(args.text)

    result = analyze_text(text)
    print(json.dumps(result.model_dump(), indent=2))


if __name__ == "__main__":
    main()


