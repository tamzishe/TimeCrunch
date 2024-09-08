from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from time import strftime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
db = SQLAlchemy(app)

class ToDo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True) #may be a future implementation, as of right now, I think the app is fine without it
    dateCreated= db.Column(db.DateTime, default=datetime.now())
    dueDate=db.Column(db.Text, nullable=True)
    dueDateDebug=db.Column(db.Text, nullable=True)
    completed =  db.Column(db.Integer, default=0) #to send to archive

    def __repr__(self):
        return '<Task %r>' % self.id

@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        task_content = request.form['content']
        try:
            task_dueDate= request.form['dueDate']
            task_dueDebug = task_dueDate
            currentTime= str(datetime.now())
            task_dueDate = stringDateToView(task_dueDate)
            if task_dueDebug[0:10]==currentTime[0:10]:
                task_dueDate=task_dueDate[0:8]
        except:
            task_dueDate="No Due Date"
        new_task =  ToDo(content=task_content, dueDate=task_dueDate, dueDateDebug=task_dueDebug, completed=0)
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect("/")
        except:
            return 'There was an issue adding your task',404
    else:
        tasks =  ToDo.query.order_by(ToDo.dateCreated).all()
        return render_template('home.html', tasks=tasks, )

@app.route("/delete/<int:id>")
def delete(id):
    taskToDelete = ToDo.query.get_or_404(id)
    try:
        db.session.delete(taskToDelete)
        db.session.commit()
        return redirect("/")
    except:
        return 'There was a issue deleting this task'

@app.route("/complete/<int:id>")
def complete(id):
    taskComplete = ToDo.query.get_or_404(id)
    try:
        taskComplete.completed=1
        db.session.commit()
        return redirect("/")
    except:
        return 'There was a issue processing the completion of this task'

@app.route("/restore")
def restore():
    tasks =  ToDo.query.order_by(ToDo.dateCreated).all()
    return render_template("archive.html", tasks=tasks)

@app.route("/restore/<int:id>")
def restoreTask(id):
    taskComplete = ToDo.query.get_or_404(id)
    try:
        taskComplete.completed = 0
        db.session.commit()
        return redirect("/")
    except:
        return 'There was a issue restoring this task'


@app.route("/update/<int:id>", methods=["GET", "POST"])
def update(id):
    task =ToDo.query.get_or_404(id)
    if request.method=="POST":
        task.content = request.form['content']
        try:
            task.dueDate= request.form['dueDate']
            task.dueDate = stringDateToView(task.dueDate)
        except:
            task.dueDate="No Due Date"
        try:
            db.session.commit()
            return redirect("/")
        except:
            return 'There was an issue updating this task'

    else:
        return render_template("update.html", task=task)

def stringDateToView(string): #2024-09-19T14:04
    splitStringAtIndex=string.find('T')
    if splitStringAtIndex==-1:
        string=numToWords(string)
        return string
    date=string[:splitStringAtIndex]
    time=string[splitStringAtIndex+1:]
    if int(time[0:2])>12: #in the pm
        time = time.replace(time[0:2], str(int(time[0:2])-12),1)
        time += " PM"
    else:
        if int(time[0:2])<10:
            time = time.replace("0", "", 1)
        time += " PM"
    date=numToWords(date[0:10])
    return (time + '\n' + date)

def numToWords(date):
    monthsList=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct","Nov", "Dec"]
    month = monthsList[int(date[5:7])-1]
    string = month + " " + date[8:10]+", " + date[0:4]
    return string

if __name__== "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)