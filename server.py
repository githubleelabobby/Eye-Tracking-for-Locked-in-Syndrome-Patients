from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)


@app.route("/")
def patient_interface():
    return send_from_directory(app.root_path, "index.html")


@app.route("/caregiver")
def caregiver_interface():
    return send_from_directory(app.root_path, "caregiver.html")


@app.route("/<path:filename>")
def project_asset(filename):
    allowed_assets = {
        "style.css",
        "script.js",
        "Water.png.png",
        "Toilet.png.jpeg",
        "Pain.png.jpeg",
        "Help.png.jpeg",
    }
    if filename not in allowed_assets:
        return jsonify({"error": "Not found"}), 404
    return send_from_directory(app.root_path, filename)


# ---------------------------------------
# EYE GAZE DATA
# ---------------------------------------

current_option = "NONE"


@app.route("/gaze", methods=["POST"])
def receive_gaze():

    global current_option

    data = request.json

    current_option = data.get(
        "option",
        "NONE"
    )

    print(
        "Gaze detected:",
        current_option
    )

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
request_time = ""
request_acknowledged = False


# ---------------------------------------
# RECEIVE PATIENT REQUEST
# ---------------------------------------

@app.route("/request", methods=["POST"])
def receive_request():

    global latest_request
    global request_time
    global request_acknowledged

    data = request.json

    new_request = data.get(
        "option",
        "NONE"
    )

    # -----------------------------------
    # Prevent duplicate request
    # -----------------------------------

    if new_request == latest_request:
        return jsonify({
            "success": True,
            "message": "Duplicate request ignored"
        })


    latest_request = new_request

    request_time = datetime.now().strftime(
        "%I:%M:%S %p"
    )

    request_acknowledged = False

    print(
        "CARE REQUEST RECEIVED:",
        latest_request,
        "at",
        request_time
    )

    return jsonify({
        "success": True,
        "message": "Request received",
        "option": latest_request,
        "time": request_time
    })


# ---------------------------------------
# GET CURRENT CAREGIVER REQUEST
# ---------------------------------------

@app.route("/request", methods=["GET"])
def get_request():

    return jsonify({
        "request": latest_request,
        "time": request_time,
        "acknowledged": request_acknowledged
    })


# ---------------------------------------
# ACKNOWLEDGE REQUEST
# ---------------------------------------

@app.route("/acknowledge", methods=["POST"])
def acknowledge_request():

    global latest_request
    global request_acknowledged

    request_acknowledged = True

    print(
        "CAREGIVER ACKNOWLEDGED:",
        latest_request
    )

    return jsonify({
        "success": True,
        "message": "Request acknowledged"
    })


# ---------------------------------------
# CLEAR REQUEST
# ---------------------------------------

@app.route("/clear-request", methods=["POST"])
def clear_request():

    global latest_request
    global request_time
    global request_acknowledged

    latest_request = "NONE"
    request_time = ""
    request_acknowledged = False

    print("REQUEST CLEARED")

    return jsonify({
        "success": True,
        "message": "Request cleared"
    })


# ---------------------------------------
# RUN SERVER
# ---------------------------------------

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
