import time
import traceback
import pandas as pd
from tqdm import tqdm

from backend.graph.workflow import graph

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

QUESTION_FILE = os.path.join(BASE_DIR, "questions.tsv")
OUTPUT_FILE = os.path.join(BASE_DIR, "evaluation_results.xlsx")
LOG_FILE = os.path.join(BASE_DIR, "evaluation_logs.txt")
SUMMARY_FILE = os.path.join(BASE_DIR, "evaluation_summary.txt")


def log_error(message):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(message + "\n")


# ------------------------
# Read Questions
# ------------------------

questions = pd.read_csv(
    QUESTION_FILE,
    sep="\t"
)

results = []

total_time = 0
success = 0
failed = 0

print(f"\nLoaded {len(questions)} questions.\n")

# ------------------------
# Evaluation Loop
# ------------------------

for _, row in tqdm(
    questions.iterrows(),
    total=len(questions),
    desc="Running Evaluation"
):

    qid = row["ID"]
    question = row["Question"]

    print(f"\n[{qid}] {question}")

    start = time.time()

    try:

        response = graph.invoke(
            {
                "question": question,
                "conversation_history": ""
            }
        )

        end = time.time()

        elapsed = round(end - start, 2)
        total_time += elapsed
        success += 1

        planner = response.get("route", "")

        answer = response.get("answer", "")

        results.append(
            {
                "Question ID": qid,
                "Question": question,
                "Planner": planner,
                "Answer": str(answer),
                "Response Time (sec)": elapsed,
                "Status": "Success"
            }
        )

    except Exception as e:

        end = time.time()

        elapsed = round(end - start, 2)

        failed += 1

        log_error(f"\n{'='*80}")
        log_error(qid)
        log_error(question)
        log_error(traceback.format_exc())

        results.append(
            {
                "Question ID": qid,
                "Question": question,
                "Planner": "",
                "Answer": "",
                "Response Time (sec)": elapsed,
                "Status": "Failed",
                "Error": str(e)
            }
        )

# ------------------------
# Save Excel
# ------------------------

df = pd.DataFrame(results)

df.to_excel(
    OUTPUT_FILE,
    index=False
)

# ------------------------
# Summary
# ------------------------

average_time = round(total_time / success, 2) if success else 0

with open(SUMMARY_FILE, "w") as f:

    f.write("Life Sciences AI Agent Evaluation\n")
    f.write("=" * 50 + "\n\n")

    f.write(f"Total Questions : {len(questions)}\n")
    f.write(f"Successful      : {success}\n")
    f.write(f"Failed          : {failed}\n")
    f.write(f"Average Time    : {average_time} sec\n")
    f.write(f"Total Time      : {round(total_time,2)} sec\n")

print("\nEvaluation Finished")
print(f"\nExcel Saved -> {OUTPUT_FILE}")
print(f"Summary     -> {SUMMARY_FILE}")
print(f"Logs        -> {LOG_FILE}")