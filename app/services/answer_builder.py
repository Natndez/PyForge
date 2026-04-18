from __future__ import annotations

from app.services.retriever import KnowledgeChunk, RetrievalResult

# build answer helper function

def get_teaching_points(primary_source: KnowledgeChunk) -> list[str]:
      # Use simple topic-aware bullets so the answer sounds more like a tutor.
      title = primary_source.title.lower()
      category = primary_source.category.lower()

      if "python" in title:
          return [
              "- Python is popular because it is readable and used in many real-world projects.",
              "- It is often a strong first language because the syntax is easier to follow than many lower-level languages.",
          ]

      if "function" in title or category == "functions":
          return [
              "- Functions help you organize code into reusable pieces instead of repeating logic.",
              "- They also make programs easier to test, debug, and understand.",
          ]

      if "loop" in title or category == "control-flow":
          return [
              "- Loops are useful when you need to repeat the same kind of action multiple times.",
              "- Picking the right loop makes your code shorter and easier to read.",
          ]

      if "variable" in title:
          return [
              "- Variables let you store information so you can reuse it later in your program.",
              "- Clear variable names make code much easier to read and debug.",
          ]

      if "dictionary" in title:
          return [
              "- Dictionaries are helpful when you want to look up information by a meaningful key.",
              "- They are extremely common in real Python programs because they make data access fast and]clear.",
          ]

      if "list" in title:
          return [
              "- Lists are one of the most common ways to store ordered data in Python.",
              "- List comprehensions are useful when you want a compact way to build a new list from existing]data.",
          ]
      return [
          "- This concept helps build a stronger foundation for writing clear Python code.",
          "- Understanding the basics well makes harder topics easier later.",
      ]




def build_answer(user_message: str, sources: list[RetrievalResult]) -> str:
    # This is not a true language model yet. It is an orchestration layer that
    # turns retrieved source chunks into a readable answer for the user.
    #
    # The important design idea is separation of concerns:
    # - retriever decides what context is relevant
    # - answer builder decides how to present that context
    #
    # Later we can replace this with prompt assembly and model inference without
    # rewriting the route.

    # If retrieval found nothing, say so explicitly instead of pretending to know.
    if not sources:
        return (
            "I could not find a strong match in the current PyForge knowledge base yet. "
            "Try asking about Python basics, loops, functions, dictionaries, or debugging."
        )

    primary_result = sources[0]
    primary_source = primary_result.chunk
    supporting_titles = ", ".join(result.chunk.title for result in sources[1:])

    # A weak top score means the app found a partial keyword overlap but probably
    # not a direct answer. This is a simple confidence guardrail.
    if primary_result.score < 2:
        return (
            "I found only a weak match in the current knowledge base, so I do not want to "
            "pretend I have a precise answer yet. "
            f"The closest source was {primary_source.title}, which says: {primary_source.content}"
        )
        
    # Open with the strongest matching explanation, then add short teaching points.
    answer_lines = [
        primary_source.content,
        "",
        "Why it matters:",
    ]
    
    # Add topic-aware teaching points based on the type of concept we retrieved
    answer_lines.extend(get_teaching_points(primary_source))
    
    # Supporting sources become related topics the user can explore next
    if supporting_titles:
        answer_lines.append("")
        answer_lines.append("You might also want to explore")
        for title in supporting_titles.split(", "):
            answer_lines.append(f"- {title}")
    
    return "\n".join(answer_lines)
