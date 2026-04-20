from pathlib import Path
import sys

# Add the project root to Python's import path so "app" can be imported.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.services.answer_builder import build_answer
from app.services.retriever import retrieve_sources

PROMPTS_PATH = Path("data/eval_prompts.txt")
OUTPUT_PATH = Path("artifacts/eval_results.txt")


def load_prompts() -> list[str]:
    # Read prompts from the evaluation file and ignore blank lines.
    with PROMPTS_PATH.open("r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]


def format_result(prompt: str, sources, answer: str) -> str:
    # Format one evaluation result so it can be printed and saved consistently.
    lines = [
        f"Prompt: {prompt}",
        "-" * 80,
    ]

    if sources:
        lines.append("Top sources:")
        for result in sources:
            lines.append(f"- {result.chunk.title} (score: {result.score})")
    else:
        lines.append("Top sources: none")

    lines.append("")
    lines.append("Answer:")
    lines.append(answer)
    lines.append("=" * 80)

    return "\n".join(lines)


def main() -> None:
    prompts = load_prompts()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    output_sections = [
        "PyForge Evaluation Run",
        "=" * 80,
    ]

    for prompt in prompts:
        sources = retrieve_sources(prompt, top_k=3)
        answer = build_answer(prompt, sources, answer_style="balanced")
        output_sections.append(format_result(prompt, sources, answer))

    output_text = "\n\n".join(output_sections)

    print(output_text)

    with OUTPUT_PATH.open("w", encoding="utf-8") as file:
        file.write(output_text)

    print(f"\nSaved evaluation results to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
