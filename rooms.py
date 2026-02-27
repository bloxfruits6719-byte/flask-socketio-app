# rooms.py
from flask import session
from flask_socketio import join_room, emit

rooms = {}

def init_socket_events(socketio):

    @socketio.on("create_room")
    def create_room(data):
        name = data["room"]
        password = data["password"]
        user = session["username"]

        rooms[name] = {
            "owner": user,
            "password": password,
            "users": [user],
            "scores": {user: 0}
        }

        join_room(name)
        emit("user_list", rooms[name]["users"], room=name)


    @socketio.on("join")
    def join(data):
        name = data["room"]
        password = data["password"]
        user = session["username"]

        if name not in rooms:
            emit("message", "Phòng không tồn tại")
            return

        if rooms[name]["password"] != password:
            emit("message", "Sai mật khẩu")
            return

        if user not in rooms[name]["users"]:
            rooms[name]["users"].append(user)
            rooms[name]["scores"][user] = 0

        join_room(name)
        emit("user_list", rooms[name]["users"], room=name)


    @socketio.on("chat")
    def chat(data):
        emit(
            "message",
            session["username"] + ": " + data["msg"],
            room=data["room"]
        )


    @socketio.on("kick")
    def kick(data):
        room = data["room"]
        target = data["user"]
        user = session["username"]

        if room not in rooms:
            return

        if rooms[room]["owner"] != user:
            return

        if target in rooms[room]["users"]:
            rooms[room]["users"].remove(target)

        emit("user_list", rooms[room]["users"], room=room)


    @socketio.on("start")
    def start(room):
        if room not in rooms:
            return

        if len(rooms[room]["users"]) < 2:
            emit("message", "Cần ít nhất 2 người")
            return

        emit("game_started", room, room=room)


    @socketio.on("disconnect")
    def disconnect_user():
        user = session.get("username")

        for r in list(rooms.keys()):
            if user in rooms[r]["users"]:
                rooms[r]["users"].remove(user)

                if not rooms[r]["users"]:
                    del rooms[r]
                else:
                    emit("user_list", rooms[r]["users"], room=r)
