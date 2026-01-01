"""
Hybrid NLP–LLM Extraction Pipeline
---------------------------------

Reference implementation for the MSc thesis:
"Bug-Report–Driven Automated Test Generation Using Hybrid NLP and Large Language Models"

Pipeline stages:
1. Regex-based literal extraction
2. NLP-based candidate extraction
3. LLM-based refinement using Tree-of-Thought prompting

Output:
- Structured JSONL file with ranked test inputs
"""

import os
import re
import json
import pandas as pd
from typing import List, Dict, Any

import spacy
from openai import OpenAI

# -----------------------------
# Configuration
# -----------------------------

INPUT_CSV = "data/sample_bug_reports.csv"
OUTPUT_JSONL = "extracted_test_inputs.jsonl"
OPENAI_MODEL = "gpt-4.1"

client = OpenAI()  # API key read from OPENAI_API_KEY


# -----------------------------
# Stage 1: Regex Literal Extraction
# -----------------------------

LITERAL_PATTERNS = {
    "string": r'"([^"]+)"|\'([^\']+)\'',
    "number": r'\b\d+(\.\d+)?\b',
    "exception": r'\b[A-Za-z0-9_]*Exception\b',
    "http_status": r'\bHTTP\s*\d{3}\b',
    "path": r'(/[A-Za-z0-9_\-./]+)|([A-Za-z]:\\[A-Za-z0-9_\-\\.\\]+)',
}


def extract_literals(text: str) -> List[Dict[str, Any]]:
    results = []
    for kind, pattern in LITERAL_PATTERNS.items():
        for match in re.finditer(pattern, text):
            value = next((g for g in match.groups() if g), match.group(0))
            results.append({
                "value": value,
                "kind": kind,
                "source": "regex"
            })
    return results


# -----------------------------
# Stage 2: NLP Extraction
# -----------------------------

def load_nlp():
    return spacy.load("en_core_web_sm")


def extract_nlp_candidates(text: str, nlp) -> List[Dict[str, Any]]:
    doc = nlp(text)
    results = []

    for ent in doc.ents:
        results.append({
            "value": ent.text,
            "kind": f"entity_{ent.label_}",
            "source": "nlp"
        })

    for sent in doc.sents:
        for token in sent:
            if token.pos_ == "VERB":
                objs = [c.text for c in token.children if c.dep_ in ("dobj", "pobj")]
                if objs:
                    results.append({
                        "value": f"{token.lemma_} {' '.join(objs)}",
                        "kind": "action",
                        "source": "nlp"
                    })

    return results


# -----------------------------
# Stage 3: LLM Refinement (ToT)
# -----------------------------

def build_prompt(bug, candidates):
    return [
        {
            "role": "system",
            "content": "You are an expert software test engineer."
        },
        {
            "role": "user",
            "content": f"""
Bug Summary: {bug.get('Summary', '')}
Steps to Reproduce:
{bug.get('Steps to Reproduce', '')}

Candidate Inputs:
{json.dumps(candidates, indent=2)}

Task:
1. Reason step by step about which inputs are relevant.
2. Remove irrelevant or duplicate values.
3. Infer missing boundary values if implied.
4. Return a ranked list in strict JSON.

Output format:
[
  {{
    "value": "...",
    "kind": "...",
    "rationale": "...",
    "relevance_score": 1-5
  }}
]
Return JSON only.
"""
        }
    ]


def refine_with_llm(messages):
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        temperature=0.2,
        max_completion_tokens=600
    )
    try:
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        return []


# -----------------------------
# Main Pipeline
# -----------------------------

def main():
    if not os.getenv("OPENAI_API_KEY"):
        raise EnvironmentError("OPENAI_API_KEY not set")

    df = pd.read_csv(INPUT_CSV)
    nlp = load_nlp()

    with open(OUTPUT_JSONL, "w", encoding="utf-8") as out:
        for _, row in df.iterrows():
            text = " ".join(str(row.get(col, "")) for col in df.columns)

            regex_inputs = extract_literals(text)
            nlp_inputs = extract_nlp_candidates(text, nlp)
            candidates = regex_inputs + nlp_inputs

            messages = build_prompt(row, candidates)
            refined = refine_with_llm(messages)

            record = {
                "bug_report_id": row.get("Bug Report ID", ""),
                "refined_test_inputs": refined
            }

            out.write(json.dumps(record) + "\n")

    print("Extraction completed. Output saved to extracted_test_inputs.jsonl")


if __name__ == "__main__":
    main()
