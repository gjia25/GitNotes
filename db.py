import sqlite3

def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance

class DB(object):
    def __init__(self):
        self.conn = sqlite3.connect("test.db", check_same_thread = False) #check_same_thread?
        self.createinittable()
        self.conn.execute("PRAGMA foreign_keys = ON")

    def createinittable(self):
        try:
            print("Creating Table user:")
            self.conn.execute("""
                CREATE TABLE user (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name CHARACTER(40) UNIQUE NOT NULL,
                    password TEXT NOT NULL
                    );
            """)
        except Exception as e:
            print(e)

        try:
            print ("Creating Course Table")
            self.conn.execute("""
                CREATE TABLE course(
                    id CHARACTER(10) PRIMARY KEY,
                    name TEXT NOT NULL,
                    instructor TEXT NOT NULL
                )
            """)
        except Exception as e:
            print(e)

        try:
            print ("Creating Notes Table")
            self.conn.execute("""
                CREATE TABLE notes(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    courseid CHARACTER(10) NOT NULL,
                    name TEXT NOT NULL,
                    userid INTEGER NOT NULL,
                    uploadtime DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    FOREIGN KEY(courseid) REFERENCES course(id),
                    FOREIGN KEY(userid) REFERENCES user(id)
                )
            """)
        except Exception as e:
            print(e)

        try:
            print ("Creating Edits Table")
            self.conn.execute("""
                CREATE TABLE edits(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    noteid INTEGER NOT NULL,
                    userid INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    comment TEXT NOT NULL,
                    uploadtime DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    FOREIGN KEY(noteid) REFERENCES notes(id),
                    FOREIGN KEY(userid) REFERENCES user(id)
                )
            """)
        except Exception as e:
            print(e)



#        try:
#            print("Creating Table user:")
#            self.conn.execute("""
#                CREATE TABLE user (
#                    id INTEGER PRIMARY KEY AUTOINCREMENT,
#                    name INTEGER UNIQUE NOT NULL
#                    );
#            """)
#        except Exception as e:
#            print(e)

    def call(self, command):
        cursor = self.conn.execute(command)
        return cursor

    def getAllNotesByUser(self, userid):
        print(userid)
        cursor = self.conn.execute("SELECT * FROM notes WHERE userid = ?;", (userid,))
        l = []
        for row in cursor:
            l.append({"name": row[2], "courseid":row[1], "id":row[0]})
            print("appended")
        return l

    def getAllNotesByUser2(self, userid):
        print(userid)
        cursor = self.conn.execute("SELECT * FROM notes WHERE userid = ?;", (userid,))
        return cursor

    def addFile(self, courseid, name, userid):
        cursor = self.conn.execute("INSERT INTO notes (courseid, name, userid) VALUES (?,?,?);", (courseid, name, userid))
        self.conn.commit()
        return cursor.lastrowid

    def addEdit(self, noteid, userid, name, comment):
        cursor = self.conn.execute("INSERT INTO edits (noteid, userid, name, comment) VALUES (?,?,?,?)", (noteid, userid, name, comment))
        self.conn.commit()
        return cursor.lastrowid

    def getAllNotesFromCourse(self, course):
        cursor = self.conn.execute("SELECT * FROM notes WHERE courseid = ?;", (course,))
        return cursor
#        l = []
#        for row in cursor:
#            l.append({"href":url_for('browseNote', course = row[1], note = note[0]), "name":row[2]})
#        return ls

    def getAllEditsByNote(self, noteid):
        cursor = self.conn.execute("SELECT * FROM edits WHERE noteid = ?", noteid)
        return cursor

    def getEditFromId(self, id):
        cursor = self.conn.execute("SELECT * FROM edits WHERE id = ?;", (id,))
        for row in cursor:
            return row

    def getNoteFromId(self, id):
        cursor = self.conn.execute("SELECT * FROM notes WHERE id = ?;", (id,))
        for row in cursor:
            return row

    def getUserNameById(self, id):
        cursor = self.conn.execute("SELECT (name) FROM user WHERE id = ?;", (id,))
        for row in cursor:
            return row[0]

    def getAllCourses(self):
        cursor = self.conn.execute("SELECT * FROM course;")
        return cursor

    def getUserPasswordByName(self, username):
        cursor = self.conn.execute("SELECT (password) FROM user WHERE name = ?;", (username,))
        for row in cursor:
            return row[0]

    def getUserId(self, username):
        cursor = self.conn.execute("SELECT (id) FROM user WHERE name = ?;", (username,))
        for row in cursor:
            return row[0]

    def getCourseNameById(self, course):
        cursor = self.conn.execute("SELECT (name) FROM course WHERE id = ?;", (course,))
        for row in cursor:
            return row

    def insertUser(self, username, password):
        cursor = self.conn.execute("""
            INSERT INTO user (name, password) VALUES (?,?);
        """, (username, password))
        self.conn.commit()
        for row in cursor:
            return row
            #{'id':row[0], 'userid':row[1], 'rating':row[2],
            #'checkintime':row[3]}

    def checkUserExist(self, username):
        cursor = self.conn.execute("SELECT id FROM user WHERE username = ?;", (username,))
        for row in cursor:
            return row

    def deleteEdit(self, edit):
        self.conn.execute("DELETE FROM edits WHERE id = ?", (edit,))
        self.conn.commit()

    def dropAll(self):
        self.conn.execute("DROP TABLE IF EXISTS user;")



DB = singleton(DB)
