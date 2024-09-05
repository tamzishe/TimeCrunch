from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
db = SQLAlchemy(app)

class ToDo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True) 
    dateCreated= db.Column(db.DateTime, default=datetime.utcnow)
    dateDue=db.Column(db.DateTime, nullable=True)
    completed =  db.Column(db.Integer, default=0) #send to archive

    
    
    def __repr__(self):
        return '<Task %r>' % self.id

@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        task_content = request.form['content']
        new_task =  ToDo(content=task_content)
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect("/")
        except:
            return 'There was an issue adding your task'
    else:
        tasks =  ToDo.query.order_by(ToDo.dateCreated).all()
        return render_template('home.html', tasks=tasks)

@app.route("/delete/<int:id>")
def delete(id):
    taskToDelete = ToDo.query.get_or_404(id)

    try:
        db.session.delete(taskToDelete)
        db.session.commit()
        return redirect("/")
    except:
        return 'There was a issue deleting this task'

@app.route("/update/<int:id>", methods=["GET", "POST"])
def update(id):
    task =ToDo.query.get_or_404(id)
    if request.method=="POST":
        task.content = request.form['content']
        try:
            db.session.commit()
            return redirect("/")
        except:
            return 'There was an issue updating this task'

    else:
        return render_template("update.html", task=task)


if __name__== "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)