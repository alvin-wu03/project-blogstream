from flask import Flask, session, render_template, request, redirect, url_for
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
cursor.execute('CREATE TABLE IF NOT EXISTS users(UserID INTEGER NOT NULL PRIMARY KEY, Username text NOT NULL UNIQUE, Password text, About text, JoinDate text);')
cursor.execute('CREATE TABLE IF NOT EXISTS posts(PostID INTEGER NOT NULL PRIMARY KEY, UserID INTEGER NOT NULL, Title text NOT NULL, Text text, Date text, Likes INTEGER NOT NULL);')
cursor.execute('CREATE TABLE IF NOT EXISTS comments(CommentID INTEGER NOT NULL PRIMARY KEY, PostID INTEGER NOT NULL, UserID INTEGER NOT NULL, Text text, Date text);')
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
        posts = get_posts()[:9]
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
            parameters = (request.form.get('username'), hashed_password, "", datetime.now())
            cursor.execute('INSERT INTO users(Username, Password, About, JoinDate) VALUES(?,?,?,?)', parameters)
            db.commit()
            return redirect("/login")
        
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/new_post", methods=['POST'])
def new_post():
    if not request.form.get('title') or 'userID' not in session or 'username' not in session:
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
    
@app.route("/edit_post", methods=['POST'])
def edit_post():
    post_id = request.form.get('post_id')
    user_id = request.form.get('user_id')
    if not request.form.get('title') or post_id == None or user_id == None or not 'userID' in session or int(session['userID']) != int(user_id):
        return render_template("error.html")
    else:
        cursor = db.cursor()
        title = html.escape(request.form.get('title'))
        if request.form.get('text'):
            text = html.escape(request.form.get('text'))
        else:
            text = ""
        date = datetime.now()
        parameters = (title, text, date, post_id, session['userID'])
        cursor.execute('UPDATE posts SET Title=?, Text=?, Date=? WHERE PostID=? AND UserID=?', parameters)
        db.commit()
        return redirect(f"/post/{post_id}")
    
@app.route("/delete_post", methods=['POST'])
def delete_post():
    post_id = request.form.get('post_id')
    user_id = request.form.get('user_id')
    if post_id == None or user_id == None or not 'userID' in session or int(session['userID']) != int(user_id):
        return render_template("error.html")
    else:
        cursor = db.cursor()
        parameters = (post_id, user_id)
        cursor.execute('DELETE FROM posts WHERE PostID=? AND UserID=?', parameters)
        db.commit()
        return redirect("/dashboard")

@app.route("/comment", methods=['POST'])
def comment_post():
    post_id = request.form.get('post_id')
    user_id = request.form.get('user_id')
    if not request.form.get('comment_text') or post_id == None or user_id == None or not 'userID' in session:
        return render_template("error.html")
    else:
        cursor = db.cursor()
        comment_text = html.escape(request.form.get('comment_text'))
        date = datetime.now()
        parameters = (post_id, session['userID'], comment_text, date)
        cursor.execute('INSERT INTO comments(PostID, UserID, Text, Date) VALUES(?,?,?,?)', parameters)
        db.commit()
        return redirect(f"/post/{post_id}")

@app.route("/post/<postid>", methods=['GET'])
def get_post(postid):
    if 'username' in session and 'userID' in session:
        cursor = db.cursor()
        cursor.execute('SELECT UserID, Title, Text, Date, Likes FROM posts WHERE PostID=?', (postid,))
        data = cursor.fetchone()
        cursor.execute('SELECT * FROM comments WHERE PostID=?', (postid,))
        comments = cursor.fetchall()
        if data:
            cursor.execute('SELECT Username FROM users WHERE UserID=?', (data[0],))
            userData = cursor.fetchone()
            for i in range(len(comments)):
                user_id = comments[i][1]  # Assuming UserID is at index 2 in comments tuple
                cursor.execute('SELECT Username FROM users WHERE UserID=?', (user_id,))
                result = cursor.fetchone()
                if result:
                    print(result)
                    username = result[0]  # Assuming Username is the first column in users table
                    comment_author = username
                    # Append the username to each comment
                    comments[i] = (comments[i], comment_author)
            #print(comments)
            return render_template("post.html", post_id = postid, user_id = data[0], author=userData[0], title=data[1], text=data[2], date=data[3], likes=data[4], comments = comments, logged_in = True)
        else:
            return render_template("error.html")
    else:
        return redirect("/login")
    
@app.route("/get_posts")
def get_posts():
    cursor = db.cursor()
    cursor.execute('SELECT p.*, u.Username FROM posts p JOIN users u ON p.UserID = u.UserID ORDER BY Date DESC')
    data = cursor.fetchall()
    if data:
        return data
    else:
        return []
    
@app.route("/feed")
def render_feed():
    if 'username' in session and 'userID' in session:
        return render_template("feed.html", logged_in = True, posts = get_posts())
    else:
        return redirect("/login")

@app.route("/user/<userid>", methods=['GET'])
def get_user(userid):
    if 'username' in session and 'userID' in session:
        cursor = db.cursor()
        cursor.execute('SELECT Username, JoinDate FROM users WHERE UserID=?', (userid,))
        userData = cursor.fetchone()
        if userData and 'userID' in session:
            username = userData[0]
            join_date = userData[1]
            cursor.execute('SELECT * FROM posts WHERE UserID=?', (userid,))
            posts = cursor.fetchall()
            return render_template("user_profile.html", userid = userid, username = username, join_date = join_date, posts = posts[-5:][::-1], logged_in="True")
        else:
            return render_template("error.html")
    return redirect("/login")

@app.route("/user/<userid>/posts", methods=['GET'])
def get_user_posts(userid):
    if 'username' in session and 'userID' in session:
        cursor = db.cursor()
        cursor.execute('SELECT Username FROM users WHERE UserID=?', (userid,))
        userData = cursor.fetchone()
        if userData and 'userID' in session:
            username = userData[0]
            cursor.execute('SELECT * FROM posts WHERE UserID=?', (userid,))
            posts = cursor.fetchall()
            return render_template("user_posts.html", username = username, posts = posts[::-1], logged_in="True")
        else:
            return render_template("error.html")
    else:
        return redirect("/login")    

@app.route("/self")    
def get_self():
    if 'userID' in session:
        user_id = session['userID']
        return redirect(url_for('get_user', userid=user_id))
    else:
        # Handle the case when user_id is not in the session
        return render_template("error.html")

if __name__ == "__main__":
    app.run()
