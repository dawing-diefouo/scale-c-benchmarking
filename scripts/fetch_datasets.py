"""Download or copy benchmark inputs into data/raw/<source>/.

Currently implemented:
- huggingface: pulls a `cais/mmlu` subset (test/validation/dev) into
  `data/raw/huggingface/mmlu/<subset>/` as one JSONL file per split, plus
  a small `info.json` with provenance.
- github: shallow-clones the SuperGLEBer benchmark repo into
  `data/raw/github/SuperGLEBer/`, plus an `info.json` recording the
  resolved commit.
"""

import json
import subprocess
from pathlib import Path

from datasets import load_dataset

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"

# SOURCES = ("github", "huggingface", "local")
SOURCES = ("huggingface")

HF_REPO = "SEC-bench/SEC-bench"
HF_SUBSET = "default"
HF_SPLITS = ("eval", "cve", "oss")

GH_REPO_URL = "https://github.com/LSX-UniWue/SuperGLEBer.git"
GH_REPO_NAME = "SuperGLEBer"
GH_REPO_BRANCH = "main"


def fetch_mmlu_computer_security() -> Path:
    out_dir = RAW / "huggingface" / "mmlu" / HF_SUBSET
    out_dir.mkdir(parents=True, exist_ok=True)

    written: dict[str, int] = {}
    for split in HF_SPLITS:
        ds = load_dataset(HF_REPO, HF_SUBSET, split=split)
        out_file = out_dir / f"{split}.jsonl"
        with out_file.open("w", encoding="utf-8") as f:
            for row in ds:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        written[split] = len(ds)
        print(f"  {split}: {len(ds)} rows -> {out_file.relative_to(ROOT)}")

    info = {
        "repo": HF_REPO,
        "subset": HF_SUBSET,
        "splits": written,
        "source_url": f"https://huggingface.co/datasets/{HF_REPO}/viewer/{HF_SUBSET}",
    }
    (out_dir / "info.json").write_text(json.dumps(info, indent=2) + "\n", encoding="utf-8")
    return out_dir


def fetch_supergleber_github() -> Path:
    out_dir = RAW / "github" / GH_REPO_NAME
    out_dir.parent.mkdir(parents=True, exist_ok=True)

    if (out_dir / ".git").exists():
        print(f"  {GH_REPO_NAME}: already cloned, fetching latest...")
        subprocess.check_call(
            ["git", "-C", str(out_dir), "fetch", "--depth", "1", "origin", GH_REPO_BRANCH]
        )
        subprocess.check_call(
            ["git", "-C", str(out_dir), "reset", "--hard", f"origin/{GH_REPO_BRANCH}"]
        )
    else:
        print(f"  {GH_REPO_NAME}: shallow-cloning {GH_REPO_URL}...")
        subprocess.check_call(
            [
                "git",
                "clone",
                "--depth",
                "1",
                "--branch",
                GH_REPO_BRANCH,
                GH_REPO_URL,
                str(out_dir),
            ]
        )

    commit = subprocess.check_output(
        ["git", "-C", str(out_dir), "rev-parse", "HEAD"], text=True
    ).strip()
    info = {
        "repo": GH_REPO_URL,
        "branch": GH_REPO_BRANCH,
        "commit": commit,
        "source_url": "https://github.com/LSX-UniWue/SuperGLEBer",
    }
    (out_dir.parent / f"{GH_REPO_NAME}.info.json").write_text(
        json.dumps(info, indent=2) + "\n", encoding="utf-8"
    )
    print(f"  {GH_REPO_NAME}: at {commit[:12]} -> {out_dir.relative_to(ROOT)}")
    return out_dir


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    for name in SOURCES:
        (RAW / name).mkdir(parents=True, exist_ok=True)

    print(f"Fetching {HF_REPO} / {HF_SUBSET} from Hugging Face...")
    hf_out = fetch_mmlu_computer_security()
    print(f"Done. Files under {hf_out.relative_to(ROOT)}\n")

    print(f"Fetching {GH_REPO_URL} from GitHub...")
    gh_out = fetch_supergleber_github()
    print(f"Done. Repo at {gh_out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
