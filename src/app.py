import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, abort

#----------------------------------------

app = Flask(__name__)
app.config['SECRET_KEY'] = 'abcd'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

#----------------------------------------


def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post

#----------------------------------------


@app.route('/', methods=('GET', 'POST'))
@app.route('/index/', methods=('GET', 'POST'))
def index():
    conn = get_db_connection()
    if request.method == 'GET':
        cursel = 'id'
        curorder = 'DESC'
    elif request.method == 'POST':
        cursel = request.form.get('sort_select')
        curorder = request.form.get('order_select')
        # curorder = request.form.get('check_order')
        if cursel is None: cursel = 'id'
        if curorder is None: curorder = 'DESC'
        # elif curorder == '': curorder = 'ASC'
    posts_table = conn.execute(f"SELECT * FROM posts ORDER BY {cursel} {curorder}").fetchall()
    col_lst = conn.execute("SELECT * FROM posts")
    col_names = [desc[0] for desc in col_lst.description]
    order_dic = {"ASC": "Ascendant", "DESC": "Descendant", }
    conn.close()
    return render_template('index.html', posts=posts_table, 
                           col_names=col_names, cursel=cursel, 
                           curorder=curorder, order_name=order_dic[curorder])

#----------------------------------------


@app.route('/about/')
def about():
    return render_template('about.html')

#----------------------------------------


@app.route('/create/', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        author = request.form['author']
        title = request.form['title']
        content = request.form['content']

        if not author:
            flash('Error: Author is required!')
        elif not title:
            flash('Error: Title is required!')
        elif not content:
            flash('Error: Content is required!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO posts (author, title, content) VALUES (?, ?, ?)',
                         (author, title, content))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('create.html')

#----------------------------------------


@app.route('/<int:id>/edit/', methods=('GET', 'POST'))
def edit(id):
    post = get_post(id)

    if request.method == 'POST':
        author = request.form['author']
        title = request.form['title']
        content = request.form['content']

        if not author:
            flash('Error: Author is required!')

        if not title:
            flash('Error: Title is required!')

        elif not content:
            flash('Error: Content is required!')

        else:
            conn = get_db_connection()
            conn.execute('UPDATE posts SET author = ?, title = ?, content = ?'
                         ' WHERE id = ?',
                         (author, title, content, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('edit.html', post=post)

#----------------------------------------

@app.route('/<int:id>/delete/', methods=('POST',))
def delete(id):
    post = get_post(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('index'))

#----------------------------------------


@app.route("/sorted", methods=['GET', 'POST'])
def sorted():
    cursel = request.form.get('sort_select')
    # return(str(sel)) # just to see what select is
    conn = get_db_connection()
    posts_table = conn.execute(f"SELECT * FROM posts ORDER BY {cursel} DESC").fetchall()
    cursor = conn.execute("SELECT * FROM posts")
    col_names = [desc[0] for desc in cursor.description]
    conn.close()
    return render_template('index.html', posts=posts_table, col_names=col_names, cursel=cursel)

#----------------------------------------


@app.route("/test", methods=['GET', 'POST'])
def test():
    sel = request.form.get('sort_select')
    # return(str(sel)) # just to see what select is
    conn = get_db_connection()
    posts_table = conn.execute(f"SELECT * FROM posts ORDER BY {sel} DESC").fetchall()
    cursor = conn.execute("SELECT * FROM posts")
    col_names = [desc[0] for desc in cursor.description]
    conn.close()
    return render_template('index.html', posts=posts_table, col_names=col_names)

#----------------------------------------


if __name__ == "__main__":
    app.run(host='127.0.0.1:5000', debug=True)

#----------------------------------------
