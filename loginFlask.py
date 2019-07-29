from flask import Flask, Response, redirect, url_for, request, session, abort, render_template
from flask_login import LoginManager, UserMixin, \
                                login_required, login_user, logout_user 
import logging
import sys
import requests
import json

app = Flask(__name__)
app.debug = True

# config
app.config.update(
    DEBUG = True,
    SECRET_KEY = 'secret_xxx'
)

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login" #Whenever the user needs to login, it will look for the app.route with /login


# silly user model
class User(UserMixin):

    def __init__(self, name, id, active=True):
        self.name = str(name)
        self.id = str(id)
        self.active = active
       

        
    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.password)



# some protected url
@app.route('/index', methods=["GET", "POST"])
@app.route('/', methods=["GET", "POST"])
@login_required
def index():
    return render_template("mainPage.html")

 
# somewhere to login
@app.route("/login", methods=["GET", "POST"])
def login():

    #Would add a "register" button in this form that redirects to a @app.route('/register') with the same type of form but instead just enters data into
    #Newslens. Then redirect to /login and allow user to use that info.
    return render_template('master.html') 

# somewhere to login
@app.route("/authenticateUser/<credentials>", methods=["GET", "POST"])
def authenticateUser(credentials):
    usr = credentials.split("   ")[0]
    psw = credentials.split("   ")[1]

    authenticatedUser = False
    print("Authenticating user")

    authenticatedUser = authenticated(usr, psw) #Checks if valid username and password

    #AUTHENTICATE USR HERE
    if(authenticatedUser): #if the username & password are a key value pair in the api
        user = User(usr, usr) #creates a user
        login_user(user) #Logs them in, flask makes a session 

        print("USER Logged in")
        return redirect(request.args.get("next") or url_for("index"))

    
    else:
        print("Cannot log in")
        return "Incorrect Credentials"

def authenticated(usr, psw):
    try:
        data_reloaded = requests.get("https://newslens.berkeley.edu/api/ruchir/load/allLogins").json()
        sys.stdout.write("Just retrieved all logins " +str(data_reloaded))
        loginValues = data_reloaded

        print("Authenticating step 3")

        if {usr: psw} in loginValues:
            print("Authenticated " +usr)
            return True
        else:
            print("Doesnt exist")
    except:
        print("Couldn't retrieve history")
        return False
    return False

@app.route("/registerUser/<credentials>", methods=["GET", "POST"])
def registerUser(credentials):
    exists = False
    usr = credentials.split("   ")[0]
    psw = credentials.split("   ")[1]

    userExists = exist(usr, psw)
    listOfLogins = []

    #AUTHENTICATE USR HERE
    if(userExists is False): #if the username & password are a key value pair in the api
        
        try:
            save_res =  requests.get("https://newslens.berkeley.edu/api/ruchir/load/allLogins").json()
            listOfLogins = save_res
            listOfLogins.append({usr: psw})
        except ValueError:
            listOfLogins.append({usr: psw})
        url = "https://newslens.berkeley.edu/api/ruchir/save/allLogins"
        print("PRINTING " +str(listOfLogins))
        save_res = requests.post(url, data=json.dumps(listOfLogins))

        user = User(usr, usr)
        login_user(user)
        return redirect(url_for('home'))
    else:
        return abort(401)

def exist(usr, psw):
    try:
        data_reloaded = requests.get("https://newslens.berkeley.edu/api/ruchir/load/allLogins").json()
        sys.stdout.write("Just retrieved all logins " +str(data_reloaded))
        loginValues = data_reloaded


        for x in range(len(loginValues)):
            sys.stdout.write("Checking " +str(x))
            if usr in loginValues[x]:
                sys.stdout.write("Username already exists " +usr)
                return True
    except:
        sys.stdout.write("Couldn't retrieve history")
        return False
    return False

# somewhere to logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return Response('<p>Logged out</p>')


# handle login failed
@app.errorhandler(401)
def page_not_found(e):
    return Response('<p>Login failed</p>')
    
    
# callback to reload the user object        
@login_manager.user_loader
def load_user(usr):
    return User(usr, usr)
    

if __name__ == "__main__":
    app.run()