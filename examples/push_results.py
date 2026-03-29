"""Push all local benchmark results to the HuggingFace dataset.

Walks through results/<connector>/ directories and uploads every
JSON file it finds.  Skips connectors with no results folder.

Usage:
    export HF_TOKEN="hf_..."
    python examples/push_results.py
"""

import glob
import os

RESULTS_DIR = "results"
REPO_ID = "diago01/llm-physics-law-breaker"


def main():
    if not os.path.isdir(RESULTS_DIR):
        print(f"No '{RESULTS_DIR}/' directory found, nothing to push.")
        return

    token = os.environ.get("HF_TOKEN", "")
    if not token:
        print("Error: HF_TOKEN environment variable is not set.")
        return

    from huggingface_hub import HfApi

    api = HfApi(token=token)

    connectors = sorted(
        d for d in os.listdir(RESULTS_DIR)
        if os.path.isdir(os.path.join(RESULTS_DIR, d))
    )

    if not connectors:
        print(f"No connector folders found under '{RESULTS_DIR}/'.")
        return

    total = 0
    for connector in connectors:
        folder = os.path.join(RESULTS_DIR, connector)
        files = sorted(glob.glob(os.path.join(folder, "*.json")))
        if not files:
            print(f"[{connector}] No JSON files, skipping.")
            continue

        print(f"[{connector}] Uploading {len(files)} file(s)...")
        for f in files:
            fname = os.path.basename(f)
            remote_path = f"results/{connector}/{fname}"
            print(f"  {fname} -> {remote_path} ...", end=" ")
            api.upload_file(
                path_or_fileobj=f,
                path_in_repo=remote_path,
                repo_id=REPO_ID,
                repo_type="dataset",
            )
            print("done")
            total += 1

    print(f"\nUploaded {total} file(s) to {REPO_ID}.")


if __name__ == "__main__":
    main()
