import sqlite3
import json
from neptune.server import NServer
from neptune.response import JSONResponse, HTTPResponse, HTMLResponse


def init_db():
    try:
        cursor.execute("""
            CREATE TABLE blog (id INTEGER PRIMARY KEY AUTOINCREMENT,
                               title TEXT,
                               content TEXT);
        """)
        db_connection.commit()
    except:
        pass

def get_all_posts():
    post_data = db_connection.execute("""SELECT id, title, content FROM blog;""")
    posts = []
    for post in post_data:
        posts.append({
            'id': post[0],
            'title': post[1],
            'content': post[2],
            'url': '/post?id={}'.format(post[0])
        })

    return posts

def new_post(title, content):
    cursor.execute(""" 
        INSERT INTO blog (title, content) VALUES (?, ?)
    """, (title, content))
    db_connection.commit()

def get_post(pid):
    post_data = db_connection.execute("""SELECT id, title, content FROM blog WHERE id = {}""".format(pid))
    post_data = [i for i in post_data][0]
    return {'id': post_data[0], 'title': post_data[1], 'content': post_data[2]}


class Home(object):
    def get(self):
        return HTMLResponse("home.html", {'posts': get_all_posts()})

class Archive(object):
    def get(self):
            return HTMLResponse("archive.html", {'posts': get_all_posts()})

class NewPost(object):
    def post(self):
        data = self.request.request_data
        data = json.loads(data)
        new_post(data['title'], data['content'])
        return JSONResponse({"status": "OK",
                             "message": "New Post Successfully Added"})


class NewPostPage(object):
    def get(self):
        return HTMLResponse("new.html")


class GetPost(object):
    def get(self):
        pid = self.request.params['id']
        return HTMLResponse("blog.html", {'post': get_post(pid)})

app = NServer(port=5000)
app.router.add_rule('/', Home)
app.router.add_rule('/archive', Archive)
app.router.add_rule('/new', NewPost)
app.router.add_rule('/newpost', NewPostPage)
app.router.add_rule('/post', GetPost)


if __name__ == "__main__":
    db_connection = sqlite3.connect(".blog.db")
    cursor = db_connection.cursor()
    init_db()
    app.run()

