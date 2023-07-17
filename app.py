from flask import Flask,session,render_template,redirect,url_for,flash,abort,request
from flask_bootstrap import Bootstrap
from flask_mysqldb import MySQL
import yaml

# db = yaml.load('db.yaml')
with open("db.yaml", "r") as yaml_file:
    db = yaml.safe_load(yaml_file)

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret-key"
app.config["MYSQL_HOST"] = db["mysql_host"]
app.config["MYSQL_USER"] = db["mysql_user"]
app.config["MYSQL_PASSWORD"] = db["mysql_password"]
app.config["MYSQL_DB"] = db["mysql_db"]
app.config["MYSQL_PORT"] = db["mysql_port"]
app.config["MYSQL_CURSORCLASS"] = "DictCursor"
mysql = MySQL(app)
Bootstrap(app)


# Create the user table
def create_user_table():
    with app.app_context():
        cur = mysql.connection.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY, 
                email VARCHAR(255) NOT NULL, 
                username VARCHAR(255) NOT NULL, 
                firstname VARCHAR(255) NOT NULL, 
                lastname VARCHAR(255) NOT NULL, 
                password VARCHAR(255) NOT NULL
            )
            """
        )
        mysql.connection.commit()
        cur.close()


# Create the posts table
def create_posts_table():
    with app.app_context():
        cur = mysql.connection.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS posts (
                id INT AUTO_INCREMENT PRIMARY KEY, 
                user_id INT NOT NULL, 
                content TEXT NOT NULL, 
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        mysql.connection.commit()
        cur.close()


# Create the comments table
def create_comments_table():
    with app.app_context():
        cur = mysql.connection.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS comments (
                id INT AUTO_INCREMENT PRIMARY KEY, 
                post_id INT NOT NULL, 
                user_id INT NOT NULL, 
                content TEXT NOT NULL, 
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE, 
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        mysql.connection.commit()
        cur.close()


# Create the likes table
def create_likes_table():
    with app.app_context():
        cur = mysql.connection.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS likes (
                id INT AUTO_INCREMENT PRIMARY KEY, 
                post_id INT NOT NULL, 
                user_id INT NOT NULL, 
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE, 
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        mysql.connection.commit()
        cur.close()

        
# Create the notes table
def create_notes_table():
    with app.app_context():
        cur = mysql.connection.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            title VARCHAR(255),
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """)
        mysql.connection.commit()
        cur.close()



# Custom function to execute a query and fetch all results
def execute_query(query, params=None, many=True):
    with app.app_context():
        cur = mysql.connection.cursor()
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        if many == True:
            result = cur.fetchall()
        else:
            result = cur.fetchone()
        cur.close()
        return result


# Custom function to execute an insert query
def execute_insert(query, params):
    with app.app_context():
        cur = mysql.connection.cursor()
        cur.execute(query, params)
        mysql.connection.commit()
        cur.close()


# Add a user record
def add_user_data(email, username, firstname, lastname, password):
    query = "INSERT INTO users (email, username, firstname, lastname, password) VALUES (%s, %s, %s, %s, %s)"
    execute_insert(query, (email, username, firstname, lastname, password))


# Add a post record
def add_post(user_id, content):
    query = "INSERT INTO posts (user_id, content) VALUES (%s, %s)"
    execute_insert(query, (user_id, content))


# Update a post record
def update_post(post_id, content):
    query = "UPDATE posts SET content = %s WHERE id = %s"
    execute_insert(query, (content, post_id))


# Delete a post record
def delete_post(post_id):
    query = "DELETE FROM posts WHERE id = %s"
    execute_insert(query, (post_id,))


# Add a comment record
def add_comment(post_id, user_id, content):
    query = "INSERT INTO comments (post_id, user_id, content) VALUES (%s, %s, %s)"
    execute_insert(query, (post_id, user_id, content))


# Add a like record
def add_like(post_id, user_id):
    query = "INSERT INTO likes (post_id, user_id) VALUES (%s, %s)"
    execute_insert(query, (post_id, user_id))



# View all posts
def view_posts():
    query = "SELECT * FROM posts"
    posts = execute_query(query)
    return posts


# View a post by ID
def view_post(post_id):
    query = "SELECT * FROM posts WHERE id = %s"
    post = execute_query(query, (post_id,),many=False)
    return post


# Get the number of likes for a post
def get_like_count(post_id):
    query = "SELECT COUNT(*) AS count FROM likes WHERE post_id = %s"
    result = execute_query(query, (post_id,))
    return result[0]['count']

# Get the comments for a post
def get_comments(post_id):
    query = "SELECT * FROM comments WHERE post_id = %s"
    comments = execute_query(query, (post_id,))
    return comments

# Check if a post is liked by a user
def is_post_liked(post_id, user_id):
    if user_id:
        query = "SELECT * FROM likes WHERE post_id = %s AND user_id = %s"
        result = execute_query(query, (post_id, user_id))
        return len(result) > 0
    return False


# Get the user ID based on the username
def get_user_id(username):
    query = "SELECT id FROM users WHERE username = %s"
    result = execute_query(query, (username,))
    if result:
        return result[0]['id']
    return None



# Add a note
def add_note(user_id, title, content):
    query = "INSERT INTO notes (user_id, title, content) VALUES (%s, %s, %s)"
    execute_insert(query, (user_id, title, content))

# Update a note
def update_note(note_id, title, content):
    query = "UPDATE notes SET title = %s, content = %s WHERE id = %s"
    execute_insert(query, (title, content, note_id))

# Delete a note
def delete_note_by_id(note_id):
    query = "DELETE FROM notes WHERE id = %s"
    execute_insert(query, (note_id,))

# Get all notes for a user
def get_notes_by_user_id(user_id):
    query = "SELECT * FROM notes WHERE user_id = %s"
    notes = execute_query(query, (user_id,))
    
    return notes

# Get a note by its ID
def get_note_by_id(note_id):
    query = "SELECT * FROM notes WHERE id = %s"
    note = execute_query(query, (note_id,),many=False)
    return note


# Get posts specific to a user
def get_user_posts(user_id):
    query = "SELECT * FROM posts WHERE user_id = %s"
    posts = execute_query(query, (user_id,))
    return posts


# Register functionality
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        username = request.form["username"]
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            return "Password and confirm password do not match"

        # Check if the username or email already exists
        query = "SELECT * FROM users WHERE username = %s OR email = %s"
        existing_user = execute_query(query, (username, email))

        if existing_user:
            return "Username or email already exists"

        # Insert the user into the users table
        add_user_data(email, username, firstname, lastname, password)
        return redirect("/login")

    return render_template("register.html")


# Login functionality
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        user = execute_query(query, (username, password),many=False)

        if user:
            session["username"] = user["username"]
            return redirect("/")
        else:
            return "Invalid username or password"

    return render_template("login.html")


# Logout functionality
@app.route("/logout")
def logout():
    session.pop('username')
    return redirect("/")



# View all posts
@app.route("/")
def view_all_posts():
    if 'username' not in session:
        return redirect('/login')
    logged_in_user_id = get_user_id(session['username'])


    posts = view_posts()
    post_data = []
    for post in posts:
        post_id = post['id']
        post['like_count'] = get_like_count(post_id)
        post['comments'] = get_comments(post_id)
        post['liked'] = is_post_liked(post_id, logged_in_user_id)

        post_data.append(post)

    return render_template('posts.html', posts=post_data)



@app.route("/user-posts")
def view_user_posts():
    if 'username' not in session:
        return redirect('/login')
    
    logged_in_user_id = get_user_id(session['username'])
    posts = get_user_posts(logged_in_user_id)
    post_data = []
    for post in posts:
        post_id = post['id']
        post['like_count'] = get_like_count(post_id)
        post['comments'] = get_comments(post_id)
        post['liked'] = is_post_liked(post_id, logged_in_user_id)

        post_data.append(post)

    return render_template('my-posts.html', posts=post_data)



# View a post
@app.route("/posts/<int:post_id>")
def view_single_post(post_id):
    if 'username' not in session:
        return redirect('/login')
    
    logged_in_user_id = get_user_id(session['username'])

    post = view_post(post_id)
    post['like_count'] = get_like_count(post_id)
    post['comments'] = get_comments(post_id)
    post['liked'] = is_post_liked(post_id, logged_in_user_id)

    return render_template('post.html', post=post,logged_in_user_id=logged_in_user_id)


# Add a post
@app.route("/posts/add", methods=["GET", "POST"])
def add_post_view():
    if 'username' not in session:
        return redirect('/login')
    username = session['username']
    user_id = get_user_id(username)

    if request.method == "POST":
        content = request.form["content"]
        add_post(user_id, content)
        return redirect("/")

    return render_template("add_post.html")



# Update a post
@app.route("/posts/<int:post_id>/update", methods=["GET", "POST"])
def update_post_view(post_id):
    if 'username' not in session:
        return redirect('/login')
    post = view_post(post_id)


    if request.method == "POST":
        content = request.form["content"]

        update_post(post_id, content)
        return redirect("/")

    return render_template("update_post.html", post=post)


# Delete a post
@app.route("/posts/<int:post_id>/delete", methods=["POST"])
def delete_post_view(post_id):
    if 'username' not in session:
        return redirect('/login')
    delete_post(post_id)
    return redirect("/")



@app.route('/posts/<int:post_id>/like', methods=['POST'])
def add_like_view(post_id):
    if 'username' not in session:
        return redirect('/login')
    user_id = get_user_id(session['username'])
    add_like(post_id, user_id)
    return redirect(f'/posts/{post_id}')

# Add a comment
@app.route('/posts/<int:post_id>/comment', methods=['POST'])
def add_comment_view(post_id):
    if 'username' not in session:
        return redirect('/login')
    user_id = get_user_id(session['username'])
    content = request.form['content']
    add_comment(post_id, user_id, content)
    return redirect(f'/posts/{post_id}')


#Add a note
@app.route('/notes/add', methods=['GET', 'POST'])
def add_note_view():
    if 'username' not in session:
        return redirect('/login')
    
    if request.method == 'POST':
        user_id = get_user_id(session['username'])
        title = request.form['title']
        content = request.form['content']
        add_note(user_id, title, content)
        return redirect('/notes')

    return render_template('add_note.html')

# Update a note
@app.route('/notes/<int:note_id>/update', methods=['GET', 'POST'])
def update_note_view(note_id):
    if 'username' not in session:
        return redirect('/login')
    note = get_note_by_id(note_id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        update_note(note_id, title, content)
        return redirect('/notes')

    return render_template('update_note.html', note=note)

# Delete a note
@app.route('/notes/<int:note_id>/delete', methods=['POST'])
def delete_note(note_id):
    if 'username' not in session:
        return redirect('/login')
    delete_note_by_id(note_id)
    return redirect('/notes')

# View all notes
@app.route('/notes')
def view_all_notes():
    if 'username' not in session:
        return redirect('/login')
    user_id = get_user_id(session['username'])
    notes = get_notes_by_user_id(user_id)
    return render_template('notes.html', notes=notes)


@app.route('/notes/<int:note_id>')
def view_note(note_id):
    if 'username' not in session:
        return redirect('/login')
    note = get_note_by_id(note_id)
    if note:
        return render_template('view_note.html', note=note)
    else:
        return "Note not found"



if __name__ == "__main__":
    create_user_table()
    create_posts_table()
    create_comments_table()
    create_likes_table()
    create_notes_table()

    app.run(debug=True)
