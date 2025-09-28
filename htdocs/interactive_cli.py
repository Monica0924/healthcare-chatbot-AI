"""
Interactive CLI for the Medical Assistant AI (Informational Only)

Run:
  python interactive_cli.py

Then type your symptoms. Type 'exit' to quit.
"""

from __future__ import annotations

from medical_assistant_agent import generate_otc_advice


def main() -> None:
    print("Medical Assistant (Informational Only)")
    print("Type your symptoms and press Enter. Type 'exit' to quit.\n")
    while True:
        try:
            symptoms = input("Symptoms> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not symptoms:
            print("Please enter some symptoms or type 'exit' to quit.")
            continue
        if symptoms.lower() in {"exit", "quit", "q"}:
            print("Goodbye.")
            break

        result = generate_otc_advice(symptoms)
        print("\n" + result + "\n")


if __name__ == "__main__":
    main()


