# -*- coding: utf-8 -*-

import json
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# =========================
# KONFIGURATION
# =========================

# FÃ¼r erste Tests kleine Modelle nutzen
BASE_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"
FINETUNED_MODEL = "segolilylabs/Lily-Cybersecurity-7B-v0.2"  # SpÃ¤ter z. B. fdtn-ai/Foundation-Sec-8B

MAX_QUESTIONS = 50


# =========================
# DATEN LADEN
# =========================

def load_questions(path):
    """
    LÃ¤dt CyberMetric JSON im Format:
    {
        "questions": [...]
    }
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data["questions"][:MAX_QUESTIONS]


# =========================
# MODELL LADEN (EINMALIG)
# =========================

def load_model(model_id):
    """
    LÃ¤dt Tokenizer + Modell und erkennt automatisch CPU/GPU
    """
    print(f"?? Lade Modell: {model_id}")

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id)

    # Manche Modelle haben kein pad_token
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)

    print(f"? Modell geladen auf: {device}")

    return tokenizer, model, device


# =========================
# MODELL ABFRAGEN
# =========================

def query_model(tokenizer, model, device, prompt):
    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=1024
    ).to(device)

    input_length = inputs["input_ids"].shape[1]

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=5,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id
        )

    generated_tokens = outputs[0][input_length:]

    response = tokenizer.decode(
        generated_tokens,
        skip_special_tokens=True
    ).strip()

    return response


# =========================
# ANTWORT EXTRAKTION
# =========================

import re

def extract_answer(text):
    text = text.strip().upper()

    match = re.search(r"\b([ABCD])\b", text)
    if match:
        return match.group(1)

    match = re.search(r"ANSWER\s*[:\-]?\s*([ABCD])", text)
    if match:
        return match.group(1)

    return "X"


# =========================
# PROMPT BAUEN
# =========================

def build_prompt(question_obj):
    """
    Erstellt standardisierten Multiple-Choice Prompt
    """
    answers_text = "\n".join([
        f"{key}) {value}"
        for key, value in question_obj["answers"].items()
    ])

    prompt = f"""Answer this cybersecurity multiple-choice question with only one letter: A, B, C, or D.

Question:
{question_obj["question"]}

Options:
{answers_text}

Answer:"""

    return prompt


# =========================
# BENCHMARK
# =========================

def run_benchmark(model_name, tokenizer, model, device, questions):
    """
    FÃ¼hrt Benchmark fÃ¼r ein Modell durch
    """
    print(f"\n?? Teste Modell: {model_name}")
    print("-" * 70)

    correct = 0
    incorrect = 0
    errors = 0
    details = []

    for i, q in enumerate(questions, 1):
        try:
            prompt = build_prompt(q)

            response = query_model(
                tokenizer,
                model,
                device,
                prompt
            )
            print("RAW RESPONSE:", repr(response))

            predicted = extract_answer(response)
            correct_answer = q["solution"].strip().upper()

            is_correct = predicted == correct_answer

            if is_correct:
                correct += 1
                status = "?"
            else:
                incorrect += 1
                status = "?"

            print(
                f"  {status} Q{i}: Predicted={predicted} | Correct={correct_answer}"
            )

            details.append({
                "question_id": i,
                "question": q["question"],
                "predicted": predicted,
                "correct": correct_answer,
                "is_correct": is_correct
            })

        except Exception as e:
            errors += 1
            print(f"  ? Error Q{i}: {str(e)}")

    accuracy = (correct / len(questions)) * 100

    return {
        "model_name": model_name,
        "accuracy": accuracy,
        "correct": correct,
        "incorrect": incorrect,
        "errors": errors,
        "details": details
    }


# =========================
# ERGEBNISSE SPEICHERN
# =========================

def save_results(base_results, finetuned_results):
    improvement = finetuned_results["accuracy"] - base_results["accuracy"]

    final_results = {
        "base_model": base_results,
        "finetuned_model": finetuned_results,
        "improvement_absolute": improvement,
        "improvement_relative_percent": (
            (improvement / base_results["accuracy"]) * 100
            if base_results["accuracy"] > 0 else 0
        )
    }

    with open("benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump(final_results, f, indent=2, ensure_ascii=False)

    print("\n?? Ergebnisse gespeichert: benchmark_results.json")


# =========================
# MAIN
# =========================

def main():
    print("=" * 70)
    print("BENCHMARK 1: CYBERMETRIC MULTIPLE-CHOICE")
    print("=" * 70)

    # Fragen laden
    questions = load_questions("CyberMetric-500.json")

    print(f"?? Geladene Fragen: {len(questions)}")

    import gc
    import torch

    # Base laden + testen
    tokenizer_base, model_base, device_base = load_model(BASE_MODEL)

    base_results = run_benchmark(
        BASE_MODEL,
        tokenizer_base,
        model_base,
        device_base,
        questions
    )

    # Base aus GPU-Speicher entfernen
    del model_base
    del tokenizer_base
    gc.collect()
    torch.cuda.empty_cache()

    # Finetuned laden + testen
    tokenizer_ft, model_ft, device_ft = load_model(FINETUNED_MODEL)

    finetuned_results = run_benchmark(
        FINETUNED_MODEL,
        tokenizer_ft,
        model_ft,
        device_ft,
        questions
    )

    # Optional danach auch entladen
    del model_ft
    del tokenizer_ft
    gc.collect()
    torch.cuda.empty_cache()

    # Ergebnisse
    print("\n" + "=" * 70)
    print("ERGEBNISSE")
    print("=" * 70)

    print(f"\n?? Base Model ({BASE_MODEL}):")
    print(
        f"   Accuracy: {base_results['accuracy']:.1f}% "
        f"({base_results['correct']}/{len(questions)} korrekt)"
    )
    print(f"   Fehler: {base_results['errors']}")

    print(f"\n?? Finetuned Model ({FINETUNED_MODEL}):")
    print(
        f"   Accuracy: {finetuned_results['accuracy']:.1f}% "
        f"({finetuned_results['correct']}/{len(questions)} korrekt)"
    )
    print(f"   Fehler: {finetuned_results['errors']}")

    improvement = (
        finetuned_results["accuracy"] - base_results["accuracy"]
    )

    relative_improvement = (
        (improvement / base_results["accuracy"]) * 100
        if base_results["accuracy"] > 0 else 0
    )

    print(f"\n?? IMPROVEMENT:")
    print(f"   Absolute: {improvement:+.1f} percentage points")
    print(f"   Relativ: {relative_improvement:+.1f}%")

    print("\n" + "=" * 70)

    # Speichern
    save_results(base_results, finetuned_results)


if __name__ == "__main__":
    main()