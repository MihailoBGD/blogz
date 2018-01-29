from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:lozinka@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'secretkey'


class Blog(db.Model):

    #next 3 lines are the db columns
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    text = db.Column(db.String(600))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, text, owner):
        self.title = title
        self.text = text
        self.owner = owner 

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique = True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password 

@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'index', 'blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')



@app.route("/") #TODO create a page that shows all of the users
def index():
    return redirect("/blog")

@app.route('/blog')
def blog():
    if request.args.get('id'):
        blog_id = request.args.get('id')
        blog = Blog.query.filter_by(id = blog_id).first()
        return render_template('single-blog.html', title = "build-a-blog", blog = blog )


    blogs = Blog.query.all()
    
    #blogs = [blogObj1, blogObj2, blogObj3]
    
    return render_template('blog-main.html',
                            title="Build-a-blog",
                            blogs = blogs)
                            
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        #todo validate
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/')
        else: 
            return "<h1>Duplicate user</h1>"
    return render_template('register.html')


@app.route('/newpost', methods=['POST', 'GET'])
def new_blog_entry():
    if request.method == 'POST':
        title_error = ""
        text_error = ""

        blog_title = request.form['title']
        blog_text = request.form['text']
        if not blog_title:
            title_error = "title field requires text sir"
        if not blog_text:
            text_error = "text field requires text sir"
        if title_error or text_error:
            return render_template('new-blog-entry.html',
                                    title_error = title_error, 
                                    text_error = text_error)

        user = User.query.filter_by(username=session['username']).first()
        blog = Blog(blog_title, blog_text, user)
        db.session.add(blog)
        db.session.commit()
        #return redirect(\"blog?id=\" + str(blog.id)
        return redirect("/blog?id={id}".format(id = blog.id))

    return render_template('new-blog-entry.html',title="Add-a-blog")

@app.route('/index')
def allblogs():
    users = User.query.all()
    return render_template('/index.html',users = users)

@app.route('/singleuser', methods=['POST', 'GET'])
def single_user():
    #Get a user object from the DB, based on their username
    user_id = request.args.get('id')
    if user_id != None:
        user = User.query.get(user_id)
        blogs = Blog.query.filter_by(owner_id=user_id).all()
        return render_template('/singleuser.html', blogs = blogs,user=user)
    return redirect('/index')

@app.route('/logout')
def logout():
    del session['username']
    return redirect ('/')

if __name__ == '__main__':
    app.run()




