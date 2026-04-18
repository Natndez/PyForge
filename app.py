from app import create_app


# Local development entry point.
# Keeping startup in a tiny file makes the rest of the app importable without
# also booting the dev server.
app = create_app()


if __name__ == "__main__":
    # debug=True enables auto-reload and the in-browser traceback page.
    # That is useful for local development, but we would not run production
    # this way.
    app.run(debug=True)
