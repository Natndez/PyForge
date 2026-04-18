# PyForge

PyForge is a domain-specific AI assistant for Python learning, developer notes, and code understanding.

The goal is not to build a fake "ChatGPT clone." The goal is to build a technically honest AI project that shows how a useful assistant is assembled from smaller parts: a web app, a knowledge base, retrieval logic, answer orchestration, and eventually model-backed generation.

## What We Are Making

PyForge is a Flask web app where a user can ask Python-related questions and receive responses grounded in a curated local knowledge base.

Right now, the app can:

- render a polished chat-style interface
- store conversation history in the Flask session
- retrieve relevant Python knowledge chunks from a local JSON knowledge base
- build a response from those retrieved chunks
- show the retrieved sources in the UI so the system is inspectable

This makes the current version a small retrieval-backed assistant, not a full language model yet.

## Why We Are Making It

This project is meant to be both:

- a tutorial project that teaches the architecture of AI products
- a portfolio project that can grow into something credible for employers

The important idea behind PyForge is that strong AI projects are not just "prompt in, answer out." They are systems with clear layers:

- a user interface
- request handling
- a data source
- retrieval or context selection
- answer construction
- later, model inference and evaluation

By building those layers one at a time, the project stays understandable and technically honest.

## How We Are Making It

We are building PyForge in phases rather than trying to jump straight to a final "AI app."

### Phase 1: Product skeleton

- Flask app setup
- route handling
- HTML/CSS UI
- session-based chat history

### Phase 2: Grounding and retrieval

- local Python knowledge base
- keyword-based retrieval
- source cards in the interface
- grounded answer builder

### Later phases

- better answer formatting
- embeddings-based retrieval
- configurable generation settings
- baseline versus adapted model comparison
- evaluation scripts and reporting

This phased approach matters because it keeps every step testable and easy to reason about.

## Current Architecture

### App startup

- `app.py`
  Local development entry point.

- `app/__init__.py`
  Creates the Flask app, configures template/static folders, and registers routes.

### Web layer

- `app/routes.py`
  Handles the main page, form submissions, session state, and rendering.

### Service layer

- `app/services/retriever.py`
  Loads the knowledge base, tokenizes text, scores chunks, and returns the best matches.

- `app/services/answer_builder.py`
  Turns retrieved sources into a user-facing answer.

### Data layer

- `data/knowledge_base.json`
  The current Python knowledge base used for retrieval.

### Frontend

- `templates/index.html`
  Main Flask template for the chat UI.

- `static/css/style.css`
  Styling for layout, typography, and visual identity.

- `static/js/app.js`
  Small client-side behavior for focus and Enter-to-send.

## Current Request Flow

When a user submits a question, the app currently works like this:

1. The browser sends the message to the Flask route.
2. The route reads the form input.
3. The retriever searches the local knowledge base for relevant chunks.
4. The answer builder turns those chunks into a response.
5. The route stores the chat history and retrieved sources in the session.
6. Flask re-renders the page with the updated answer and source cards.

This is the current mental model for the whole app:

`user question -> retrieval -> answer builder -> session update -> rendered UI`

## Why The Current Design Is Useful

Even though the current version is simple, it already demonstrates several important engineering ideas:

- separating route logic from backend logic
- grounding answers in a scoped knowledge base
- showing sources so answers are inspectable
- keeping the app modular so retrieval or generation can be upgraded later

That modularity is important. We can later replace:

- keyword retrieval with embeddings
- the simple answer builder with model-backed generation
- session storage with a database

without rewriting the whole app from scratch.

## Running Locally

### 1. Open the project

In a terminal, move into the project folder:

```bash
cd custom-llm
```

If you already have the folder open in VS Code, you can use the built-in terminal there.

### 2. Create a virtual environment

This creates a project-local Python environment so dependencies stay isolated from your global Python install:

```bash
python3 -m venv .venv
```

### 3. Activate the virtual environment

On macOS or Linux:

```bash
source .venv/bin/activate
```

When activation works, your terminal prompt should start with `(.venv)`.

### 4. Install dependencies

Install the packages listed in `requirements.txt`:

```bash
PIP_USER=0 python -m pip install --no-user -r requirements.txt
```

Right now the dependency list is intentionally small because the project is still in its early phases.

### 5. Start the app

For a normal local run:

```bash
python app.py
```

Then open this URL in your browser:

`http://127.0.0.1:5000`

### Daily workflow after the first setup

Once `.venv` already exists and dependencies are installed, you usually only need:

```bash
source .venv/bin/activate
python app.py
```

## Troubleshooting Local Run

### Port 5000 is already in use

If you see an error saying port `5000` is already in use, start Flask on another port instead:

```bash
flask --app app run --debug --port 5001
```

Then open:

`http://127.0.0.1:5001`

### The browser shows a Flask template or import error

Try these checks:

1. Make sure your virtual environment is activated.
2. Make sure dependencies were installed successfully.
3. Make sure you are running the command from the project root.

### The app does not reload after code changes

Stop the server with `Ctrl+C`, then start it again:

```bash
python app.py
```

## Project Status

Current status:

- Flask app is running
- chat UI is in place
- retrieval-backed answering is working
- source inspection is working
- answer quality is still limited by the small local knowledge base and simple keyword retrieval

In other words: the project foundation is real, but the more advanced AI layers are still ahead.
