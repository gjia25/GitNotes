from flask import Flask, request, redirect, url_for, render_template, flash, session
import db
import os
from pathlib import Path
import codecs
import difflib
from werkzeug.utils import secure_filename
#from werkzeug.security import generate_password_hash, check_password_hash


ALLOWED_EXTENSIONS = set(['txt'])
UPLOAD_FOLDER = 'uploads/'
EDIT_FOLDER = 'edits/'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
Db = db.DB()
app.secret_key = "dev"

def getLogIn():
    try:
        return session['username']
    except:
        return None

def getDifference(fname1, fname2):
    txt = Path(os.path.join(os.path.abspath("."), UPLOAD_FOLDER, fname1+".txt")).read_text()
    txt = txt.split("\n")
    txt2 = Path(os.path.join(os.path.abspath("."), EDIT_FOLDER, fname2+".txt")).read_text()
    txt2 = txt2.split("\n")
    note = Db.getNoteFromId(fname1)
    edit = Db.getEditFromId(fname2)
    diff = difflib.HtmlDiff().make_table(txt,txt2, "master file", "edits")#"{0} by {1}".format(note[2], Db.getUserNameById(note[3])),"Edit by {0} \n {1}".format())#Db.getUserNameById(edit[2]), edit[3]))

    """
    pos1 = diff.index('<thead>')
    pos2 = diff.index('<tbody>')

    old = "master file"
    new = "edits"

    newfile1 = diff[:pos1]
    newfile2 = diff[pos2:]
    newfilewith2 = newfile1 + '<tr><th class="diff_next"><br /></th><th colspan="2" class="diff_header">{0}</th><th class="diff_next"><br /></th><th colspan="2" class="diff_header">{1}</th></tr></thead>'.format(old, new) + newfile2

    diff2 = difflib.HtmlDiff().make_file(fromfile,tofile2,fromfile,tofile2)

    pos3 = diff2.index('<table class="diff" id="difflib_chg_to1__top"')
    pos4 = diff2.index('<table class="diff" summary="Legends">')
    add = diff2[pos3:pos4]

    pos5 = newfilewith2.index('</table>')
    pos6 = newfilewith2.index('<table class="diff" summary="Legends">')
    before = newfilewith2[:pos5]
    after = newfilewith2[pos6:]
    newfile = before + add + after
    """
    return diff



@app.before_first_request
def runOnStart():
    try:
        session['userid']
        session['username']
    except:
         session['userid'] = None
         session['username'] = None
    session.permanent = True

@app.route('/logout/')
def logout():
    session.clear()
    session['userid'] = None
    session['username'] = None
    return redirect(url_for("home"))

@app.route('/')
def home():
    return render_template("index.html", user = session['username'], index = url_for("home"), browse = url_for("browse"), signout = url_for("logout"), account = url_for("account"), login = url_for("login_user"), img=url_for('static', filename="k.jpg")) #TODO: home page

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/browse/')
def browse():
    cursor = Db.getAllCourses()
    l = []
    for row in cursor:
        l.append({"href": url_for("browseCourse", course = row[0]), "id": row[0], "name": row[1], "instructor":row[2]})
    return render_template("browse.html", user = session['username'], account = url_for("account"), login = url_for("login_user"), courselist = l, index = url_for("home"), browse = url_for("browse"), signout = url_for("logout"))

@app.route('/browse/<course>/')
def browseCourse(course):
    cursor = Db.getAllNotesFromCourse(course)
    l = []
    for row in cursor:
        author = Db.getUserNameById(row[3])
        l.append({"href":url_for('browseNote', course = row[1], note = row[0]), "name":row[2], "author":author})
#    l = Db.getAllNotesFromCourse(course)
    row = Db.getCourseNameById(course)
    return render_template("coursebrowse.html", notelist = l, course_no = course, course_name = row[0], user = session['username'], account=url_for("account"), login=url_for("login_user"), index = url_for("home"), browse = url_for("browse"), upload = url_for("upload_file", course = course), signout = url_for("logout"))

@app.route('/browse/<course>/<note>/')
def browseNote(course, note):
    row = Db.getNoteFromId(note)
    text = Path(os.path.join(os.path.abspath("."), app.config['UPLOAD_FOLDER'], (note +".txt"))).read_text()
    text = text.split('\n')
    cursor = Db.getAllEditsByNote(note)
    print ("WORK")
    if cursor != None:
        print ("please")
        list = []
        for r in cursor:
            list.append({"href": url_for("browseEdits", courseid = course, note = note, edit = r[0]),"name": r[3], "user": Db.getUserNameById(r[2]), "comment":r[4], "id":r[0], "noteid":note})
    else:
        list = None
    print(session['username'])
    print(Db.getUserNameById(row[3]))
    return render_template("viewnotes.html", notes=text, user=session['username'], course = row[1], name = row[2], time = row[4], href = url_for("browseCourse", course=course), editlist = list, author = Db.getUserNameById(row[3]), push = url_for('push'), login = url_for("login_user"), uploadedits = url_for("uploadEdits", course = course, note = row[0]), index = url_for("home"), browse = url_for("browse"), account = url_for("account"), signout = url_for("logout"))

@app.route('/browse/<course>/upload/', methods=['GET', 'POST'])
def upload_file(course):
    if request.method == 'POST':
        if session['userid'] is None:
            flash("Please log in")
            print("Please log in")
            return redirect(request.url)
        if 'file' not in request.files:
            flash("No File Found") #TODO: redirect to NO FILE FOUND
            print("No File Found")
            return redirect(request.url)
        file = request.files['file']

        if file.filename == '':
            flash("No selected file")
            print("No selected file")
            return redirect(request.url) #TODO: redirect to NO SELECTED FILE
        if file and allowed_file(file.filename):
            try:
                #courseid = request.form['courseid']
                notename = request.form['notename']
                fileid = Db.addFile(course, notename, session['userid'])
            except Exception as e:
                flash("Please use a valid notename")
                print("Please use a valid notename", str(e))
                return redirect(request.url)
            filename = secure_filename(str(fileid) + ".txt")
            file.save(os.path.join(os.path.abspath("."), app.config["UPLOAD_FOLDER"], filename))
            flash("File uploaded")
            print("File uploaded")
            return redirect(url_for("browseNote", course = course, note = fileid)) #TODO: redirect
    return render_template("upload.html", login=url_for("login_user"), account = url_for("account"), user = session['username'], href=url_for("browseCourse", course=course), courseid = course, coursename = Db.getCourseNameById(course)[0], index = url_for("home"), browse = url_for("browse"), signout = url_for("logout")) #TODO: upload page


@app.route('/register/', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            if not username or (len(username) > 40):
                error = "Please use a valid username within 40 characters"
            elif not password:
                error = "Please enter a password"
            elif Db.insertUser(username, password) is not None:
                error = 'User {} is already registered.'.format(username)
            else:
                error = "Registration successful"
        except Exception as e:
            error = ("Something went wrong. The uesrname might be taken. Please try another one!")
        flash(error)
    return render_template("registration.html", login=url_for("login_user"), account = url_for("account"), user = session['username'], index = url_for("home"), browse = url_for("browse"), signout = url_for("logout")) #TODO: register pages

@app.route('/login/', methods=['GET', 'POST'])
def login_user():
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        passcode = Db.getUserPasswordByName(username)
        error = None
        if passcode is None:
            error = "User not found"
            print(error)
        elif passcode != password:
            error = "Incorrect password"
            print(error)

        if error is None:
            session.clear()
            session['userid'] = Db.getUserId(username)
            session['username'] = username
            return redirect(url_for("home"))

        flash(error)
    print(url_for("register_user"))
    return render_template("login.html", index = url_for("home"), browse = url_for("browse"), reg = url_for("register_user"), signout = url_for("logout")) #TODO: FIX THIS

@app.route('/account/')
def account():
    l = Db.getAllNotesByUser(session['userid'])
    for i in range(len(l)):
        l[i]['href'] = url_for("browseNote", course = l[i]['courseid'], note = l[i]['id'])
    print(l)
    return render_template("accounthome.html", uploadednotes = l, user = session['username'], account = url_for("account"), login = url_for("login_user"), index = url_for("home"), browse = url_for("browse"), signout = url_for("logout"))

@app.route('/browse/<courseid>/<note>/<edit>')
def browseEdits(courseid, note, edit):
    text = getDifference(note, edit)
    print(text)
    n = Db.getNoteFromId(note)
    return render_template("viewedit.html", user = session['username'], account = url_for('account'), login = url_for('login_user'), href = url_for('browseNote', note = note, course = courseid), courseid = courseid, notename = n[2], author = Db.getUserNameById(n[3]), time = n[4], table = text, noteid = note, editid = edit, push = url_for("push"), index = url_for("home"), browse = url_for("browse"), signout = url_for("logout"))

@app.route('/browse/<course>/<note>/uploadedits/', methods=["GET","POST"])
def uploadEdits(course, note):
    if request.method == 'POST':
        if session['userid'] is None:
            flash("Please log in")
            print("Please log in")
            return redirect(request.url)
        if 'file' not in request.files:
            flash("No File Found") #TODO: redirect to NO FILE FOUND
            print("No File Found")
            return redirect(request.url)
        file = request.files['file']

        if file.filename == '':
            flash("No selected file")
            print("No selected file")
            return redirect(request.url) #TODO: redirect to NO SELECTED FILE\
        if file and allowed_file(file.filename):
            try:
                #courseid = request.form['courseid']
                editname = request.form['editname']
                comment = request.form['comment']
                fileid = Db.addEdit(note, session['userid'], editname, comment)
            except Exception as e:
                flash("Something wrong happened. Please try again later.")
                print(str(e))
                return redirect(request.url)
            filename = secure_filename(str(fileid) + ".txt")
            file.save(os.path.join(os.path.abspath("."), EDIT_FOLDER, filename))
            flash("File uploaded")
            print("File uploaded")
            return redirect(url_for("browseEdits", courseid = course, note = note, edit = fileid))
    return render_template("uploadedits.html", user = session['username'], account = url_for('account'), login = url_for('login_user'), href = url_for('browseNote', course=course, note = note), courseid = course,
        noteid = Db.getNoteFromId(note)[2], index = url_for("home"), browse = url_for("browse"), signout = url_for("logout"))

@app.route('/push/', methods=['POST'])
def push():
    course = request.form['courseid']
    note = request.form['noteid']
    edit = request.form['editid']
    print(note)
    Db.deleteEdit(edit)
    f = open(os.path.join(os.path.abspath("."), app.config['UPLOAD_FOLDER'], (note +".txt")), "w")
    newfile = Path(os.path.join(os.path.abspath("."), EDIT_FOLDER, (edit+".txt"))).read_text()
    f.writelines(newfile)
    return redirect(url_for("browseNote", course = course, note = note) )

@app.route('/error/')
def error():
    return "Something went wrong. Please try again later."
