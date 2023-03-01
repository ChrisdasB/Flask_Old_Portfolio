aeroleads_API = "c53b1e22d829b7b12666122519b8dec4"

import os
import re
import feedparser
import csv

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from credentials import *
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from flask_mail import Mail, Message
from profanity_check import predict
from langdetect import detect
from googletrans import Translator
from smtplib import SMTPException, SMTPRecipientsRefused


from toolbox import login_required, admin_required

app = Flask(__name__)

# Configure mailing
app.config['MAIL_SERVER']= 'smtp.web.de'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = mail_address
app.config['MAIL_PASSWORD'] = mail_password
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

# Setup Mailing
mail = Mail(app)

# Configure translator
translator = Translator()


# Deletes session when closes browser
app.config["SESSION_PERMANENT"] = False
app.secret_key = "banana"

# Get Database
db = SQL("sqlite:///portfolio.db")


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# HOME
@app.route("/", methods=["GET", "POST"])
@login_required
def home():
    # If we are logged in and send GET to home, display user-Homescreen
    if request.method == "GET":
        # Get current userdata of loged in user from DB
        userdata = db.execute("SELECT username, reg_date, user_id FROM users WHERE user_id=?;", session["user_id"])

        # Get the 5 newest comments from DB and sort by timestamp
        comments = db.execute("SELECT * FROM comments ORDER BY timestamp DESC LIMIT 10;")

        # Fro every comment, format timestamp and resolve username by user_id
        for comment in comments:
            comment["timestamp"] = comment["timestamp"][0:10]
            comment["username"] = db.execute("SELECT username FROM users WHERE user_id = ?;", comment["user_id"])[0]["username"]
        
        # Render template and send userdata and comments
        return render_template("home.html", userdata=userdata, comments=comments)


# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    # If requested via GET, display login page
    if request.method == "GET":
        return render_template("login.html")
    
    # If requested via POST

    # Get variables
    username = request.form.get("username")
    password = request.form.get("password")

    # Check for input
    if not username or not password:
        return render_template("login.html", warning="Please fill in a username and a password!")
    
    # Check for chars and numbers, no special chars allowed
    pattern = re.compile("^[a-zA-Z0-9]+$")

    # If username or password does not match regex, rerender template with warning
    if not pattern.search(password):
        return render_template("register.html", warning="Password may only contain upper and lower chars and numbers!")
    if not pattern.search(username):
        return render_template("register.html", warning="Username may only contain upper and lower chars and numbers!")
    
    # Try to get userdata based on given username, else rerender template with warning
    db_data = db.execute("SELECT * FROM users WHERE username = ?;", username)
    if not db_data:
        return render_template("login.html", warning="Username or Password incorrect!")
    
    # Compare stored hash against given password, else rerender template with warning
    if not check_password_hash(db_data[0]["hash"], password):
        return render_template("login.html", warning="Username or Password incorrect!")

    # Insert current timestmap on log_date into DB
    db.execute("UPDATE users SET log_date = ? WHERE user_id = ?;", datetime.now(), db_data[0]["user_id"])

    # Log user in by setting session key to user_id
    session["user_id"] = db_data[0]["user_id"]

    # Redriect to home
    return redirect("/")
    

# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():
    # If request via GET, show register page
    if request.method == "GET":
        return render_template("register.html")
    
    # If request via POST

    # Get variables from form
    newUsername = request.form.get("username")
    newPassword = request.form.get("password")
    confirmation = request.form.get("password2")

    # Check for input on all fields
    if not newUsername or not newPassword or not confirmation:
        return render_template("register.html", warning="Please fill all fields (Username, Password, Confirmation)")
    
    # Check for offensive username from local list

    # Fill profanity_list by opening, reading and adding from CSV-File
    profanity_list = []
    with open('static/custom_profanity.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in spamreader:
            profanity_list.append(row)

    # For propper comparrison, get username in lowercase
    newUsername_lower = newUsername.lower()

    # Check username against every entry in profanity_list, if we have a hit, rerender template with warning
    for word in profanity_list:
        if word[0] in newUsername_lower:
            return render_template("register.html", warning="No offensive usernames allowed.")
        
    # Translate text via API call to google translator
    newUsername_eng = translator.translate(newUsername_lower)
    newUsername_eng = newUsername_eng.text

    # Reformat translated text and put it in englisch profanity checker, if we have a hit, rerender template with warning
    newUsername_eng_arr = [newUsername_eng]
    if predict(newUsername_eng_arr) > 0:
        return render_template("register.html", warning="No offensive usernames allowed.")

    # Check if two passwords match
    if not newPassword == confirmation:
        return render_template("register.html", warning="Passwords do not match!")
    
    # Check if Username is beween 5 and 15 chars
    if not len(newUsername) >= 5 or len(newUsername) > 15:
        return render_template("register.html", warning="Username must be minimum 5 an maximum 15 chars!")

    # Check PW length and containing chars
    if not len(newPassword) >= 6 or len(newPassword) > 20:
        return render_template("register.html", warning="Password must be minimum 6 and maximum 20 chars!")
    
    # Check for a number in Password
    if not any(characters.isdigit() for characters in newPassword):
        return render_template("register.html", warning="Password must contain at least one number!")
    
    # Check for chars and numbers with regex pattern, no special chars allowed
    pattern = re.compile("^[a-zA-Z0-9]+$")
    if not pattern.search(newPassword):
        return render_template("register.html", warning="Password may only contain upper and lower chars and numbers!")
    if not pattern.search(newUsername):
        return render_template("register.html", warning="Username may only contain upper and lower chars and numbers!")

    # Check db for unique username    
    username_check = db.execute("SELECT username FROM users WHERE username = ?;", newUsername)
    if username_check:
        return render_template("register.html", warning="Username already taken!")
    
    # Insert new user into DB
    db.execute("INSERT INTO users (username, hash, reg_date) VALUES (?,?,?);",newUsername, generate_password_hash(newPassword), datetime.now())

    # Get user_id (Generated by DB)
    user_id = db.execute("SELECT user_id FROM users WHERE username = ?;", newUsername)

    # Log user in by setting session value
    session["user_id"] = user_id[0]["user_id"]

    # Redirect to home
    return redirect("/")


# LOGOUT
@app.route("/logout")
def logout():
    # Clear all session-data
    session.clear()
    # Redirect to home
    return redirect("/")


# CONTACT
@app.route("/contact", methods=["GET", "POST"])
@login_required
def contact():
    # If request method is GET
    if request.method == "GET":
        return render_template("contact.html")
    

    # If request method is POST

    # Get variables from form
    msg_title = request.form.get("title")
    message = request.form.get("message")
    user_mail = request.form.get("mail")

    # Check mail pattern against regex-pattern. If user did not provide mail, set to NO ENTRY
    mail_regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
    if not user_mail:
        user_mail = "NO ENTRY"
    elif not re.fullmatch(mail_regex, user_mail):
        return render_template("contact.html", warning = "You mail adress is not valid")    

    # Get username from DB
    username = db.execute("SELECT username FROM users WHERE user_id = ?;", session["user_id"])
    username = username[0]["username"]

    # Create and send thank you mail so sender
    
    # Mail validation seems to be only reliable with payed API's. This would go beyond the scope of the project for now.
    # I instead display a message, telling the user, that he should have received a 'Thank You' message.

    # If user provided mail address, prepare mail-template with given title and content
    if user_mail:        
        msg = Message("Thank you for your message!",sender=app.config['MAIL_USERNAME'], recipients=[user_mail])
        msg.html = render_template("tymessage.html", username=username, msg_title = msg_title, msg_body=message)
        # Try to send the TY-mail to given mail adress
        try:
            mail.send(msg)
        except SMTPRecipientsRefused as e:
            app.log_exception(e)
           

    # Create and send message to my mail adress
    msg = Message("New message from portfolio. User: " + username, sender=app.config['MAIL_USERNAME'], recipients=[contact_mail])
    msg.html = render_template("message.html", username=username, msg_title = msg_title, msg_body=message, user_mail=user_mail, timestamp = str(datetime.now()))
    mail.send(msg)


    # Return user to contact with notification, that sending was successfull
    return render_template("contact.html", warning="Message send. If you provided a mail address, please check your inbox. If you received no mail, you most likely misspelled your address or it is invalid!")


# COMMENT
@app.route("/comment", methods=["GET", "POST"])
@login_required
def comment():
    # If request method is GET, render template
    if request.method == "GET":
        return render_template("comment.html")
    
    # Get variables
    comment_text = request.form.get("comment")

    # Check input
    #If empty
    if not comment_text:
        return render_template("comment.html", warning="Please enter a comment!")
    
    # If shorter 5 or longer 35
    if len(comment_text.split(" ")) < 5 or len(comment_text.split(" ")) > 35:
        return render_template("comment.html", warning="Pleaser enter at lest 5 words, max 35!")
    
    # Prepare custom profanity list from local CSV
    profanity_list = []
    with open('static/custom_profanity.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in spamreader:
            profanity_list.append(row)

    # Transfer text to lower case
    comment_text_lower = comment_text.lower()

    # Check each word in text against profanity list
    for word in profanity_list:
        if word[0] in comment_text_lower:
            return render_template("comment.html", warning="Please watch your language :(")

    # Translate text API call from google translator
    comment_eng = translator.translate(comment_text)
    comment_eng = comment_eng.text

    # Format translated text and send it to englisch profnity checker
    comment_eng_arr = [comment_eng]
    if predict(comment_eng_arr) > 0:
        return render_template("comment.html", warning="Please watch your language :(")
    
    # If we detect a foreign language, display translated text for validation to user
    if detect(comment_text_lower) != "en":
        return render_template("comment.html", translation=comment_eng)

    # Insert comment into DB
    db.execute("INSERT INTO comments (user_id, timestamp, text) VALUES(?,?,?);", session["user_id"], str(datetime.now()), comment_text)

    # Redirect to home
    return redirect("/")


# RSSREADER
@app.route("/rssreader", methods=["GET", "POST"])
@login_required
def rssreader():
    # If request method is GET, display template
    if request.method == "GET":
        return render_template("rssreader.html")
    
    # Get variables
    rss_url = request.form.get("rssurl")

    # If no url provided, rerender template with warning
    if not rss_url:
        return render_template("rssreader.html", warning = "Please enter a URL!")
    
    # Check URL against regex-pattern and rerender template with warning if no match
    url_pattern = "^https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$"
    if not re.match(url_pattern, rss_url):
        return render_template("rssreader.html", warning = "Invalid entry. Make sure your link starts with 'HTTPS'!")

    # Contact given URL, get data and reformat it
    rss_feed = feedparser.parse(rss_url)

    rss_feed = rss_feed['entries']
    for feed in rss_feed:
        feed['published'] = feed['published'][0:16]

    # If we have no content found, rerender template with warning
    if len(rss_feed) == 0:
        warning_string = "{} entrys found! Please check your link/source.".format(len(rss_feed))
    # If we have found content, show user how many entry we found, along with the rss data
    else:
        warning_string = "{} entrys found!".format(len(rss_feed))
    return render_template("rssreader.html", rss_feed = rss_feed, warning = warning_string)


# BLOG
@app.route("/blog", methods=["GET"])
@login_required
def blog():
    # Get all blog-entrys from db, order the and display to user
    blogs = db.execute("SELECT * FROM blog ORDER BY timestamp DESC;")    
    return render_template("blog.html", blogs=blogs)


#ADMIN
@app.route("/admincenter", methods=["GET", "POST"])
# Make sure, admin is logged in in this session
@admin_required
def admincenter():
    # If request methos is GET, display admincenter
    if request.method == "GET":
        return render_template("admincenter.html")
    

# BLOGPOST
@app.route("/blogpost", methods =["POST"])
@admin_required
def blogpost():
    # Get variables from form
    blog_text = request.form.get("content")
    blog_title = request.form.get("title")

    # Insert into blog table in DB
    db.execute("INSERT INTO blog(text, title, timestamp) VALUES(?,?,?);",blog_text, blog_title, str(datetime.now())[0:19])

    # Rerender template and display success message
    return render_template("/admincenter.html", warning="Post successfull!")


# DELETE COMMENT
@app.route("/deletecomment", methods =["POST"])
@admin_required
def deletecomment():
    # Get variables
    comment_id = request.form.get("comment_id")
    if comment_id:
        db.execute("DELETE FROM comments WHERE comment_id=?;", comment_id)

    return redirect("/")

# DELETE POST
@app.route("/deletepost", methods =["POST"])
@admin_required
def deletepost():
    # Get variables
    post_id = request.form.get("post_id")
    if post_id:
        db.execute("DELETE FROM blog WHERE post_id=?;", post_id)

    return redirect("/blog")


# DELETE USER
@app.route("/deleteuser", methods =["POST"])
@admin_required
def deleteuser():
    # Get variables
    username = request.form.get("username")
    if not username:
        return render_template("/admincenter.html", warning1 = "Please enter a username!")
    
    userdata = db.execute("SELECT * FROM users WHERE username = ?;", username)
    if not userdata:
        return render_template("/admincenter.html", warning1 = "No user with the name '{}' found.".format(username))
    
    # DELETE COMMENTS FROM USER
    db.execute("DELETE FROM comments WHERE user_id = ?", userdata[0]['user_id'])

    # DELETE USER
    db.execute("DELETE FROM users WHERE user_id = ?", userdata[0]['user_id'])

    return render_template("/admincenter.html", warning1 = "User '{}' and all comments where deleted!".format(username))