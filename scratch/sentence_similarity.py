"""Semantic similarity between two sentences via dense embeddings.

Encodes each sentence with a Sentence Transformer (bi-encoder), computes
cosine similarity between the vectors, and optionally flags a match when
similarity meets or exceeds a threshold.

References:
  https://www.sbert.net/docs/quickstart.html
  https://www.sbert.net/docs/package_reference/util/similarity.html

Example:
  python scratch/sentence_similarity.py \\
    "The weather is lovely today." \\
    "It's so sunny outside!" \\
    --threshold 0.5
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

ROOT = Path(__file__).resolve().parents[1]

# Multilingual default (fits German/English benchmark data); override with --model.
DEFAULT_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
DEFAULT_THRESHOLD = 0.5


def encode(model: SentenceTransformer, text: str) -> np.ndarray:
    vector = model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
    return np.asarray(vector, dtype=np.float64)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity; vectors are L2-normalized after encode()."""
    return float(cos_sim(a, b).item())


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Embed two sentences and measure semantic similarity (cosine)."
    )
    parser.add_argument("sentence_a", help="First sentence")
    parser.add_argument("sentence_b", help="Second sentence")
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Hugging Face Sentence Transformer id (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        help=f"Similarity threshold for 'similar' verdict (default: {DEFAULT_THRESHOLD})",
    )
    parser.add_argument(
        "--no-threshold",
        action="store_true",
        help="Only print the cosine score; skip similar/dissimilar verdict",
    )
    parser.add_argument(
        "--show-vectors",
        action="store_true",
        help="Print embedding dimension and L2 norms (debug)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    model = SentenceTransformer(args.model)
    emb_a = encode(model, args.sentence_a)
    emb_b = encode(model, args.sentence_b)
    score = cosine_similarity(emb_a, emb_b)

    print(f"model:      {args.model}")
    print(f"sentence_a: {args.sentence_a!r}")
    print(f"sentence_b: {args.sentence_b!r}")
    print(f"cosine:     {score:.4f}")

    if args.show_vectors:
        print(f"dim:        {emb_a.shape[0]}")
        print(f"norm_a:     {np.linalg.norm(emb_a):.6f}")
        print(f"norm_b:     {np.linalg.norm(emb_b):.6f}")

    if not args.no_threshold:
        similar = score >= args.threshold
        verdict = "similar" if similar else "not similar"
        print(f"threshold:  {args.threshold:.4f}")
        print(f"verdict:    {verdict} (score {'>=' if similar else '<'} threshold)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
