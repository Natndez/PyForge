from flask import Blueprint, redirect, render_template, request, session, url_for

from app.services.answer_builder import build_answer
from app.services.retriever import retrieve_sources


# The "main" blueprint owns the browser-facing routes for the current app.
main = Blueprint("main", __name__)


@main.route("/", methods=["GET", "POST"])
def index():
    # Session state lets us keep a lightweight chat history without a database.
    # Flask stores session data per browser session, which is enough for this
    # tutorial phase and keeps the architecture simple.
    history = session.get("history", [])
    last_sources = session.get("last_sources", [])
    selected_style = session.get("answer_style", "balanced")
    selected_top_k = session.get("top_k", 3)

    if request.method == "POST":
        # request.form contains fields submitted by the HTML form in index.html.
        user_message = request.form.get("message", "").strip()
        
        # To control the style of the answer
        answer_style = request.form.get("answer_style", "balanced")
        
        # Top k selection
        top_k = int(request.form.get("top_k", 3))
        
        if user_message:
            # Retrieval is the first "AI system" step: find relevant local context.
            # Right now this is keyword overlap against a curated JSON knowledge base.
            sources = retrieve_sources(user_message, top_k=top_k)

            # We store both sides of the conversation so the template can render a
            # chat-like transcript on the next page load.
            history.append({"role": "user", "content": user_message})
            history.append(
                {
                    "role": "assistant",
                    # The answer builder is intentionally separate from the route.
                    # Routes should coordinate work, not contain all of the logic.
                    "content": build_answer(user_message, sources, answer_style),
                }
            )
            session["history"] = history
            session["answer_style"] = answer_style
            session["top_k"] = top_k

            # Sessions need plain JSON-serializable structures. The retriever
            # returns dataclasses, so we flatten them into dictionaries here.
            session["last_sources"] = [
                {
                    "title": result.chunk.title,
                    "category": result.chunk.category,
                    "content": result.chunk.content,
                    "score": result.score,
                }
                for result in sources
            ]
            # Redirect after POST avoids duplicate form submissions on refresh.
            # This is the common Post/Redirect/Get pattern in server-rendered apps.
            return redirect(url_for("main.index"))

    # On GET, or after the redirect, render the page with the current session data.
    return render_template(
        "index.html",
        history=history,
        sources=last_sources,
        answer_style=selected_style,
        top_k=selected_top_k,
    )


@main.post("/reset")
def reset():
    # Resetting the session gives us a clean slate without touching any other user.
    session["history"] = []
    session["last_sources"] = []
    session["answer_style"] = "balanced"
    session["top_k"] = 3
    return redirect(url_for("main.index"))
