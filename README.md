## Project Overview
# bug-report-to-test-generation
Hybrid NLP and Large Language Model–based pipeline for bug-report–driven automated test input extraction and integration with EvoSuite and Pynguin.
# Bug-Report–Driven Test Generation Using Hybrid NLP–LLM Techniques

This repository contains the reference implementation of the hybrid bug-report–driven
test input extraction pipeline proposed in the MSc thesis:

**"Bug-Report–Driven Automated Test Generation Using Hybrid NLP and Large Language Models"**

The project demonstrates how unstructured bug reports can be transformed into
high-quality, structured test inputs using a combination of:
- Regular-expression-based literal extraction
- Natural Language Processing (NLP)
- Large Language Models (LLMs) with Tree-of-Thought prompting

These extracted inputs are then used as seed values for automated test generation tools
such as EvoSuite (Java) and Pynguin (Python).

---
## Flow - 
THESIS (Chapter 3 + Appendices)
        ↓
   GitHub Link
        ↓
    README.md
        ↓
  Code Execution

---
## Repository Structure
src/
hybrid_nlp_llm_pipeline.py # Main extraction pipeline
test_input_consumer.py # Integration with EvoSuite / Pynguin

data/
sample_bug_reports.csv # Sample bug report dataset

requirements.txt # Python dependencies

---

## Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/Pulsar1224/bug-report-driven-test-generation.git
cd bug-report-driven-test-generation

Install dependencies:
pip install -r requirements.txt
python -m spacy download en_core_web_sm

Set the OpenAI API key as an environment variable:
export OPENAI_API_KEY="your_api_key_here"

(On Windows PowerShell)
setx OPENAI_API_KEY "your_api_key_here"

## Running the Pipeline
1. Execute the hybrid extraction pipeline:
python src/hybrid_nlp_llm_pipeline.py
### Output - 
  This produces a structured output file: extracted_test_inputs.jsonl

2. Run the consumer script to prepare seed inputs:
python src/test_input_consumer.py
### Output - 
  The selected inputs can then be injected into EvoSuite (Java) or Pynguin (Python) to guide automated test generation.
