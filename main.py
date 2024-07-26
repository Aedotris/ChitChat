from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO

app = Flask(__name__)
app.config["SECRET_KEY"] = "hjhjsdahhds"
socketio = SocketIO(app)

# Sử dụng một room chat duy nhất cho mọi người
ROOM = "general"

# Lưu trữ tin nhắn trong một list
messages = []

@app.route("/", methods=["POST", "GET"])
def home():
    session.clear()
    if request.method == "POST":
        name = request.form.get("name")
        avatar = request.form.get("avatar")

        if not name:
            return render_template("home.html", error="Please enter a name.", name=name, avatar=avatar)

        session["name"] = name
        session["avatar"] = avatar
        return redirect(url_for("chat"))

    return render_template("home.html")

@app.route("/chat")
def chat():
    if session.get("name") is None:
        return redirect(url_for("home"))

    return render_template("chat.html", messages=messages)

@socketio.on("message")
def message(data):
    content = {
        "name": session.get("name"),
        "message": data["data"],
        "avatar": session.get("avatar")
    }
    messages.append(content)  # Lưu tin nhắn vào list
    send(content, to=ROOM)
    print(f"{session.get('name')} said: {data['data']}")

@socketio.on("connect")
def connect(auth):
    name = session.get("name")
    if not name:
        return

    join_room(ROOM)
    send({"name": name, "message": "has entered the room", "avatar": session.get("avatar")}, to=ROOM)
    print(f"{name} joined room {ROOM}")

@socketio.on("disconnect")
def disconnect():
    name = session.get("name")
    leave_room(ROOM)

    send({"name": name, "message": "has left the room", "avatar": session.get("avatar")}, to=ROOM)
    print(f"{name} has left the room {ROOM}")

if __name__ == "__main__":
    socketio.run(app, debug=True)