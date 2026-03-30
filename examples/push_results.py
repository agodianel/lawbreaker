"""Push all local benchmark results to the HuggingFace dataset.

Walks through results_v0.5/ and results_v0.6/ directories and uploads
every JSON file it finds, preserving the versioned directory structure
on HuggingFace.

Usage:
    export HF_TOKEN="hf_..."
    python examples/push_results.py
"""

import glob
import os

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ID = "diago01/llm-physics-law-breaker"
HF_README = os.path.join(_SCRIPT_DIR, "hf_readme.md")

# Versioned result directories to upload
RESULT_DIRS = [
    ("results_v0.5", os.path.join(_SCRIPT_DIR, "results_v0.5")),
    ("results_v0.6", os.path.join(_SCRIPT_DIR, "results_v0.6")),
]


def _upload_dir(api, label, local_dir):
    """Upload all JSON files under *local_dir* preserving sub-folder structure."""
    if not os.path.isdir(local_dir):
        print(f"[{label}] Directory not found, skipping.")
        return 0

    connectors = sorted(
        d for d in os.listdir(local_dir)
        if os.path.isdir(os.path.join(local_dir, d))
    )

    if not connectors:
        print(f"[{label}] No connector folders found, skipping.")
        return 0

    uploaded = 0
    for connector in connectors:
        folder = os.path.join(local_dir, connector)
        files = sorted(glob.glob(os.path.join(folder, "*.json")))
        if not files:
            print(f"[{label}/{connector}] No JSON files, skipping.")
            continue

        print(f"[{label}/{connector}] Uploading {len(files)} file(s)...")
        for f in files:
            fname = os.path.basename(f)
            remote_path = f"{label}/{connector}/{fname}"
            print(f"  {fname} -> {remote_path} ...", end=" ")
            api.upload_file(
                path_or_fileobj=f,
                path_in_repo=remote_path,
                repo_id=REPO_ID,
                repo_type="dataset",
            )
            print("done")
            uploaded += 1

    return uploaded


def main():
    token = os.environ.get("HF_TOKEN", "")
    if not token:
        print("Error: HF_TOKEN environment variable is not set.")
        return

    from huggingface_hub import HfApi

    api = HfApi(token=token)

    total = 0
    for label, local_dir in RESULT_DIRS:
        print(f"\n{'='*50}")
        print(f"Uploading {label}")
        print(f"{'='*50}")
        total += _upload_dir(api, label, local_dir)

    # Upload the dataset README
    if os.path.isfile(HF_README):
        print(f"\n{'='*50}")
        print("Uploading dataset README")
        print(f"{'='*50}")
        api.upload_file(
            path_or_fileobj=HF_README,
            path_in_repo="README.md",
            repo_id=REPO_ID,
            repo_type="dataset",
        )
        print("  hf_readme.md -> README.md ... done")
        total += 1

    print(f"\nUploaded {total} file(s) to {REPO_ID}.")


if __name__ == "__main__":
    main()
