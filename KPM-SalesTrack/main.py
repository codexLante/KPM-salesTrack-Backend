from app import create_app
import os
from dotenv import load_dotenv
from flask_cors import CORS


load_dotenv()


app=create_app()
CORS(app)


@app.route("/")
def home():
    return "Welcome KPM salesTrack"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)