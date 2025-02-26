from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    """
    Home route to verify API is running.
    """
    return jsonify({"message": "Bin Collection API is running!"})

@app.route('/routes', methods=['GET'])
def list_routes():
    """
    Debugging route: Lists all available API endpoints.
    """
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            "endpoint": rule.endpoint,
            "methods": list(rule.methods),
            "route": str(rule)
        })
    return jsonify({"routes": routes})

@app.route('/get-bin-schedule', methods=['GET'])
def get_bin_schedule():
    """
    API Endpoint: Get bin collection schedule for a given postcode.
    Example: /get-bin-schedule?postcode=SA1%206RA
    """
    postcode = request.args.get('postcode')
    if not postcode:
        return jsonify({"error": "No postcode provided"}), 400

    # Temporary response to verify the API works
    return jsonify({
        "message": "API is working, but scraper function is not implemented yet.",
        "postcode": postcode
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render assigns a dynamic port
    print(f"🚀 Running Flask on port {port}...")  # Debugging log
    app.run(host="0.0.0.0", port=port, debug=True)
