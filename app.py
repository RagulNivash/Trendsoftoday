from flask import Flask, render_template, flash, request, redirect, url_for, session
from forms import LoginForm, RegistrationForm
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import LoginManager, UserMixin
from flask_login import login_user, logout_user, current_user, login_required
from flask_dance.contrib.google import make_google_blueprint, google
from news import *


import os
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = '1'
os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = '1'
 

 
#create the object of Flask
app  = Flask(__name__)
 
app.config['SECRET_KEY'] = 'Secret Key'
 
blueprint = make_google_blueprint(
    client_id="240639012288-6nf6mpvdsbblc8dmt417b54ufcnm3eqk.apps.googleusercontent.com",
    client_secret="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",
    # reprompt_consent=True,
    offline=False,
    scope=["profile", "email"]
)
app.register_blueprint(blueprint, url_prefix="/login") 

#SqlAlchemy Database Configuration With Mysql
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:''@localhost/crud'

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://spdycygtnurafi:c3a7622b6147567e3decab2b5ad5f4324858f7d5bccb6bdb323e1775ce156c1f@ec2-52-21-207-163.compute-1.amazonaws.com:5432/d49t7177ug8vt3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
 
 
db = SQLAlchemy(app)
 
 
#login code
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'Login'
 
 
 
 
#This is our model
class UserInfo(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(100), unique = True)
    password = db.Column(db.String(100))
 
 
 
    def __init__(self, username, password):
        self.username = username
        self.password = password
 
 
 
 
@login_manager.user_loader
def load_user(user_id):
    return UserInfo.query.get(int(user_id))
 
 
 
 
#creating our routes
@app.route('/')
@login_required
def index():
 
    name = current_user.username
 
    return render_template('index.html', name = name)
 
 
 
#login route
@app.route('/login' , methods = ['GET', 'POST'])
def Login():
    form = LoginForm()
    
    if request.method == 'POST':
        if form.validate_on_submit():
            user = UserInfo.query.filter_by(username=form.username.data).first()
 
            if user:
                if check_password_hash(user.password, form.password.data):
                    login_user(user)
 
                    return redirect(url_for('index'))
 
 
                flash("Invalid Credentials")
 
    return render_template('login.html', form = form)
 
 
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('Login'))
 
 
 
#register route
@app.route('/register' , methods = ['GET', 'POST'])
def register():
    form = RegistrationForm()
 
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method = 'sha256')
        username = form.username.data
        password = hashed_password
 
 
        new_register =UserInfo(username=username, password=password)
 
        db.session.add(new_register)
 
        db.session.commit()
 
        flash("Registration was successfull, please login")
 
        return redirect(url_for('Login'))
 
 
    return render_template('registration.html', form=form)
 

#news

@app.route('/news/', methods = ['GET', 'POST'])
def news():
    if request.method == 'GET':
        news_list=fetch_top_news()
        

    elif request.method == 'POST':
        category =  request.form.get('category')
        print("category: %s"%category)
        if category != None:
            news_list=fetch_category_news(category)
        keyword = request.form.get('keyword')
        print("keyword: %s"%keyword)
        if keyword != None:
            news_list=fetch_news_search_topic(keyword)
        location = request.form.get('location')
        print("location: %s"%location)
        if location != None:
            news_list = fetch_location_news(location)    
        print(news_list)
    
    return render_template('index.html', newslist = news_list)
 
@app.route("/googlelogin")
def googlelogin():
    hashed_password = generate_password_hash("google", method = 'sha256')
    flag = 0
    if not google.authorized:
        flag = 1
        return render_template(url_for("google.login"))


    resp = google.get("/oauth2/v2/userinfo")
    assert resp.ok, resp.text
    email=resp.json()["email"]
    if flag != 1:
        try:
            new_register =UserInfo(username=email, password=hashed_password)
            db.session.add(new_register)
            db.session.commit() 
        except:
            print("existing user")
 

    return render_template("index.html",email=email)
 
 
 
#run flask app
if __name__ == "__main__":
    app.run(debug=True)