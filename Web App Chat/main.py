from flask import Flask, flash, render_template, request, session, redirect, url_for, jsonify, json
from flask_socketio import join_room, leave_room, send, SocketIO
import random, hashlib
from string import ascii_uppercase
from flask_cors import CORS
import sqlite3
from datetime import datetime
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
import base64

app = Flask(__name__)
app.config["SECRET_KEY"] = "blabla"
socketio = SocketIO(app)
rooms = {}

# Pymongo connection
uri = "mongodb+srv://admin:123@cluster0.4r2hpju.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri)

# MongoDB database and collection for chat logs
database: Database = client.get_database("chats")
collection: Collection = database.get_collection("chatlog")

#Images DB Connection
chat_images_db = "images"
chat_images: Collection = database.get_collection(chat_images_db)

# Users DB Connection
users_database: Database = client.get_database("users")
users_info_collection: Collection = users_database.get_collection("info")

# Templates
register_template = "register.html"
login_template = "login.html"
home_template = "home.html"
room_template = "room.html"
live_rooms_template = "live_rooms.html" 
account_management_template = "account_management.html"

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
    if "username" in session:
            flash("You are already logged in", 'error')
            return redirect(url_for("home"))
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            flash("Please complete all the fields", 'error')
            return redirect(url_for("login"))
        
        #cursor = connection.cursor()
        #query = "SELECT username, password, isadmin FROM users WHERE email=?"
        #cursor.execute(query, (email,))
        #user = cursor.fetchone()

        user = users_info_collection.find_one({"email": email})

        if user:
            stored_password = user.get("password")
            hasher = hashlib.shake_256()
            hasher.update(password.encode("utf-8"))
            hashed_password = hasher.digest(32)
            
            if hashed_password == stored_password:
                session["username"] = user["username"]
                session["isadmin"] = user.get("isadmin", 0)
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
    if "username" in session:
        flash("You are already logged in", 'error')
        return redirect(url_for("home"))
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("repeat_password")

        if not email or not username or not password or not confirm_password:
            flash("Please complete all the fields", 'error')
            return redirect(url_for("register"))

        existing_user = users_info_collection.find_one({"$or": [{"email": email}, {"username": username}]})

        if existing_user:
            flash("Email or Username already exists", 'error')
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("Passwords don't match")
            return redirect(url_for("register"))

        hasher = hashlib.shake_256()
        hasher.update(password.encode("utf-8"))
        hashed_password = hasher.digest(32)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = {
            "created": timestamp,
            "email": email,
            "username": username,
            "password": hashed_password,
            "isadmin": 0
        }
        users_info_collection.insert_one(data)

        flash("You have successfully registered", 'success')
        return redirect(url_for("login"))

    return render_template(register_template)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if "username" not in session:
        flash('You must log in first.', 'error')
        return redirect(url_for("login"))
    
    user = users_info_collection.find_one({"username": session["username"]})

    if user and user.get("isadmin", 0) != 1:
        flash('You must be an admin to access this page.', 'error')
        return redirect(url_for("home"))
    
    home = request.form.get('home')
    
    if home:
        return redirect(url_for('home'))

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

            existing_user = users_info_collection.find_one({"$or": [{"email": addemail}, {"username": addusername}]})

            if existing_user:
                flash(f"User with email {addemail} or username {addusername} already exists. Please choose a different email/username.", 'error')
            else:
                addisadmin = 'addisadmin' in request.form
                addisadmin = int(addisadmin)

                data = {
                    "email": addemail,
                    "username": addusername,
                    "password": hashed_password,
                    "isadmin": addisadmin
                }

                users_info_collection.insert_one(data)
                flash(f"User {addusername} added successfully.", 'success')
        

        if username_to_update and new_email:
            users_info_collection.update_one({"username": username_to_update}, {"$set": {"email": new_email}})
            flash(f"Email for {username_to_update} updated successfully.", 'success')

        if username_to_update and new_username:
            users_info_collection.update_one({"username": username_to_update}, {"$set": {"username": new_username}})
            flash(f"Username for {username_to_update} updated successfully to {new_username}", 'success')

        if username_to_update and new_password:
            hasher = hashlib.shake_256()
            hasher.update(new_password.encode("utf-8"))
            hashed_new_password = hasher.digest(32)

            users_info_collection.update_one({"username": username_to_update}, {"$set": {"password": hashed_new_password}})
            flash(f"Password for {username_to_update} updated successfully.", 'success')

        if username_to_delete:
            users_info_collection.delete_one({"username": username_to_delete})
            flash(f"User {username_to_delete} deleted successfully.", 'success')

    users = list(users_info_collection.find({}, {"_id": 0, "username": 1, "email": 1}))
    
    return render_template("admin.html", users=users)


@app.route("/account_management", methods=["GET", "POST"])
def account_management():
    if "username" not in session:
        flash('You are not logged in', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        old_password = request.form.get('oldPassword')
        new_password = request.form.get('newPassword')

        if email or username or old_password or new_password:
            user = users_info_collection.find_one({"username": session["username"]})
            
            if user:
                stored_password = user.get('password', '')

                hasher = hashlib.shake_256()
                hasher.update(old_password.encode("utf-8"))
                hashed_old_password = hasher.digest(32)

                if hashed_old_password == stored_password:
                    update_query = {}

                    if email:
                        update_query['email'] = email

                    if username:
                        update_query['username'] = username

                    if new_password:
                        hasher = hashlib.shake_256()
                        hasher.update(new_password.encode("utf-8"))
                        hashed_new_password = hasher.digest(32)
                        update_query['password'] = hashed_new_password

                    users_info_collection.update_one({"username": session["username"]}, {"$set": update_query})
                    flash('Account updated successfully', 'success')
                else:
                    flash('Old password is incorrect', 'error')
            else:
                flash('User not found', 'error')

    return render_template(account_management_template)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.route("/live_rooms", methods=['GET', 'POST'])
def live_rooms():
    if "username" not in session:
        flash('You must login first.', 'error')
        return redirect(url_for('login'))
    live_rooms_list = [{"code": code, "members": rooms[code]["members"]} for code in rooms]
    return render_template(live_rooms_template, live_rooms=live_rooms_list)

# Function to append chat log to MongoDB collection
def append_to_chat_log(message, sender, room):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {"timestamp": timestamp, "sender": sender, "message": message, "room": room}
    collection.insert_one(log_entry)

# Function to append chat log to MongoDB collection
def append_to_images(message, sender, room):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {"timestamp": timestamp, "sender": sender, "message": message, "room": room}
    chat_images.insert_one(log_entry)

# Function to fetch chat logs from MongoDB collection
def get_chat_logs(room):
    logs = collection.find({"room": room})
    return logs

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
    print(f"{session['username']} said: {data['data']}")
    append_to_chat_log(data["data"], session["username"], room)

@socketio.on("image")
def image(data):
    room = session.get("room")
    if room not in rooms:
        return
    content = {
        "name": session["username"],
        "message": data["data"],
        "is_image": True 
    }
    send(content, to=room)
    rooms[room]["messages"].append(content)
    append_to_images(data["data"], session["username"], room)

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

# MYSQL for users
# MongoDB for objects (images etc.)