from flask import Flask, render_template, request, redirect, session
from huffman import build_huffman_tree, generate_codes, serialize_tree
from datetime import datetime
import json

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "secretkey123"

users = {}   # temporary user storage
user_data = {}  # stores encoding history per user: {username: [encodings]}


# ------------------------ HOME → LOGIN ------------------------
@app.route("/")
def home():
    return render_template("login.html")


# ------------------------ LOGIN ------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users and users[username] == password:
            session["user"] = username
            # Initialize user data if doesn't exist
            if username not in user_data:
                user_data[username] = []
            return redirect("/dashboard")

        return render_template("login.html", error="Invalid Credentials")

    return render_template("login.html")


# ------------------------ SIGNUP ------------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users[username] = password
        user_data[username] = []  # Initialize empty encoding history
        return redirect("/login")

    return render_template("signup.html")


# ------------------------ DASHBOARD ------------------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    username = session["user"]
    
    # Initialize user data if doesn't exist
    if username not in user_data:
        user_data[username] = []
    
    encodings = user_data[username]
    
    # Calculate real statistics
    total_encodings = len(encodings)
    last_text = encodings[-1]["text"][:50] + "..." if encodings and len(encodings[-1]["text"]) > 50 else (encodings[-1]["text"] if encodings else "No encodings yet")
    
    # Calculate average compression ratio
    if encodings:
        total_ratio = sum(e.get("ratio", 0) for e in encodings)
        avg_ratio = int(total_ratio / len(encodings))
    else:
        avg_ratio = 0
    
    # Count saved encodings
    saved_count = sum(1 for e in encodings if e.get("saved", False))
    
    return render_template(
        "dashboard.html",
        username=username,
        total_encodings=total_encodings,
        last_text=last_text,
        ratio=avg_ratio,
        saved_count=saved_count
    )


# ------------------------ ENCODE PAGE (GET) ------------------------
@app.route("/encode", methods=["GET"])
def encode_page():
    if "user" not in session:
        return redirect("/login")

    return render_template("index.html")      # TEXT INPUT PAGE


# ------------------------ ENCODE RESULT (POST) ------------------------
@app.route("/encode", methods=["POST"])
def encode():
    if "user" not in session:
        return redirect("/login")

    username = session["user"]
    text = request.form["text"]

    root, freq = build_huffman_tree(text)
    codes = generate_codes(root)
    encoded = "".join(codes[ch] for ch in text)
    
    # Serialize tree for visualization
    tree_data = serialize_tree(root)
    tree_json = json.dumps(tree_data)
    
    # Calculate compression ratio
    original_size = len(text) * 8  # Assuming 8 bits per character
    encoded_size = len(encoded)
    if original_size > 0:
        ratio = int((1 - encoded_size / original_size) * 100)
    else:
        ratio = 0
    
    # Save encoding to user history
    if username not in user_data:
        user_data[username] = []
    
    encoding_record = {
        "text": text,
        "encoded": encoded,
        "frequency": freq,
        "codes": codes,
        "ratio": ratio,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "saved": False
    }
    
    user_data[username].append(encoding_record)

    return render_template(
        "result.html",
        text=text,
        frequency=freq,
        codes=codes,
        encoded=encoded,
        ratio=ratio,
        encoding_id=len(user_data[username]) - 1,
        tree_json=tree_json
    )


# ------------------------ HISTORY ------------------------
@app.route("/history")
def history():
    if "user" not in session:
        return redirect("/login")
    
    username = session["user"]
    if username not in user_data:
        user_data[username] = []
    
    encodings = user_data[username]
    # Create list with original indices for proper mapping
    encodings_with_indices = [(len(encodings) - 1 - i, enc) for i, enc in enumerate(reversed(encodings))]
    
    return render_template(
        "history.html",
        username=username,
        encodings_with_indices=encodings_with_indices,
        total_count=len(encodings)
    )


# ------------------------ SAVE ENCODING ------------------------
@app.route("/save/<int:encoding_id>")
def save_encoding(encoding_id):
    if "user" not in session:
        return redirect("/login")
    
    username = session["user"]
    if username in user_data and 0 <= encoding_id < len(user_data[username]):
        user_data[username][encoding_id]["saved"] = True
    
    return redirect("/history")


# ------------------------ CLEAR ALL ------------------------
@app.route("/clear", methods=["POST"])
def clear_all():
    if "user" not in session:
        return redirect("/login")
    
    username = session["user"]
    if username in user_data:
        user_data[username] = []
    
    return redirect("/dashboard")


# ------------------------ LOGOUT ------------------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True, port=5001, host='127.0.0.1')
