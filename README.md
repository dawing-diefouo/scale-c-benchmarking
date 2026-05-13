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

* CyberMetric
* SecBench
* MMLU

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

* MCQ Answering
* Open Explanations
* Scenario-Based Reasoning
* Code / Configuration Analysis
* Mitigation Strategies
* Safety Judgement
* Exploit / Malware / Misuse Handling

---

## Bewertet:

### Factual Knowledge

* Accuracy
* Fachwissen

### Reasoning

* Szenarioanalyse
* Codeverständnis
* Verteidigungslogik

### Safety

* Verweigert es schädliche Inhalte?
* Bleibt es bei Defensive?
* Erkennt es Missbrauch?

---

# TIER 2 — STRUCTURED EDUCATIONAL GENERATION

## Fokus:

### Struktur + Didaktik + H5P

## Kernfrage:

### „Kann das Modell valide, didaktisch hochwertige Lerninhalte erzeugen?“

---

## Enthält:

* MCQ Generation
* Cloze Generation
* H5P Structured Generation
* H5P MCQ Generation

---

## Bewertet:

### Structural Validity

* JSON korrekt?
* H5P Schema korrekt?
* Felder korrekt?

### Didactic Quality

* Gute Distraktoren
* Verständliche Fragen
* Lernförderlichkeit

### Constraint Following

* Anzahl Antworten korrekt
* Single vs Multi Answer
* Keine Extra-Texte

---

# TIER 3 — MULTILINGUAL / LOCALIZATION (Optional)

## Fokus:

### Deutsch + EN→DE + lokale Bildungsfähigkeit

## Kernfrage:

### „Kann das Modell Cybersecurity-Inhalte qualitativ hochwertig in mehreren Sprachen erzeugen?“

---

## Enthält:

* EN → DE Translation
* Native German Items
* German H5P Generation

---

## Bewertet:

* Terminologie
* Sprachqualität
* Grammatik
* Didaktische Lokalisierung

---

# 3. Warum diese Tier-Struktur stark ist

## Vorteil:

Statt nur „Fragentypen“ zu sammeln, messt ihr:

# Fähigkeiten

---

## Beispiel:

Ein Modell kann:

### Gut sein in:

* MCQ beantworten

### Aber schlecht sein in:

* MCQ erzeugen
* H5P validieren
* sichere Antworten geben

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

* Einfach erweiterbar

### Fehlertoleranz

* Ein kaputtes Item zerstört nicht alles

### Skalierbarkeit

* Tausende Fragen möglich

### HuggingFace / Pandas freundlich

---

## Wichtig:

### Datei = Kompetenzbereich

### task_type = konkrete Aufgabe

---

# Beispiel:

## tier2_structured_generation.jsonl kann enthalten:

* mcq_generation
* cloze_generation
* h5p_generation

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

* Topic
* Difficulty
* Language
* Risk
* Source

---

## payload

### Aufgabe selbst:

* Frage
* Prompt
* Code
* H5P-Anweisung

---

## evaluation

### Bewertungslogik:

* exact_match
* rubric
* h5p_validation
* safety_rubric

---

# 7. Wichtigste task_type-Werte

## Tier 1:

* mcq_answering
* open_explanation
* short_answer
* scenario_reasoning
* code_configuration_analysis
* mitigation_defense_strategy
* safety_judgement

---

## Tier 2:

* mcq_generation
* cloze_generation
* h5p_structured_generation
* h5p_mcq_generation

---

## Tier 3:

* translated_en_de
* native_german
* german_h5p_generation

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

* Knowledge Score
* Reasoning Score
* Safety Score

---

# Tier 2:

* JSON Validity
* H5P Compliance
* Pedagogy Score
* Constraint Adherence

---

# Tier 3:

* Translation Quality
* German Fluency
* Localization Quality

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

* Struktur
* H5P
* MCQ Generation

### Mittel:

* Domain Wissen

### Potenziell riskant:

* Safety Drift

---

# 12. Beispiel wissenschaftlicher Mehrwert

## Ihr könnt zeigen:

### Base Model:

* Stark im Wissen
* Schwach in H5P

### FT Model:

* Moderat besser im Wissen
* Stark besser in H5P
* Eventuell Safety-Veränderung

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
