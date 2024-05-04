from app import app
import os

if __name__ == "__main__":
    # below arrangment is done specially for Heroku
    # https://stackoverflow.com/questions/17260338/deploying-flask-with-heroku
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
