from frontend import app
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(port)
    app.run(port=port, debug=True)
