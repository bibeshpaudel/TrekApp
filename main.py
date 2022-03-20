from flask import Flask, jsonify, render_template, request, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from os import path, environ
from dotenv import load_dotenv

# for database

from flaskext.mysql import MySQL
from pymysql.err import IntegrityError

from flask_session import Session


import uuid


app = Flask(__name__)


basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))


SECRET_KEY = environ.get("SECRET_KEY") or "hard to guess string"
DEBUG = True
MYSQL_HOST = environ.get("MYSQL_HOST")
MYSQL_USER = environ.get("MYSQL_USER")
MYSQL_PASSWORD = environ.get("MYSQL_PASSWORD")
MYSQL_DB = environ.get("MYSQL_DB")

app.config["SECRET_KEY"] = SECRET_KEY
app.config["MYSQL_DATABASE_USER"] = MYSQL_USER
app.config["MYSQL_DATABASE_PASSWORD"] = MYSQL_PASSWORD
app.config["MYSQL_DATABASE_DB"] = MYSQL_DB

mysql = MySQL(app)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/")
def home():
    logged_in_user = None

    if session.get("email"):
        logged_in_user = session["email"]
    return render_template("index.html", result={"logged_in_user": logged_in_user})


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/doLogin", methods=["POST"])
def doLogin():
    email = request.form["email"]
    password = request.form["psw"]

    cursor = mysql.get_db().cursor()
    resp = cursor.execute(
        """SELECT id,email ,full_name FROM Users WHERE email=%s and password=%s;""",
        (email, password),
    )

    user = cursor.fetchone()
    cursor.close()
    if resp == 1:
        session["email"] = email
        session["userId"] = user[0]
        logged_in_user = session.get("email")
        return render_template("home.html", result={"logged_in_user": logged_in_user})
    else:
        return render_template("login.html", result="Invalid Credentials")


@app.route("/doRegister", methods=["POST"])
def doRegister():
    full_name = request.form["full_name"]
    email = request.form["email"]
    phone_number = request.form["phone_number"]
    address = request.form["address"]

    password = request.form["psw"]
    hashed_password = generate_password_hash(password)

    cursor = mysql.get_db().cursor()
    resp = cursor.execute(
        """INSERT INTO `Users` (`id`, `full_name`, `address`, `email`, `phone_number`, `password`) VALUES (NULL, %s, %s, %s, %s, %s);""",
        (full_name, address, email, phone_number, hashed_password),
    )

    mysql.get_db().commit()
    cursor.close()


    if resp == 1:
        return render_template("login.html")
    else:
        return render_template(
            "register.html", result="User not registered successfully"
        )




@app.route("/treks")
def allTreks():

    cursor = mysql.get_db().cursor()
    cursor.execute(
        """SELECT td.id as 'SNO', td.title as 'Title',
    td.days AS 'Days' , td.difficulty as 'Difficulty'
     ,td.total_cost as 'Total cost', td.upvotes as 'Upvotes', 
     u.full_name as 'Full name',u.id as 'userId' FROM `Trek_Destinations`
    as td JOIN Users as u ON td.user_id=u.id;"""
    )
    treks = cursor.fetchall()

    cursor.close()
    logged_in_user = None
    if session.get("email"):
        logged_in_user = session["email"]

    if session.get("userId"):
        userId = session.get("userId")
    return render_template(
        "listing.html",
        result={"treks": treks, "logged_in_user": logged_in_user, "userId": userId},
    )




@app.route("/trek/<int:trekId>")
def getTrekbyId(trekId):

    cursor = mysql.get_db().cursor()
    cursor.execute(
        """SELECT td.id as 'SNO', td.title as 'Title',
    td.days AS 'Days' , td.difficulty as 'Difficulty'
     ,td.total_cost as 'Total cost', td.upvotes as 'Upvotes', 
     u.full_name as 'Full name' FROM `Trek_Destinations`
    as td JOIN Users as u ON td.user_id=u.id where td.id=%s;""",
        (trekId,),
    )
    trek = cursor.fetchone()

    cursor.close()
    cursor = mysql.get_db().cursor()
    cursor.execute(
        """SELECT * FROM `Itineraries` WHERE `trek_destination_id`=%s;""", (trekId,)
    )
    Itineraries = cursor.fetchall()

    cursor.close()

    return render_template(
        "trekdetail.html", result={"trek": trek, "Itineraries": Itineraries}
    )


@app.route("/logout")
def logout():
    session["email"] = None
    session["userId"] = None

    return redirect("/")


@app.route("/addTrek")
def addTrek():
    if session.get("email"):
        logged_in_user = session["email"]

    return render_template("addtrek.html", result={"logged_in_user": logged_in_user})


@app.route("/doAddTrek", methods=["POST"])
def doAddTrek():
    logged_in_user = None

    if session.get("email"):
        logged_in_user = session["email"]

    title = request.form["title"]
    days = request.form["days"]
    difficulty = request.form["difficulty"]
    total_cost = request.form["total_cost"]
    upvotes = 0

    cursor = mysql.get_db().cursor()
    cursor.execute("""SELECT id FROM `Users` WHERE `email`=%s;""", (logged_in_user,))
    user = cursor.fetchone()
    cursor.close()
    userId = user[0]

    cursor = mysql.get_db().cursor()
    cursor.execute(
        """INSERT INTO `Trek_Destinations` VALUES (NULL, %s, %s, %s, %s, %s,%s);""",
        (title, days, difficulty, total_cost, upvotes, userId),
    )

    mysql.get_db().commit()
    cursor.close()

    return redirect("/treks")



@app.route("/editTrek/<int:trekId>")
def editTrek(trekId):
    logged_in_user = None
    if session.get("email"):
        logged_in_user = session["email"]

    cursor = mysql.get_db().cursor()
    cursor.execute(
        """SELECT td.id as 'SNO', td.title as 'Title',
    td.days AS 'Days' , td.difficulty as 'Difficulty'
     ,td.total_cost as 'Total cost', td.upvotes as 'Upvotes', 
     u.full_name as 'Full name' FROM `Trek_Destinations`
    as td JOIN Users as u ON td.user_id=u.id where td.id=%s;""",
        (trekId,),
    )
    trek = cursor.fetchone()
    cursor.close()

    return render_template(
        "editTrek.html", result={"trek": trek, "logged_in_user": logged_in_user}
    )


@app.route("/doUpdateTrek", methods=["POST"])
def doUpdateTrek():
    logged_in_user = None

    if session.get("email"):
        logged_in_user = session["email"]

    title = request.form["title"]
    days = request.form["days"]
    difficulty = request.form["difficulty"]
    total_cost = request.form["total_cost"]
    trekId = request.form["trekId"]

    cursor = mysql.get_db().cursor()
    cursor.execute(
        """UPDATE `Trek_Destinations` SET `title`=%s,`days`=%s,`difficulty`=%s,`total_cost`=%s WHERE`id`=%s;""",
        (title, days, difficulty, total_cost, trekId),
    )

    mysql.get_db().commit()
    cursor.close()

    return redirect("/treks")




@app.route("/doDeleteTrek/<int:trekId>")
def doDelete(trekId):
    cursor = mysql.get_db().cursor()
    cursor.execute("""DELETE from `Trek_Destinations` WHERE `id`=%s;""", (trekId,))
    mysql.get_db().commit()
    cursor.close()

    return redirect("/treks")


@app.route("/addIternary")
def addIternary():
    logged_in_user = None
    if session.get("email"):
        logged_in_user = session["email"]
    cursor = mysql.get_db().cursor()
    userId = None
    if session.get("userId"):
        userId = session.get("userId")

    cursor.execute(
        """SELECT id,title from `Trek_Destinations` where user_id=%s ;""", (userId,)
    )
    treks = cursor.fetchall()

    cursor.close()

    return render_template(
        "addIternary.html", result={"treks": treks, "logged_in_user": logged_in_user}
    )


@app.route("/doAddIternary", methods=["POST"])
def doAddIternary():
    logged_in_user = None

    if session.get("email"):
        logged_in_user = session["email"]

    title = request.form["title"]
    day = request.form["day"]
    start_place = request.form["start_place"]
    end_place = request.form["end_place"]
    description = request.form["description"]
    duration = request.form["duration"]
    cost = request.form["cost"]
    trek_destination_id = request.form["trek_destination_id"]

    cursor = mysql.get_db().cursor()
    cursor.execute(
        """INSERT INTO `Itineraries` VALUES (NULL,%s, %s, %s, %s, %s,%s,%s,%s)""",
        (
            title,
            day,
            start_place,
            end_place,
            description,
            duration,
            cost,
            trek_destination_id,
        ),
    )

    mysql.get_db().commit()
    cursor.close()

    return redirect("/treks")


@app.route("/iternary/<int:trekId>")
def getIternaryByTrekId(trekId):

    cursor = mysql.get_db().cursor()
    cursor.execute(
        """SELECT * FROM `Itineraries` WHERE `trek_destination_id`=%s;""", (trekId,)
    )
    itineraries = cursor.fetchall()

    print(itineraries)
    cursor.close()

    return render_template(
        "iternary.html", result={"trekId": trekId, "itineraries": itineraries}
    )




@app.route("/myTreks/<string:param>")
def getTreksbyUser(param):
    userId = None
    if session.get("email"):
        logged_in_user = session["email"]

    if session.get("userId"):
        userId = session.get("userId")
    cursor = mysql.get_db().cursor()
    if param == "user":
        cursor.execute(
            """SELECT * FROM `Trek_Destinations` WHERE `user_id`=%s;""", (userId,)
        )
    else:
        cursor.execute("""SELECT * FROM `Trek_Destinations`;""")

    treks = cursor.fetchall()

    cursor.close()
    return render_template("mytreks.html", result={"treks": treks, "userId": userId})



@app.route("/search/treks")
def search():
    keyword = request.args.get("keyword")
    cursor = mysql.get_db().cursor()
    searchString = "%" + keyword + "%"
    cursor.execute(
        """SELECT * FROM `Trek_Destinations`
    WHERE `title` Like %s;""",
        (searchString,),
    )
    treks = cursor.fetchall()
    cursor.close()

    logged_in_user = None
    if session.get("email"):
        logged_in_user = session["email"]

    if session.get("userId"):
        userId = session.get("userId")
    result = {"treks": treks, "logged_in_user": logged_in_user}

    return render_template("mytreks.html", result={"treks": treks, "userId": userId})



@app.route("/api/doRegister", methods=["POST"])
def doRegisterAPI():
    print(request.json)

    full_name = request.json["full_name"]
    email = request.json["email"]
    phone_number = request.json["phone_number"]
    address = request.json["address"]

    password = request.json["psw"]
    hashed_password = generate_password_hash(password)

    token = uuid.uuid4()

    cursor = mysql.get_db().cursor()
    try:
        cursor.execute(
            """INSERT INTO `Users` (`id`, `full_name`, `address`, `email`, `phone_number`, `password`, `token`) VALUES (NULL, %s, %s, %s, %s, %s, %s);""",
            (full_name, address, email, phone_number, hashed_password, token),
        )

        
        mysql.get_db().commit()
        cursor.close()
    except IntegrityError:
        return jsonify({"result": "Duplicate email. Please enter different email."})

    return jsonify({"result": "Registered User Successfully"})


@app.route("/api/doLogin", methods=["POST"])
def doLoginApi():
    email = request.json["email"]
    password = request.json["password"]

    cursor = mysql.get_db().cursor()
    resp = cursor.execute("""SELECT password FROM Users WHERE email=%s;""", (email,))

    hashpassword = cursor.fetchone()[0]

    checkHashPassword = check_password_hash(hashpassword, password)

    if not checkHashPassword:
        return jsonify({"result": "Email and password didn't match"})

    resp = cursor.execute(
        """SELECT id,email ,full_name FROM Users WHERE email=%s and password=%s;""",
        (email, hashpassword),
    )

    user = cursor.fetchone()
    cursor.close()


    if resp == 1:
        session["email"] = email
        session["userId"] = user[0]
        logged_in_user = session.get("email")

        token = str(uuid.uuid4())

        cursor = mysql.get_db().cursor()
        resp = cursor.execute(
            """UPDATE Users set token=%s WHERE email=%s ;""", (token, email)
        )
        mysql.get_db().commit()

        user = cursor.fetchone()
        cursor.close()

        return jsonify(
            {"message": "Successful Login", "loggedIn": True, "token": token}
        )

    else:

        return jsonify(
            {
                "result": "Login Failed ,Please check your username and password",
                "loggedIn": False,
            }
        )



def _validate_token(token):
    cursor = mysql.get_db().cursor()
    cursor.execute("""SELECT id FROM Users WHERE token=%s;""", (token,))

    user = cursor.fetchone()
    cursor.close()
    userId = 0

    if user is not None:
        userId = user[0]
    return userId


@app.route("/rest/treks")
def allAPITreks():

    cursor = mysql.get_db().cursor()
    cursor.execute(
        """SELECT td.id as 'SNO', td.title as 'Title',
    td.days AS 'Days' , td.difficulty as 'Difficulty'
     ,td.total_cost as 'Total cost', td.upvotes as 'Upvotes', 
     u.full_name as 'Full name' FROM `Trek_Destinations`
    as td JOIN Users as u ON td.user_id=u.id;"""
    )
    treks = cursor.fetchall()

    cursor.close()
    logged_in_user = None
    if session.get("email"):
        logged_in_user = session["email"]
    result = {"treks": treks, "logged_in_user": logged_in_user}

    return jsonify(result)


@app.route("/rest/treks", methods=["POST"])
def doAddTrekApi():
    logged_in_user = None

    if session.get("email"):
        logged_in_user = session["email"]

    title = request.json["title"]
    days = request.json["days"]
    difficulty = request.json["difficulty"]
    total_cost = request.json["total_cost"]
    token = request.json["token"] or None

    userId = _validate_token(token)
    if userId == 0:
        return jsonify({"message": "Please enter a valid token"})

    upvotes = 0

    cursor = mysql.get_db().cursor()
    cursor.execute(
        """INSERT INTO `Trek_Destinations` VALUES (NULL, %s, %s, %s, %s, %s,%s);""",
        (
            title,
            days,
            difficulty,
            total_cost,
            upvotes,
            userId,
        ),
    )

    mysql.get_db().commit()
    cursor.close()

    return jsonify({"message": "Trek has been added Successfully"})


@app.route("/rest/treks", methods=["PUT"])
def doUpdateTrekApi():
    title = request.json["title"]
    days = request.json["days"]
    difficulty = request.json["difficulty"]
    total_cost = request.json["total_cost"]
    trekId = request.json["trekId"]

    token = request.json["token"] or None
    userId = _validate_token(token)
    if userId == 0:
        return jsonify({"message": "Please enter a valid token"})

    cursor = (
        mysql.get_db().cursor()
    resp = cursor.execute(
        """UPDATE `Trek_Destinations` SET `title`=%s,`days`=%s,`difficulty`=%s,`total_cost`=%s WHERE`id`=%s and `user_id`=%s ;""",
        (title, days, difficulty, total_cost, trekId, userId),
    )
    if resp == 0:
        return jsonify({"message": "you cannot update someone else's trek"})

    mysql.get_db().commit()  
    cursor.close()
    return jsonify({"message": "Trek has been updated Successfully"})


@app.route("/rest/treks", methods=["DELETE"])
def doDeleteTrekApi():

    trekId = request.json["trekId"]

    token = request.json["token"] or None
    userId = _validate_token(token)
    if userId == 0:
        return jsonify({"message": "Please enter a valid token"})

    cursor = mysql.get_db().cursor()
    resp = cursor.execute(
        """DELETE from `Trek_Destinations` WHERE `id`=%s and `user_id`=%s ;""",
        (trekId, userId),
    )
    if resp == 0:
        return jsonify({"message": "you cannot delete someone else's trek"})

    mysql.get_db().commit()
    cursor.close()
    return jsonify({"message": "Trek has been deleted Successfully"})


@app.route("/api/search/treks")
def searchApi():
    keyword = request.args.get("keyword")
    cursor = mysql.get_db().cursor()
    searchString = "%" + keyword + "%"
    cursor.execute(
        """SELECT * FROM `Trek_Destinations`
    WHERE `title` Like %s;""",
        (searchString,),
    )
    treks = cursor.fetchall()
    cursor.close()

    logged_in_user = None
    if session.get("email"):
        logged_in_user = session["email"]
    result = {"treks": treks, "logged_in_user": logged_in_user}

    return jsonify(result)


app.run(debug=True)
