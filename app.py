from flask import Flask, request, redirect, session, render_template_string
from flask_socketio import SocketIO
from rooms import init_socket_events

app = Flask(__name__)
app.secret_key = "super_secret_key_123"

# ===== SOCKETIO =====
socketio = SocketIO(app)
init_socket_events(socketio)

# ====== DATABASE GIẢ LẬP ======
users = {
    "admin": {"password": "123456", "role": "admin", "locked": False},
    "mod": {"password": "123456", "role": "mod", "locked": False},
    "user": {"password": "123456", "role": "user", "locked": False}
}

# ================= LOGIN UI =================
def render_login(error=""):
    html = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <title>Đăng nhập</title>
    </head>
    <body>
    <h2>Đăng nhập</h2>
    <div style="color:red;">{{ error }}</div>
    <form method="POST">
    <input name="username" placeholder="Username" required><br><br>
    <input name="password" type="password" placeholder="Password" required><br><br>
    <button type="submit">Sign In</button>
    </form>
    <a href="/register">Chưa có tài khoản? Đăng ký</a>
    </body>
    </html>
    """
    return render_template_string(html, error=error)

# ================= REGISTER UI =================
def render_register(error=""):
    html = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <title>Đăng ký</title>
    </head>
    <body>
    <h2>Đăng ký</h2>
    <div style="color:red;">{{ error }}</div>
    <form method="POST">
    <input name="username" required><br><br>
    <input name="password" type="password" required><br><br>
    <button type="submit">Tạo tài khoản</button>
    </form>
    <a href="/">Quay lại đăng nhập</a>
    </body>
    </html>
    """
    return render_template_string(html, error=error)

# ================= LOGIN =================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users:

            if users[username]["locked"]:
                return render_login("Tài khoản đã bị khóa")

            if users[username]["password"] == password:
                session["user"] = username
                session["role"] = users[username]["role"]
                return redirect("/dashboard")

        return render_login("Sai tài khoản hoặc mật khẩu")

    return render_login()

# ================= REGISTER =================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users:
            return render_register("Tài khoản đã tồn tại")

        users[username] = {
            "password": password,
            "role": "user",
            "locked": False
        }

        return redirect("/")

    return render_register()

# ================= DASHBOARD =================
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    role = session.get("role")
    username = session.get("user")

    # ADMIN PANEL
    if role == "admin":
        user_list = ""

        for u in users:
            if u != "admin":
                status = "🔒 Locked" if users[u]["locked"] else "🟢 Active"
                action = "unlock" if users[u]["locked"] else "lock"

                user_list += f"""
                <p>
                {u} ({users[u]['role']}) - {status}
                <a href='/admin/{action}/{u}'>[{action.upper()}]</a>
                </p>
                """

        return f"""
        <h2>ADMIN PANEL</h2>
        {user_list}
        <br>
        <a href='/logout'>Logout</a>
        """

    return f"""
    <h1>Xin chào {username}</h1>
    <h2>Role: {role}</h2>
    <a href='/logout'>Logout</a>
    """

# ================= LOCK / UNLOCK =================
@app.route("/admin/lock/<username>")
def lock_user(username):
    if session.get("role") != "admin":
        return redirect("/")

    if username in users:
        users[username]["locked"] = True

    return redirect("/dashboard")

@app.route("/admin/unlock/<username>")
def unlock_user(username):
    if session.get("role") != "admin":
        return redirect("/")

    if username in users:
        users[username]["locked"] = False

    return redirect("/dashboard")

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ================= RUN =================
if __name__ == "__main__":
    socketio.run(app, debug=True)
