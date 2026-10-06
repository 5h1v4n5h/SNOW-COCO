import os
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STAGE_DIR = PROJECT_ROOT / "docker_stage"

def stage_files():
    print(f"[*] Staging files into {STAGE_DIR}...")
    if STAGE_DIR.exists():
        shutil.rmtree(STAGE_DIR)
    STAGE_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Copy api, core, web, requirements.txt
    for folder in ["api", "core", "web"]:
        src = PROJECT_ROOT / folder
        dst = STAGE_DIR / folder
        print(f"  -> Copying {folder}...")
        shutil.copytree(src, dst)

    print("  -> Copying requirements.txt...")
    shutil.copy2(PROJECT_ROOT / "requirements.txt", STAGE_DIR / "requirements.txt")

    # 2. Copy data (excluding synthetic_large to keep image fast & slim)
    data_dst = STAGE_DIR / "data"
    data_dst.mkdir(parents=True, exist_ok=True)
    for data_item in ["clinical_docs", "raw_csv", "processed_chunks.json", "processed_chunks.csv"]:
        src = PROJECT_ROOT / "data" / data_item
        dst = data_dst / data_item
        if src.exists():
            print(f"  -> Copying data/{data_item}...")
            if src.is_dir():
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)

    # 3. Create clean Dockerfile inside STAGE_DIR
    dockerfile_content = """FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \\
    build-essential \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 8000

CMD ["uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8000"]
"""
    with open(STAGE_DIR / "Dockerfile", "w", encoding="utf-8") as f:
        f.write(dockerfile_content)

    print("[OK] Staging complete.")

if __name__ == "__main__":
    stage_files()
