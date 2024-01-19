from flask import Flask, flash, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO
import random, hashlib
from string import ascii_uppercase
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
app.config["SECRET_KEY"] = "blabla"
socketio = SocketIO(app)
rooms = {}

# Templates
register_template = "register.html"
login_template = "login.html"
home_template = "home.html"
room_template = "room.html"
live_rooms_template = "live_rooms.html" 

# Database
database = "database.db"

def generate_unique_code(Length):
    while True:
        code = ""
        for _ in range(Length):
            code += random.choice(ascii_uppercase)
        if code not in rooms:
            break
    return code

@app.route("/login", methods=["POST", "GET"])
def login():
    connection = sqlite3.connect(database)
    if "username" in session:
            flash("You are already logged in", 'error')
            return redirect(url_for("home"))
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            flash("Please complete all the fields", 'error')
            return redirect(url_for("login"))
        
        cursor = connection.cursor()
        query = "SELECT username, password, isadmin FROM users WHERE email=?"
        cursor.execute(query, (email,))
        user = cursor.fetchone()

        if user:
            stored_password = user[1]
            hasher = hashlib.shake_256()
            hasher.update(password.encode("utf-8"))
            hashed_password = hasher.digest(32)
            
            if hashed_password == stored_password:
                session["username"] = user[0]
                session["isadmin"] = user[2]
                print("User:", user)
                print("Session username:", session["username"])
                return redirect(url_for("home"))
            else:
                flash("Incorrect password", 'error')
        else:
            flash("Email not found", 'error')

    return render_template(login_template)

@app.route("/logout")
def logout():
    session.pop("username", None)
    flash('You have successfully logged out.', 'success')
    return redirect(url_for("login"))

@app.route("/", methods=["POST", "GET"])
def home():
    if "username" not in session:
        flash('You must login first.', 'error')
        return redirect(url_for("login"))
    if request.method == "POST":
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)
        logout = request.form.get("logout")
        admin = request.form.get("admin")

        if admin:
            return redirect(url_for("admin"))

        if logout == "true":
            session.pop("username", None)
            flash('You have successfully logged out.', 'success')
            return redirect(url_for("login"))

        if join != False and not code:
            flash("Please enter a room code.", 'error')
            return render_template(home_template, code=code)

        room = code
        if create != False:
            room = generate_unique_code(4)
            rooms[room] = {"members": 1, "messages": []}
        elif code not in rooms:
            flash("Room does not exist or Invalid Code", 'error')
            return render_template(home_template, error="Room does not exist.", code=code)

        session["room"] = room
        return redirect(url_for("room"))

    return render_template(home_template)


@app.route("/room", methods=["GET", "POST"])
def room():
    if request.method == "POST":
        room_code = request.form.get("joinroom")
        if room_code in rooms:
            session["room"] = room_code
            return redirect(url_for("room"))
        else:
            flash("Room does not exist", 'error')
            return redirect(url_for("live_rooms"))

    room = session.get("room")
    if room is None or session["username"] is None or room not in rooms:
        return redirect(url_for("home"))
    members = rooms.get(room, {}).get("members", 0)
    return render_template(room_template, code=room, messages=rooms[room]["messages"], members=members)

@app.route("/register", methods=["POST", "GET"])
def register():
    connection = sqlite3.connect(database)
    if "username" in session:
        flash("You are already logged in", 'error')
        return redirect(url_for("home"))
    if request.method == "POST":
        cursor = connection.cursor()

        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("repeat_password")

        if not email or not username or not password or not confirm_password:
            flash("Please complete all the fields", 'error')
            return redirect(url_for("register"))

        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        existing_email = cursor.fetchone()

        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        existing_username = cursor.fetchone()

        if existing_email:
            flash("Email already exists", 'error')
            return redirect(url_for("register"))
        
        if existing_username:
            flash("Username already exists", 'error')
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("Passwords don't match")
            return redirect(url_for("register"))
        #elif password is None or len(password) < 8:
        #    flash("Password is too short")
        #    return redirect(url_for("register"))
        else:
            hasher = hashlib.shake_256()
            hasher.update(password.encode("utf-8"))
            hashed_password = hasher.digest(32)
            cursor.execute("INSERT INTO users (email, username, password, isadmin) VALUES (?, ?, ?, 0)", (email, username, hashed_password))
            connection.commit()
            cursor.close()
            connection.close()
            flash("You have successfully registered", 'success')
            return redirect(url_for("login"))

    return render_template(register_template)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    home = request.form.get("home")
    logout = request.form.get("logout")

    if logout == "true":
        session.pop("username", None)
        flash('You have successfully logged out.', 'success')
        return redirect(url_for("login"))
    
    if home:
        return redirect(url_for("home"))

    if "username" not in session:
        flash('You must log in first.', 'error')
        return redirect(url_for("login"))

    is_admin = session.get("isadmin", 0)

    if not is_admin:
        flash('You must be an admin to access this page.', 'error')
        return redirect(url_for("home"))

    connection = sqlite3.connect(database)
    cursor = connection.cursor()

    if request.method == "POST":
        username_to_update = request.form.get("username_to_update")
        new_email = request.form.get("new_email")
        new_username = request.form.get("new_username")
        new_password = request.form.get("new_password")
        username_to_delete = request.form.get("username_to_delete")
        addusername = request.form.get("addusername")
        addemail = request.form.get("addemail")
        addpassword = request.form.get("addpassword")

        if addusername and addemail and addpassword:                
            hasher = hashlib.shake_256()
            hasher.update(addpassword.encode("utf-8"))
            hashed_password = hasher.digest(32)

            addisadmin = 'addisadmin' in request.form

            addisadmin = int(addisadmin)

            cursor.execute("INSERT INTO users (email, username, password, isadmin) VALUES (?, ?, ?, ?)", (addemail, addusername, hashed_password, addisadmin))
            connection.commit()
            flash(f"User {addusername} added successfully.", 'success')
        

        if username_to_update and new_email:
            cursor.execute("UPDATE users SET email = ? WHERE username = ?", (new_email, username_to_update))
            connection.commit()
            flash(f"Email for {username_to_update} updated successfully.", 'success')

        if username_to_update and new_username:
            cursor.execute("UPDATE users SET username = ? WHERE username = ?", (new_username, username_to_update))
            connection.commit()
            flash(f"Username for {username_to_update} updated successfully.", 'success')

        if username_to_update and new_password:
            hasher = hashlib.shake_256()
            hasher.update(new_password.encode("utf-8"))
            hashed_password = hasher.digest(32)

            cursor.execute("UPDATE users SET password = ? WHERE username = ?", (hashed_password, username_to_update))
            connection.commit()
            flash(f"Password for {username_to_update} updated successfully.", 'success')

        if username_to_delete:
            cursor.execute("DELETE FROM users WHERE username = ?", (username_to_delete,))
            connection.commit()
            flash(f"User {username_to_delete} deleted successfully.", 'success')

    cursor.execute("SELECT username, email FROM users")
    users = cursor.fetchall()
    connection.close()

    return render_template("admin.html", users=users)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.route("/live_rooms")
def live_rooms():
    live_rooms_list = [{"code": code, "members": rooms[code]["members"]} for code in rooms]
    return render_template(live_rooms_template, live_rooms=live_rooms_list)

@socketio.on("message")
def message(data):
    room = session.get("room")
    if room not in rooms:
        return 
    
    content = {
        "name": session["username"],
        "message": data["data"]
    }
    send(content, to=room)
    rooms[room]["messages"].append(content)
    print(f"{session["username"]} said: {data['data']}")

@socketio.on("connect")
def connect(auth):
    room = session.get("room")
    name = session["username"]
    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return
    
    join_room(room)
    emit_member_count(room)
    send({"name": name, "message": "has entered the room"}, to=room)
    rooms[room]["members"] += 1
    print(f"{name} joined room {room}")

def emit_member_count(room):
    member_count = rooms[room]["members"]
    socketio.emit("update_member_count", {"members": member_count}, room=room)

@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)

    if room in rooms:
        rooms[room]["members"] -= 1
        emit_member_count(room)
        if rooms[room]["members"] <= 1:
            del rooms[room]
    
    send({"name": name, "message": "has left the room"}, to=room)
    print(f"{name} has left the room {room}")

if __name__ == "__main__":
    socketio.run(app, debug=True)