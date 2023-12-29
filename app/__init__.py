from flask import Flask, session, render_template, request, redirect
from datetime import datetime
import os
import html
import sqlite3
import bcrypt

app = Flask(__name__)
app.secret_key = os.urandom(32)
DB_FILE="database.db"
db = sqlite3.connect(DB_FILE, check_same_thread = False)
cursor = db.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users(UserID INTEGER NOT NULL PRIMARY KEY, Username text NOT NULL UNIQUE, Password text);')
cursor.execute('CREATE TABLE IF NOT EXISTS posts(PostID INTEGER NOT NULL PRIMARY KEY, UserID INTEGER NOT NULL, Title text NOT NULL, Text text, Date text, Likes INTEGER NOT NULL);')
db.commit()

@app.route("/")
def index():
    if 'username' in session and 'userID' in session:
        return redirect("/dashboard")
    else:
        return redirect("/login")

@app.route("/dashboard")
def render_dashboard():
    if 'username' in session and 'userID' in session:
        posts = get_posts()[-9:][::-1]
        truncated_posts = []
        for post in posts:
            truncated_text = post[3][:200] + "..." if len(post[3]) > 200 else post[3] # 200 character limit 
            truncated_post = post[:3] + (truncated_text,) + post[4:]
            truncated_posts.append(truncated_post)
        return render_template("dashboard.html", user = session['username'], logged_in = True, posts = truncated_posts)
    else:
        return redirect("/login")

@app.route("/login")
def render_login():
    if'username' in session and 'userID' in session:
        return render_template("dashboard.html", user = session['username'])    
    return render_template("login.html")

@app.route("/registration")
def render_registration():
    if'username' in session and 'userID' in session:
        return redirect("/dashboard")
    return render_template("register.html")

@app.route("/authenticate", methods=['POST'])
def login():
    if not request.form.get('username') or not request.form.get('password'):
        return render_template("error.html")
    else:
        cursor = db.cursor()
        cursor.execute('SELECT UserID, password FROM users WHERE Username=?', (request.form.get('username'),))
        data = cursor.fetchone()
        if data and bcrypt.checkpw(request.form.get('password').encode('utf-8'), data[1]):
            session['username'] = request.form.get('username')
            session['userID'] = int(data[0])
            return redirect("/dashboard")
        else:
            return render_template("error.html")

@app.route("/register", methods=['POST']) 
def register():
    if not request.form.get('username') or not request.form.get('password'):
        return render_template("error.html")
    else:
        cursor = db.cursor()
        cursor.execute('SELECT UserID FROM users WHERE Username=?', (request.form.get('username'),))
        data = cursor.fetchone()
        if data:
            return render_template("error.html")
        else:
            hashed_password = bcrypt.hashpw(request.form.get('password').encode('utf-8') , bcrypt.gensalt(rounds=12))
            parameters = (request.form.get('username'), hashed_password,)
            cursor.execute('INSERT INTO users(Username, Password) VALUES(?,?)', parameters)
            db.commit()
            return redirect("/login")
        
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/new_post", methods=['POST'])
def new_post():
    if not request.form.get('title'):
        return render_template("error.html")
    else:
        cursor = db.cursor()
        title = html.escape(request.form.get('title'))
        if request.form.get('text'):
            text = html.escape(request.form.get('text'))
        else:
            text = ""
        date = datetime.now()
        parameters = (session['userID'], title, text, date, 0,)
        cursor.execute('INSERT INTO posts(UserID, Title, Text, Date, Likes) VALUES(?,?,?,?,?)', parameters)
        db.commit()
        return redirect(f"/post/{cursor.lastrowid}")

@app.route("/post/<postid>", methods=['GET'])
def get_post(postid):
    cursor = db.cursor()
    cursor.execute('SELECT UserID, Title, Text, Date, Likes FROM posts WHERE PostID=?', (postid,))
    data = cursor.fetchone()
    if data:
        cursor.execute('SELECT Username FROM users WHERE UserID=?', (data[0],))
        username = cursor.fetchone()
        return render_template("post.html", post_id = postid, author=username[0], title=data[1], text=data[2], date=data[3], likes=data[4], logged_in = True)
    else:
        return render_template("error.html")
    
@app.route("/get_posts")
def get_posts():
    cursor = db.cursor()
    cursor.execute('SELECT * FROM posts')
    data = cursor.fetchall()
    if data:
        for i in range(len(data)):
            cursor.execute('SELECT Username FROM users WHERE UserID=?', (data[i][1],))
            data[i] += cursor.fetchone() # Author is always final value
        return data
    else:
        return []
    
@app.route("/feed")
def render_feed():
    return render_template("feed.html", logged_in = True, posts = get_posts())

if __name__ == "__main__":
    app.run()
