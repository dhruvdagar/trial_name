from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, Table, Column, Integer, ForeignKey
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from webforms import UserForm, LoginForm, NamerForm, PostForm, PasswordForm, SearchForm
from flask_ckeditor import CKEditor

app = Flask(__name__)

ckeditor = CKEditor(app)
app.config['SECRET_KEY'] = "My secret key"
# app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///users.db"

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:mypassword123@localhost/blog_users"

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# flask login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


# TABLES

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    # author = db.Column(db.String(200))
    content = db.Column(db.Text(2000))
    slug = db.Column(db.String(200))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    # foreign key to link users
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return '<Name %r>' % self.title


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    fv_color = db.Column(db.String(200))
    # password
    pass_hash = db.Column(db.String(120))
    # user can have many posts
    posts = db.relationship('BlogPost', backref='poster')

    @property
    def password(self):
        raise AttributeError("Not Readable")

    @password.setter
    def password(self, password):
        self.pass_hash = generate_password_hash(password)

    def verify_pass(self, password):
        return check_password_hash(self.pass_hash, password)

    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Name %r>' % self.name


# with app.app_context():
#     db.create_all()


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/admin')
@login_required
def admin():
    id = current_user.id
    if id == 1 or id == 4:
        return render_template("admin.html")
    else:
        flash("Access Denied")
        return redirect(url_for('dashboard'))


@app.context_processor
def base():
    form = SearchForm()
    dhruv = "Hey hey hey"
    return dict(form=form, dhruv=dhruv)


@app.route('/search', methods=['POST'])
def search():
    form = SearchForm()
    posts = BlogPost.query
    if form.validate_on_submit():
        searched_for = form.searched_for.data
        # query the database
        posts = posts.filter(BlogPost.content.like("%" + searched_for + "%"))
        posts = posts.order_by(BlogPost.title).all()
        return render_template("search.html", form=form, searched_for=searched_for, posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(user_name=form.username.data).first()
        if user:
            if check_password_hash(user.pass_hash, form.password.data):
                login_user(user)
                flash('Login Successful')
                return redirect(url_for('dashboard'))

            else:
                flash('Wrong Password')
        else:
            flash('User Does Not Exist')

    return render_template("login.html", form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('You have been Logout')
    return redirect(url_for('login'))


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template("dashboard.html")


@app.route('/view_posts')
def view_posts():
    # Grabbing Posts
    posts = BlogPost.query.order_by(BlogPost.date_posted)
    return render_template("posts.html", posts=posts)


@app.route('/indv_post/<int:id>')
def indv_post(id):
    post = BlogPost.query.get_or_404(id)
    return render_template("indv_post.html", post=post)


@app.route('/indv_post/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = BlogPost.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        # post.author = form.author.data
        post.slug = form.slug.data
        # Update Database
        db.session.add(post)
        db.session.commit()
        flash("POST Updated")
        return redirect(url_for('indv_post', id=post.id))
    # adds(prints) data to form
    if current_user.id == post.poster_id:
        form.title.data = post.title
        form.content.data = post.content
        # form.author.data = post.author
        form.slug.data = post.slug
        return render_template("edit_post.html", form=form, post=post)
    else:
        flash("Not Authorised")
        posts = BlogPost.query.order_by(BlogPost.date_posted)
        return render_template("posts.html", posts=posts)


@app.route('/indv_post/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = BlogPost.query.get_or_404(id)
    id = current_user.id
    if id == post_to_delete.poster.id:
        try:
            db.session.delete(post_to_delete)
            db.session.commit()
            flash("POST Deleted")
            posts = BlogPost.query.order_by(BlogPost.date_posted)
            return render_template("posts.html", posts=posts)
        except:
            flash("There was an error")
            posts = BlogPost.query.order_by(BlogPost.date_posted)
            return render_template("posts.html", posts=posts)
    else:
        flash("Not Authorised")
        posts = BlogPost.query.order_by(BlogPost.date_posted)
        return render_template("posts.html", posts=posts)


@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        poster = current_user.id
        post = BlogPost(title=form.title.data,
                        content=form.content.data,
                        poster_id=poster,
                        slug=form.slug.data)

        form.title.data = ''
        # form.author.data = ''
        form.slug.data = ''
        form.content.data = ''

        db.session.add(post)
        db.session.commit()

        flash("BLOG SUBMITTED")

    return render_template("add_post.html", form=form)


@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = NamerForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Form Submitted Successfully")
    return render_template("name.html", name=name, form=form)


@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
    email = None
    password = None
    user_to_check = None
    passed = None
    form = PasswordForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        form.email.data = ''
        form.password_hash.data = ''

        user_to_check = Users.query.filter_by(email=email).first()
        passed = check_password_hash(user_to_check.pass_hash, password)
    return render_template("test_pw.html",
                           email=email, form=form, password=password, user_to_check=user_to_check, passed=passed)


@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # hashing
            hash_the_pass = generate_password_hash(form.pass_hash.data)
            user = Users(name=form.name.data,
                         user_name=form.user_name.data,
                         email=form.email.data,
                         fv_color=form.fv_color.data,
                         pass_hash=hash_the_pass
                         )
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.user_name.data = ''
        form.email.data = ''
        form.fv_color.data = ''
        form.pass_hash.data = ''
        flash("User Added Successfully")
    our_users = Users.query.order_by(Users.date_added)
    return render_template("add_user.html", form=form, name=name, our_users=our_users)


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form["name"]
        name_to_update.email = request.form["email"]
        name_to_update.fv_color = request.form["fv_color"]
        name_to_update.user_name = request.form["user_name"]
        try:
            name_to_update.verified = True
            db.session.commit()
            flash("User updated")
            # return render_template("update.html", name_to_update=name_to_update, form=form, id=id)
            return redirect(url_for("dashboard", name_to_update=name_to_update, form=form, id=id))
        except:
            flash("Error")
            # return render_template("update.html", name_to_update=name_to_update, form=form, id=id)
            return redirect(url_for("dashboard", name_to_update=name_to_update, form=form, id=id))

    else:
        pass
        # return render_template("update.html", name_to_update=name_to_update, form=form, id=id)
        # return redirect(url_for("dashboard", name_to_update=name_to_update, form=form, id=id))

    return render_template("update.html", name_to_update=name_to_update, form=form, id=id)


@app.route('/delete/<int:id>')
def delete(id):
    name = None
    form = UserForm()
    user_to_delete = Users.query.get_or_404(id)
    our_users = Users.query.order_by(Users.date_added)

    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User Deleted")
        return render_template("add_user.html", form=form, name=name, our_users=our_users)
    except:
        flash("Error")
        return render_template("add_user.html", form=form, name=name, our_users=our_users)


@app.errorhandler(404)
def page_not_find(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def page_not_find(e):
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(debug=True)
