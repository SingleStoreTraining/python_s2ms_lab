from flask import Flask, render_template, request, redirect, session
from dbconnector import connectToS2MS
app = Flask(__name__)
app.secret_key = 'keep it secret, keep it safe'


@app.route('/')
def hello_world():
    print("in the index method")
    return render_template('index.html')


@app.route('/register', methods=['POST'])
def register():
    s2ms = connectToS2MS('pylabdb')
    # *** REGISTRATION 1 ***
    # Check Email To See If It Already Exists - Retrieve a User Using the Provided Email
    query = "SELECT * FROM users WHERE email = %(email)s"
    data = {"email" : request.form['Email']}
    UserExist = s2ms.query_db(query, data)

    if UserExist == ():
        print("NEW USER")
        if request.form['Password'] != request.form['PasswordConfirmation']:
            regerror = "Passwords do not match!"
            return render_template("index.html", regerror = regerror)
        else:
            # Validate for empty
            if request.form['Username'] == '' or request.form['Email'] == '' or request.form['Password'] == '':
                regerror = "Please complete all required fields"
                return render_template("index.html", regerror = regerror)
            else:
                #*** REGISTRATION 2 ***
                # Create the New User
                print("CREATING NEW USER!!!")
                s2ms = connectToS2MS('pylabdb')
                query = "INSERT INTO users (username, email, password) VALUES (%(username)s, %(email)s, %(password)s );"
                data = {
                    "username" : request.form['Username'],
                    "email" : request.form['Email'],
                    "password" : request.form['Password'],
                }
                s2ms.query_db(query, data)


                # *** REGISTRATION 3 ***
                # Set this user's id in session before redirecting
                s2ms = connectToS2MS('pylabdb')
                query = "SELECT * FROM users WHERE email = %(email)s"
                data = {"email" : request.form['Email']}
                UserExist = s2ms.query_db(query, data)
                session['userId'] = UserExist[0]['userId']

                return redirect("/dashboard")
                              
    else:
        regerror = "This email currently exists!"
        return render_template("index.html", regerror = regerror)


@app.route('/dashboard')
def dashboard():
    CurrSessionId = str(session['userId'])

    # *** DASHBOARD 1 ***
    # Retrieve Current User
    s2ms = connectToS2MS('pylabdb')
    query = "SELECT * FROM users WHERE userId = %(curruserid)s"
    data = {"curruserid" : CurrSessionId}
    CurrUser = s2ms.query_db(query, data)
        
    # *** DASHBOARD 2 ***
    # Retrieve Current User's ToDos
    s2ms = connectToS2MS('pylabdb')
    query = "SELECT * FROM toDos WHERE userId = %(userid)s;"
    data = {"userid" : CurrSessionId}
    AllToDos = s2ms.query_db(query, data)
    
    return render_template('dashboard.html', CurrUser = CurrUser, AllToDos = AllToDos)  # Return the string 'Hello World!' as a response
    

@app.route('/logout') 
def logout():
    session.clear()
    return redirect("/")


@app.route('/login', methods=['POST'])
def login():
    # *** LOGIN ***
    # Retrieve user with email
    s2ms = connectToS2MS('pylabdb')
    query = "SELECT * FROM users WHERE email = %(email)s"
    data = {"email" : request.form['Email']}
    CurrUser = s2ms.query_db(query, data)
    if CurrUser == ():
        logerror = "This email has not been registered. Please register or try again!"
        return render_template('index.html', logerror = logerror)
    else:
        # check password
        if CurrUser[0]["password"] != request.form['PwToCheck'] :
            logerror = "The password is incorrect - please try again!"
            return render_template('index.html', logerror = logerror)
    
        # Set this user's id in session before redirecting
        session['userId'] = CurrUser[0]['userId']
        return redirect("/dashboard")


@app.route('/addToDo', methods=['POST'])
def addToDo():
    if request.form['Title'] == '' or request.form['Description'] == '' :
        todoerror = "Please include all required fields."
    else :
        # *** CREATE TODO ***
        # Create New ToDo
        s2ms = connectToS2MS('pylabdb')
        query = "INSERT INTO toDos (title, description, userId) VALUES (%(title)s, %(description)s, %(userid)s);"
        data = {
            "title" : request.form['Title'],
            "description" : request.form['Description'],
            "userid" : session['userId']
        }
        CurrUser = s2ms.query_db(query, data)
    
    return redirect("/dashboard")



@app.route('/delete/<todoid>') 
def delete(todoid):
    # *** DELETE TODO ***
    # Delete Todo
    s2ms = connectToS2MS('pylabdb')
    query = "DELETE FROM toDos WHERE toDosId = %(toDoId)s"
    data = {"toDoId" : todoid}
    s2ms.query_db(query, data)

    return redirect("/dashboard")



@app.route('/edit/<todoid>') 
def edit(todoid):
    # *** EDIT TODO 1 ***
    # Retreive ToDo Using TodoId
    s2ms = connectToS2MS('pylabdb')
    query = "SELECT * FROM toDos WHERE toDosId = %(toDoId)s"
    data = {"toDoId" : todoid}
    CurrToDo = s2ms.query_db(query, data)

    return render_template('edit.html', CurrToDo = CurrToDo)


@app.route('/EditTodo', methods=['POST'])
def EditTodo():
    # *** EDIT TODO 2 ***
    # Update Todo
    s2ms = connectToS2MS('pylabdb')
    query = "UPDATE toDos SET title = %(title)s, description = %(description)s WHERE toDosId = %(todoid)s;"
    data = {
            "title" : request.form['Title'],
            "description" : request.form['Description'],
            "todoid" : request.form['TodoId']
        }
    s2ms.query_db(query, data)

    return redirect("/dashboard")




if __name__=="__main__":
    app.run(debug=True)
