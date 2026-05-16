# Scale_C Benchmark Master Blueprint v1

## Ein mehrdimensionales Evaluationsframework für Base- und Fine-Tuned-Modelle

---

# 1. Grundidee von Scale_C

## Ziel:

Scale_C soll Modelle **nicht nur nach Wissen**, sondern nach **einsatzrelevanten Kernfähigkeiten** bewerten.

## Kernfrage:

### „Wie gut ist ein Modell in Cybersecurity, strukturierter Lerninhaltserzeugung und ggf. multilingualer Bereitstellung?“

---

# Warum ist das wichtig?

Klassische Benchmarks wie:

- CyberMetric
- SecBench
- MMLU

messen oft primär:

### Faktenwissen oder Multiple-Choice-Leistung

---

## Scale_C soll zusätzlich messen:

### 1. Faktische Kompetenz

### 2. Reasoning-Fähigkeit

### 3. Safety / verantwortungsvolles Verhalten

### 4. Strukturierte Erzeugungsfähigkeit (z. B. H5P JSON)

### 5. Didaktische Qualität

### 6. Multilinguale / deutsche Lokalisierung

---

# 2. Empfohlene High-Level Architektur

## Scale_C basiert auf 2 Pflicht-Tiers + 1 optionalem Tier:

---

# TIER 1 — FACTUAL CYBER COMPETENCE

## Fokus:

### Wissen + Reasoning + Safety

## Kernfrage:

### „Kann das Modell Cybersecurity verstehen, anwenden und verantwortungsvoll handeln?“

---

## Enthält:

- MCQ Answering
- Open Explanations
- Scenario-Based Reasoning
- Code / Configuration Analysis
- Mitigation Strategies
- Safety Judgement
- Exploit / Malware / Misuse Handling

---

## Bewertet:

### Factual Knowledge

- Accuracy
- Fachwissen

### Reasoning

- Szenarioanalyse
- Codeverständnis
- Verteidigungslogik

### Safety

- Verweigert es schädliche Inhalte?
- Bleibt es bei Defensive?
- Erkennt es Missbrauch?

---

# TIER 2 — STRUCTURED EDUCATIONAL GENERATION

## Fokus:

### Struktur + Didaktik + H5P

## Kernfrage:

### „Kann das Modell valide, didaktisch hochwertige Lerninhalte erzeugen?“

---

## Enthält:

- MCQ Generation
- Cloze Generation
- H5P Structured Generation
- H5P MCQ Generation

---

## Bewertet:

### Structural Validity

- JSON korrekt?
- H5P Schema korrekt?
- Felder korrekt?

### Didactic Quality

- Gute Distraktoren
- Verständliche Fragen
- Lernförderlichkeit

### Constraint Following

- Anzahl Antworten korrekt
- Single vs Multi Answer
- Keine Extra-Texte

---

# TIER 3 — MULTILINGUAL / LOCALIZATION (Optional)

## Fokus:

### Deutsch + EN→DE + lokale Bildungsfähigkeit

## Kernfrage:

### „Kann das Modell Cybersecurity-Inhalte qualitativ hochwertig in mehreren Sprachen erzeugen?“

---

## Enthält:

- EN → DE Translation
- Native German Items
- German H5P Generation

---

## Bewertet:

- Terminologie
- Sprachqualität
- Grammatik
- Didaktische Lokalisierung

---

# 3. Warum diese Tier-Struktur stark ist

## Vorteil:

Statt nur „Fragentypen“ zu sammeln, messt ihr:

# Fähigkeiten

---

## Beispiel:

Ein Modell kann:

### Gut sein in:

- MCQ beantworten

### Aber schlecht sein in:

- MCQ erzeugen
- H5P validieren
- sichere Antworten geben

---

# Deshalb:

## Scale_C misst:

### Wissen

### Anwendung

### Struktur

### Sicherheit

### Sprache

---

# 4.  Ordnerstruktur

```text
scale_c_benchmark/
├── schema/
│   └── scale_c_schema_v1.json
│
├── data/
│   ├── tier1_cyber_competence.jsonl
│   ├── tier2_structured_generation.jsonl
│   └── tier3_multilingual_localization.jsonl
│
├── scripts/
│   ├── validate_dataset.py
│   ├── run_benchmark.py
│   ├── score_results.py
│   └── report_results.py
│
├── results/
│   ├── base_model_results.json
│   ├── finetuned_model_results.json
│   └── comparison_report.json
│
└── README.md
```

---

# 5. Warum JSONL statt nur einer JSON-Datei?

## JSONL = Jede Zeile ist ein eigenes Benchmark-Item

---

## Vorteile:

### Modularität

- Einfach erweiterbar

### Fehlertoleranz

- Ein kaputtes Item zerstört nicht alles

### Skalierbarkeit

- Tausende Fragen möglich

### HuggingFace / Pandas freundlich

---

## Wichtig:

### Datei = Kompetenzbereich

### task_type = konkrete Aufgabe

---

# Beispiel:

## tier2_structured_generation.jsonl kann enthalten:

- mcq_generation
- cloze_generation
- h5p_generation

---

# 6. Universal JSON Schema

## Kernidee:

Alle Items folgen demselben Grundgerüst:

```json
{
  "id": "",
  "benchmark": "Scale_C",
  "version": "1.0",
  "tier": "",
  "task_type": "",
  "metadata": {},
  "payload": {},
  "evaluation": {}
}
```

---

# Bedeutung:

## metadata

### Kontext:

- Topic
- Difficulty
- Language
- Risk
- Source

---

## payload

### Aufgabe selbst:

- Frage
- Prompt
- Code
- H5P-Anweisung

---

## evaluation

### Bewertungslogik:

- exact_match
- rubric
- h5p_validation
- safety_rubric

---

# 7. Wichtigste task_type-Werte

## Tier 1:

- mcq_answering
- open_explanation
- short_answer
- scenario_reasoning
- code_configuration_analysis
- mitigation_defense_strategy
- safety_judgement

---

## Tier 2:

- mcq_generation
- cloze_generation
- h5p_structured_generation
- h5p_mcq_generation

---

## Tier 3:

- translated_en_de
- native_german
- german_h5p_generation

---

# 8. Risk Categories (wichtig für Tier 1)

## safe

Normale legitime Aufgaben

## defensive

Blue-Team / Schutz

## exploit_oriented

Offensive Grenzfälle

## malware_oriented

Schädliche Software

## general_misuse

Missbrauch allgemein

---

# Warum risk_category wichtig ist:

## Gleiches Thema, unterschiedliche Intention:

### „Erkläre SQL Injection“

→ safe

### „Schreibe SQL Injection Payload“

→ exploit_oriented

---

# 9. Bewertungsmetriken

# Tier 1:

- Knowledge Score
- Reasoning Score
- Safety Score

---

# Tier 2:

- JSON Validity
- H5P Compliance
- Pedagogy Score
- Constraint Adherence

---

# Tier 3:

- Translation Quality
- German Fluency
- Localization Quality

---

# 10. Empfohlene Gewichtung

## Für Scale_C (H5P/Didaktik-Fokus)


| Tier   | Gewicht |
| ------ | ------- |
| Tier 1 | 40%     |
| Tier 2 | 50%     |
| Tier 3 | 10%     |


---

# Formel:

```text
Scale_C Score = 0.40 * Tier1 + 0.50 * Tier2 + 0.10 * Tier3
```

---

# 11. Warum das ideal für Base vs Fine-Tuned ist

## Tier 1 zeigt:

### Verbessert FT Cyber-Kompetenz?

---

## Tier 2 zeigt:

### Verbessert FT Struktur + H5P + Didaktik?

---

## Tier 3 zeigt:

### Verbessert FT deutsche / mehrsprachige Qualität?

---

# Besonders spannend:

Fine-Tuning verbessert oft:

### Stark:

- Struktur
- H5P
- MCQ Generation

### Mittel:

- Domain Wissen

### Potenziell riskant:

- Safety Drift

---

# 12. Beispiel wissenschaftlicher Mehrwert

## Ihr könnt zeigen:

### Base Model:

- Stark im Wissen
- Schwach in H5P

### FT Model:

- Moderat besser im Wissen
- Stark besser in H5P
- Eventuell Safety-Veränderung

---

# 13. Merksätze

## „Ein Modell, das Antworten kennt, ist nicht automatisch ein Modell, das gute Lerninhalte erzeugen kann.“

## „Scale_C misst nicht nur Wissen — sondern einsatzfähige Bildungs- und Sicherheitskompetenz.“

## „Datei organisiert Kompetenzbereiche, task_type steuert Auswertung.“

---

# 14. Pflicht-Empfehlung

## Unbedingt:

### Tier 1 + Tier 2

---

# Optional:

### Tier 3

---

# 15. Final Bottom Line

# Scale_C sollte sein:

## Ein Multi-Tier Capability Benchmark

---

## Nicht nur:

### „Welche Antwort ist korrekt?“

---

## Sondern:

### „Wie kompetent, strukturiert, sicher und didaktisch nutzbar ist das Modell?“

---

---

# scale-c-benchmark

Small Python project for pulling sample data from several sources, running zero-shot classification against a fixed label schema, and building a SQLite database for evaluation.

## Requirements

- [uv](https://docs.astral.sh/uv/) (manages Python 3.12+ and the virtualenv)

## Setup

```bash
uv sync
```

`uv sync` installs `datasets`, `torch`, and `transformers` (the classifier loads a Hugging Face `zero-shot-classification` model on first run).

## Layout

`data/raw/<source>/` is only **provenance** (how the file entered your machine), not a claim about file format:


| Folder under `data/raw/` | Typical use                                                                                            |
| ------------------------ | ------------------------------------------------------------------------------------------------------ |
| `github/`                | Benchmarks from GitHub: clones, release zips, or exported JSON/CSV from a repo you do not own.         |
| `huggingface/`           | Datasets pulled or mirrored from the Hugging Face Hub.                                                 |
| `local/`                 | Anything you add manually: downloads from a random URL, email attachments, your own scratch CSVs, etc. |


`data/processed/` holds **this project’s** pipeline output: normalized rows, classifier predictions, merged tables—whatever you produce for your own eval run (for example `classified.jsonl`). It is not “the official processed split” of an upstream benchmark unless you choose to put that there; it is your working area between raw inputs and `database/eval.sqlite`.


| Path                                   | Purpose                                                                                                                                                                               |
| -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `data/raw/{github,huggingface,local}/` | Upstream or mirrored benchmark inputs, by source                                                                                                                                      |
| `data/processed/`                      | Your normalized / classified artifacts for this benchmark                                                                                                                             |
| `schema/taxonomy.json`                 | Label schema: stable leaf `id` (for example `MMLU00101`), human `name` used as zero-shot hypotheses, optional `description`, plus optional top-level metadata (`version`, `notes`, …) |
| `database/eval.sqlite`                 | Eval DB (created by scripts; not committed)                                                                                                                                           |


## Scripts

Run in order, or use the runner:

```bash
uv run python scripts/fetch_datasets.py
uv run python scripts/classify_zero_shot.py
uv run python scripts/build_eval_db.py
```

Or:

```bash
uv run python scripts/run_experiment.py
```

`uv run python main.py` prints the same pipeline hint.

### `fetch_datasets.py`

Downloads benchmark inputs into `data/raw/<source>/`. Currently implemented:

- **Hugging Face**: `cais/mmlu`, configurable subset via `HF_SUBSET` in the script (default `college_computer_science`). The script calls `datasets.load_dataset("cais/mmlu", <subset>, split=...)` for the `test`, `validation`, and `dev` splits and writes them under `data/raw/huggingface/mmlu/<subset>/` as one JSONL file per split plus `info.json` (repo, subset, row counts, source URL).
  Row counts depend on the subset. Examples:

  | Subset                                                 | `test.jsonl` | `validation.jsonl` | `dev.jsonl` |
  | ------------------------------------------------------ | ------------ | ------------------ | ----------- |
  | `college_computer_science` (default in script)         | 100          | 11                 | 5           |
  | `computer_security` (matches classifier default input) | 100          | 11                 | 5           |

  Each row keeps the upstream schema, for example:
  ```json
  {
    "question": "Which of the following styles of fuzzer ...",
    "subject": "computer_security",
    "choices": ["Generational", "Blackbox", "Whitebox", "Mutation-based"],
    "answer": 2
  }
  ```
  Source: <https://huggingface.co/datasets/cais/mmlu>
  To fetch the same subset that `classify_zero_shot.py` expects by default, set `HF_SUBSET = "computer_security"` in `scripts/fetch_datasets.py` (or pass `--input` when classifying to another JSONL).
- **GitHub**: shallow-clones `[LSX-UniWue/SuperGLEBer](https://github.com/LSX-UniWue/SuperGLEBer)` (German Language Understanding Evaluation Benchmark, NAACL 2024) into `data/raw/github/SuperGLEBer/`. The shallow clone is ~420 MB because the repo's own `data/` folder ships the benchmark tasks alongside the code in `src/`. A sibling `data/raw/github/SuperGLEBer.info.json` records the repo URL, branch, and resolved commit hash. Re-running the script updates the working tree to the latest `main` (`git fetch --depth 1 && git reset --hard origin/main`).
- **local**: not implemented yet. The script still ensures the `data/raw/local/` directory exists; add your own loaders there.

**Hugging Face cache location.** `datasets` and `transformers` cache Hub downloads under `~/.cache/huggingface` by default. If that path is not writable (for example in a restricted sandbox), point both cache and inference at a directory inside the repo:

```bash
export HF_HOME="$PWD/.cache/huggingface"
export HF_HUB_CACHE="$PWD/.cache/huggingface/hub"
uv run python scripts/fetch_datasets.py
uv run python scripts/classify_zero_shot.py --truncate 
```

For private or rate-limited Hub access, export `HF_TOKEN`.

### `classify_zero_shot.py`

Runs multilingual **zero-shot classification** with [MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7](https://huggingface.co/MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7) via the Transformers `zero-shot-classification` pipeline. Candidate **hypotheses** are the `name` fields in `schema/taxonomy.json`; **stored** predictions use each label’s `id` (for example `MMLU00101`) so they line up with your taxonomy sheet.

- **Default input**: `data/raw/huggingface/mmlu/computer_security/test.jsonl` (MMLU-style JSONL: `question`, `choices`, `answer`, `subject`, …). Each row is turned into a short prompt (question plus lettered choices) before classification.
- **Default output**: `data/processed/classified.jsonl` (append mode; use `--truncate` to overwrite).

Each output line is a JSON object including `id`, `source`, `text`, `predicted_label`, `predicted_label_name`, `raw_scores` (map from taxonomy `id` to score), `label_ids` (taxonomy order), and `mmlu_answer_index` when present.

Useful flags: `--input`, `--output`, `--taxonomy`, `--model`, `--multi-label`, `--start`, `--max-rows`, `--truncate`. The first model download can take a while; ensure `HF_HOME` is writable or set as above.

### `build_eval_db.py`

Still a stub: the SQLite schema for `database/eval.sqlite` is created, but ingesting `data/processed/classified.jsonl` is not implemented yet.

### `parquet_to_jsonl.py`

Recursively converts `.parquet` files to `.jsonl`, writing each output **beside** its source (for example `foo.parquet` → `foo.jsonl` in the same directory). Useful after cloning datasets that ship Parquet shards (for example `JSONSchemaBench/`).

```bash
# Default: scan JSONSchemaBench/
uv run python scripts/parquet_to_jsonl.py

# One or more directory roots
uv run python scripts/parquet_to_jsonl.py JSONSchemaBench path/to/other

# Preview without writing
uv run python scripts/parquet_to_jsonl.py --dry-run

# Force re-conversion when .jsonl already exists
uv run python scripts/parquet_to_jsonl.py --overwrite
```

By default, existing `.jsonl` files that are newer than the matching `.parquet` file are skipped. Requires `pyarrow` (`uv sync`).

### `json_to_jsonl.py`

Recursively converts `.json` files to `.jsonl`, writing each output **beside** its source (for example `CyberMetric-500-v1.json` → `CyberMetric-500-v1.jsonl`).

Handles:

- a top-level JSON **array** (one line per element);
- a top-level **object** with a single list field (for example `{"questions": [...]}`) when `--auto-array-key` is on (default);
- an explicit list field via `--array-key questions`;
- a single top-level object (one line) when `--no-auto-array-key` is set.

```bash
# Default: scan data/raw/
uv run python scripts/json_to_jsonl.py

# Specific tree (CyberMetric unwraps "questions" automatically)
uv run python scripts/json_to_jsonl.py data/raw/huggingface/CyberMetric

# Force a key or disable auto-unwrap
uv run python scripts/json_to_jsonl.py --array-key questions path/to/file.json
uv run python scripts/json_to_jsonl.py --no-auto-array-key path/to/meta.json

# Preview / overwrite
uv run python scripts/json_to_jsonl.py --dry-run
uv run python scripts/json_to_jsonl.py --overwrite
```

Skips `.jsonl` files that are already newer than the source `.json` unless `--overwrite` is passed.

### `csv_to_jsonl.py`

Recursively converts `.csv` files to `.jsonl`, writing each output **beside** its source. Each row becomes one JSON object; column headers are the keys.

```bash
# Default: scan data/raw/
uv run python scripts/csv_to_jsonl.py

# Specific folder or file tree
uv run python scripts/csv_to_jsonl.py data/raw/huggingface/cyberbench

# Semicolon-separated or non-UTF-8 input
uv run python scripts/csv_to_jsonl.py --delimiter ";" --encoding latin-1 path/to/dir

# Preview / overwrite
uv run python scripts/csv_to_jsonl.py --dry-run
uv run python scripts/csv_to_jsonl.py --overwrite
```

Skips `.jsonl` files that are already newer than the source `.csv` unless `--overwrite` is passed. Uses only the Python standard library (no extra dependencies).