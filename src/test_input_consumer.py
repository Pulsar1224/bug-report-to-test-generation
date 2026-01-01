"""
Test Input Consumer Script
--------------------------

Consumes structured test inputs and selects top-ranked values
for EvoSuite (Java) and Pynguin (Python) integration.
"""

import json

INPUT_JSONL = "extracted_test_inputs.jsonl"
TOP_K = 3


def select_top_k(inputs, k):
    return sorted(
        inputs,
        key=lambda x: x.get("relevance_score", 0),
        reverse=True
    )[:k]


def main():
    with open(INPUT_JSONL, "r", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            bug_id = record.get("bug_report_id", "")
            inputs = record.get("refined_test_inputs", [])

            top_inputs = select_top_k(inputs, TOP_K)

            print(f"\nBug ID: {bug_id}")
            print("Seed Inputs:")
            for i, inp in enumerate(top_inputs, 1):
                print(
                    f"{i}. {inp.get('value')} "
                    f"(type={inp.get('kind')}, score={inp.get('relevance_score')})"
                )


if __name__ == "__main__":
    main()
