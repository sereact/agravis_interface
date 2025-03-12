from flask import Flask, request, jsonify
import os

app = Flask(__name__)

STATION_ID = os.getenv("STATION_ID", "SEREACT_1")


@app.route("/<station_id>/readyForNextBin", methods=["POST"])  # ✅ Change to POST
def receive_next_source_bin(station_id):  # ✅ Better function name
    data = request.json  # Extract JSON data from the request
    print(f"NEXT SOURCE BIN RECEIVED: {data}")  # Display data in console
    return (
        jsonify(
            {
                "message": "POST request received",
                "data": data,
            }
        ),
        200,
    )


@app.route("/<station_id>/pickResponse", methods=["POST"])  # ✅ Change to POST
def receive_pick_result(station_id):  # ✅ Better function name
    data = request.json  # Extract JSON data from the request
    print(f"PICK RESULT RECEIVED: {data}")  # Display data in console

    return (
        jsonify(
            {
                "message": "POST request received",
                "data": data,
            }
        ),
        200,
    )


@app.route("/<station_id>/status", methods=["POST"])  # ✅ Change to POST
def receive_status(station_id):  # ✅ Better function name
    data = request.json  # Extract JSON data from the request
    print(f"STATUS RECEIVED: {data}")  # Display data in console

    return (
        jsonify(
            {
                "message": "POST request received",
                "data": data,
            }
        ),
        200,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)  # Start the server on port 5000
