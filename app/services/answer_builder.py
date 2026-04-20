from __future__ import annotations

from app.services.retriever import KnowledgeChunk, RetrievalResult

def get_teaching_points(primary_source: KnowledgeChunk) -> list[str]:
    
    # use topic aware bullet points so the answer sounds more tutorish
    title = primary_source.title.lower()
    category = primary_source.category.lower()
    
    if "python" in title:
        return [
            "- Python is popular because it is readable and used in many real-world projects.",
            "- It is often a strong first language because the syntax is easier to follow than many lower-level languages",
        ]
        
    if "function" in title or category == "functions":
        return [
            "- Functions help organize code into reusable pieces instead of repeating the same logic.",
            "- They also make programs easier to test, debug, and understand.",
        ]

    if "class" in title or "object-oriented-programming" in category:
        return [
            "- Classes help group related data and behavior together, which makes larger programs easier to organize.",
            "- They become especially useful when modeling real-world concepts or reusable components.",
        ]

    if "module" in title:
        return [
            "- Modules help split code into separate files so projects stay easier to navigate and maintain.",
            "- Importing from modules also encourages reuse instead of rewriting the same logic in multiple places.",
        ]
        
    if "loop" in title or category == "control-flow":
        return [
            "- Loops are useful when the same kind of action needs to happen multiple times.",
            "- Choosing the right loop keeps code shorter and easier to read.",
        ]

    if "conditional" in title:
        return [
            "- Conditionals let code respond differently depending on what is true at runtime.",
            "- They are one of the basic tools for adding decision-making to a program.",
        ]
        
    if "variable" in title:
        return [
            "- Variables let a program store information so it can be reused later.",
            "- Clear variable names make code easier to read and much easier to debug.",
        ]
        
    if "dictionary" in title:
        return [
            "- Dictionaries are helpful when values need to be looked up by a meaningful key.",
            "- They are one of the most common data structures used in real Python programs.",
        ]

    if "string" in title:
        return [
            "- Strings are used constantly for user input, messages, file content, and general text processing.",
            "- Learning string operations early makes many everyday Python tasks much easier.",
        ]

    if "tuple" in title:
        return [
            "- Tuples are useful when values belong together but should not be changed accidentally.",
            "- They are often used for fixed groupings of related data, such as coordinates or return values.",
        ]

    if "set" in title:
        return [
            "- Sets are especially useful when uniqueness matters more than order.",
            "- They also make membership checks efficient, which can be helpful in larger programs.",
        ]

    if "list" in title:
        return [
            "- Lists are one of the most common ways to store ordered data in Python.",
            "- List comprehensions are useful when building a new list from existing data in a compact way.",
        ]

    if "file" in title:
        return [
            "- File handling is important whenever a program needs to save information or read existing data.",
            "- Using tools like `with open(...)` helps manage files safely and avoids common resource bugs.",
        ]

    if "exception" in title or category == "debugging":
        return [
            "- Exceptions make errors visible at runtime, which helps developers find and fix problems more quickly.",
            "- Handling exceptions carefully can keep a program from crashing when something unexpected happens.",
        ]

    return [
        "- This concept helps build a stronger foundation for writing clear Python code.",
        "- Understanding the basics well makes more advanced topics easier later.",
    ]

def build_answer(user_message: str, sources: list[RetrievalResult], answer_style: str = "balanced") -> str:
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
        
    # Begin with the direct explanation from the best available source
    answer_lines = [primary_source.content]
    
    # Rendering different formatting depending on selected response option
    if answer_style in {"balanced", "explanatory"}:
        answer_lines.append("")
        answer_lines.append("Why it matters:")
        answer_lines.extend(get_teaching_points(primary_source))
    
    if answer_style == "explanatory" and supporting_titles:
        answer_lines.append("")
        answer_lines.append("You might also want to explore:")
        for title in supporting_titles.split(", "):
            answer_lines.append(f"- {title}")
            
    if answer_style == "concise" and supporting_titles:
        answer_lines.append("")
        answer_lines.append(f"Related: {supporting_titles}")
    
    
    return "\n".join(answer_lines)
