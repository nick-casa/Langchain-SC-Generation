from flask import Flask, render_template, request
import requests  # Import the requests library

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        prompt = request.form["prompt"]
        if not prompt:
            return render_template("home.html", error="Prompt is required.")

        # Prepare the URL to call the backend API
        backend_url = "http://127.0.0.1:5000/process"

        # Make a POST request to the backend
        try:
            response = requests.post(backend_url, json={"prompt": prompt})
            if response.status_code == 200:
                data = response.json()
                return render_template("home.html", result=data)
            else:
                return render_template(
                    "home.html", error="Failed to get a response from the backend."
                )
        except requests.exceptions.RequestException as e:
            return render_template("home.html", error=str(e))

    return render_template("home.html")


if __name__ == "__main__":
    app.run(
        debug=True, port=5001
    )  # Ensure this is running on a different port than the backend
