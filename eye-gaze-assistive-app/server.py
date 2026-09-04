from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


# ---------------------------------------
# EYE GAZE DATA
# ---------------------------------------

current_option = "NONE"


@app.route("/gaze", methods=["POST"])
def receive_gaze():

    global current_option

    data = request.json

    current_option = data.get("option", "NONE")

    print("Gaze detected:", current_option)

    return jsonify({
        "success": True
    })


@app.route("/gaze", methods=["GET"])
def get_gaze():

    return jsonify({
        "option": current_option
    })


# ---------------------------------------
# CAREGIVER REQUEST DATA
# ---------------------------------------

latest_request = "NONE"


@app.route("/request", methods=["POST"])
def receive_request():

    global latest_request

    data = request.json

    latest_request = data.get(
        "option",
        "NONE"
    )

    print(
        "CARE REQUEST RECEIVED:",
        latest_request
    )

    return jsonify({
        "success": True,
        "message": "Request received"
    })


@app.route("/request", methods=["GET"])
def get_request():

    return jsonify({
        "request": latest_request
    })


# ---------------------------------------
# RUN SERVER
# ---------------------------------------

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )