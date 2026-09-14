from flask import Flask, request, jsonify
from flask_cors import CORS
import pyautogui
import time

app = Flask(__name__)

CORS(
    app,
    resources={
        r"/*": {
            "origins": [
                "http://127.0.0.1:5500",
                "http://localhost:5500",
                "https://sahilala213-sudo.github.io"
            ]
        }
    },
    methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"]
)

screen_width, screen_height = pyautogui.size()

last_click_time = 0
click_cooldown = 0.7


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "success": True,
        "message": "Virtual Mouse Server is running"
    })


@app.route("/move", methods=["POST", "OPTIONS"])
def move_mouse():
    if request.method == "OPTIONS":
        return "", 204

    data = request.get_json(silent=True) or {}

    x = float(data.get("x", 0))
    y = float(data.get("y", 0))

    screen_x = int(x * screen_width)
    screen_y = int(y * screen_height)

    screen_x = max(0, min(screen_x, screen_width - 1))
    screen_y = max(0, min(screen_y, screen_height - 1))

    pyautogui.moveTo(screen_x, screen_y, duration=0.03)

    return jsonify({
        "success": True,
        "x": screen_x,
        "y": screen_y
    })


@app.route("/click", methods=["POST", "OPTIONS"])
def click_mouse():
    global last_click_time

    if request.method == "OPTIONS":
        return "", 204

    current_time = time.time()

    if current_time - last_click_time < click_cooldown:
        return jsonify({
            "success": False,
            "message": "Click cooldown"
        })

    last_click_time = current_time

    data = request.get_json(silent=True) or {}
    button = data.get("button", "left")

    if button == "right":
        pyautogui.click(button="right")
    else:
        pyautogui.click(button="left")

    print(f"{button.upper()} CLICK")

    return jsonify({
        "success": True,
        "button": button
    })


@app.route("/double-click", methods=["POST", "OPTIONS"])
def double_click_mouse():
    global last_click_time

    if request.method == "OPTIONS":
        return "", 204

    current_time = time.time()

    if current_time - last_click_time < click_cooldown:
        return jsonify({
            "success": False,
            "message": "Click cooldown"
        })

    last_click_time = current_time

    pyautogui.doubleClick(interval=0.1)

    print("DOUBLE CLICK")

    return jsonify({
        "success": True,
        "button": "double"
    })


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )
