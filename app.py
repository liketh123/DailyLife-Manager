from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import sqlite3
from pathlib import Path
from datetime import date

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "dailylife.db"
app = Flask(__name__)
app.secret_key = "change-this-secret-in-production"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL,
        priority TEXT NOT NULL DEFAULT 'Medium', due_date TEXT NOT NULL,
        completed INTEGER NOT NULL DEFAULT 0, created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS schedules (
        id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL,
        schedule_date TEXT NOT NULL, start_time TEXT NOT NULL,
        end_time TEXT, notes TEXT
    );
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL,
        amount REAL NOT NULL, category TEXT NOT NULL, expense_date TEXT NOT NULL, notes TEXT
    );
    CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL,
        target TEXT, progress INTEGER NOT NULL DEFAULT 0, deadline TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    conn.close()

@app.route("/")
def dashboard():
    conn = get_db()
    today = date.today().isoformat()
    tasks = conn.execute("SELECT * FROM tasks WHERE due_date=? ORDER BY completed, priority, id DESC",(today,)).fetchall()
    schedules = conn.execute("SELECT * FROM schedules WHERE schedule_date=? ORDER BY start_time",(today,)).fetchall()
    expenses = conn.execute("SELECT * FROM expenses WHERE expense_date=? ORDER BY id DESC",(today,)).fetchall()
    goals = conn.execute("SELECT * FROM goals ORDER BY deadline IS NULL, deadline").fetchall()
    stats = {
        "total_tasks": conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0],
        "completed_tasks": conn.execute("SELECT COUNT(*) FROM tasks WHERE completed=1").fetchone()[0],
        "today_expenses": conn.execute("SELECT COALESCE(SUM(amount),0) FROM expenses WHERE expense_date=?",(today,)).fetchone()[0],
        "goals": len(goals)
    }
    conn.close()
    return render_template("index.html", tasks=tasks, schedules=schedules, expenses=expenses, goals=goals, stats=stats, today=today)

@app.route("/tasks", methods=["GET","POST"])
def tasks():
    if request.method == "POST":
        title=request.form.get("title","").strip()
        priority=request.form.get("priority","Medium")
        due_date=request.form.get("due_date") or date.today().isoformat()
        if not title: flash("Task title is required.","error")
        else:
            conn=get_db(); conn.execute("INSERT INTO tasks(title,priority,due_date) VALUES(?,?,?)",(title,priority,due_date)); conn.commit(); conn.close()
            flash("Task added successfully.","success")
        return redirect(url_for("tasks"))
    conn=get_db(); rows=conn.execute("SELECT * FROM tasks ORDER BY due_date DESC, completed, id DESC").fetchall(); conn.close()
    return render_template("tasks.html",tasks=rows)

@app.post("/tasks/<int:task_id>/toggle")
def toggle_task(task_id):
    conn=get_db(); conn.execute("UPDATE tasks SET completed=CASE completed WHEN 0 THEN 1 ELSE 0 END WHERE id=?",(task_id,)); conn.commit(); conn.close()
    return redirect(request.referrer or url_for("dashboard"))

@app.post("/tasks/<int:task_id>/delete")
def delete_task(task_id):
    conn=get_db(); conn.execute("DELETE FROM tasks WHERE id=?",(task_id,)); conn.commit(); conn.close()
    flash("Task deleted.","success"); return redirect(request.referrer or url_for("tasks"))

@app.route("/schedule", methods=["GET","POST"])
def schedule():
    if request.method=="POST":
        title=request.form.get("title","").strip(); d=request.form.get("schedule_date") or date.today().isoformat()
        start=request.form.get("start_time",""); end=request.form.get("end_time",""); notes=request.form.get("notes","").strip()
        if not title or not start: flash("Activity name and start time are required.","error")
        else:
            conn=get_db(); conn.execute("INSERT INTO schedules(title,schedule_date,start_time,end_time,notes) VALUES(?,?,?,?,?)",(title,d,start,end,notes)); conn.commit(); conn.close()
            flash("Schedule item added.","success")
        return redirect(url_for("schedule"))
    conn=get_db(); rows=conn.execute("SELECT * FROM schedules ORDER BY schedule_date DESC,start_time").fetchall(); conn.close()
    return render_template("schedule.html",schedules=rows)

@app.post("/schedule/<int:item_id>/delete")
def delete_schedule(item_id):
    conn=get_db(); conn.execute("DELETE FROM schedules WHERE id=?",(item_id,)); conn.commit(); conn.close()
    flash("Schedule item deleted.","success"); return redirect(request.referrer or url_for("schedule"))

@app.route("/expenses", methods=["GET","POST"])
def expenses():
    if request.method=="POST":
        title=request.form.get("title","").strip(); raw=request.form.get("amount",""); category=request.form.get("category","Other")
        d=request.form.get("expense_date") or date.today().isoformat(); notes=request.form.get("notes","").strip()
        try:
            amount=float(raw)
            if amount<=0: raise ValueError
        except ValueError: amount=None
        if not title or amount is None: flash("Enter a valid expense name and positive amount.","error")
        else:
            conn=get_db(); conn.execute("INSERT INTO expenses(title,amount,category,expense_date,notes) VALUES(?,?,?,?,?)",(title,amount,category,d,notes)); conn.commit(); conn.close()
            flash("Expense added.","success")
        return redirect(url_for("expenses"))
    conn=get_db(); rows=conn.execute("SELECT * FROM expenses ORDER BY expense_date DESC,id DESC").fetchall()
    total=conn.execute("SELECT COALESCE(SUM(amount),0) FROM expenses").fetchone()[0]; conn.close()
    return render_template("expenses.html",expenses=rows,total=total)

@app.post("/expenses/<int:expense_id>/delete")
def delete_expense(expense_id):
    conn=get_db(); conn.execute("DELETE FROM expenses WHERE id=?",(expense_id,)); conn.commit(); conn.close()
    flash("Expense deleted.","success"); return redirect(request.referrer or url_for("expenses"))

@app.route("/goals", methods=["GET","POST"])
def goals():
    if request.method=="POST":
        title=request.form.get("title","").strip(); target=request.form.get("target","").strip(); deadline=request.form.get("deadline") or None
        try: progress=max(0,min(100,int(request.form.get("progress",0))))
        except ValueError: progress=0
        if not title: flash("Goal title is required.","error")
        else:
            conn=get_db(); conn.execute("INSERT INTO goals(title,target,progress,deadline) VALUES(?,?,?,?)",(title,target,progress,deadline)); conn.commit(); conn.close()
            flash("Goal added.","success")
        return redirect(url_for("goals"))
    conn=get_db(); rows=conn.execute("SELECT * FROM goals ORDER BY deadline IS NULL,deadline").fetchall(); conn.close()
    return render_template("goals.html",goals=rows)

@app.post("/goals/<int:goal_id>/progress")
def update_goal_progress(goal_id):
    try: progress=max(0,min(100,int(request.form.get("progress",0))))
    except ValueError: progress=0
    conn=get_db(); conn.execute("UPDATE goals SET progress=? WHERE id=?",(progress,goal_id)); conn.commit(); conn.close()
    return redirect(request.referrer or url_for("goals"))

@app.post("/goals/<int:goal_id>/delete")
def delete_goal(goal_id):
    conn=get_db(); conn.execute("DELETE FROM goals WHERE id=?",(goal_id,)); conn.commit(); conn.close()
    flash("Goal deleted.","success"); return redirect(request.referrer or url_for("goals"))

@app.route("/health")
def health():
    try:
        conn=get_db(); conn.execute("SELECT 1").fetchone(); conn.close()
        return jsonify(status="healthy",application="DailyLife Manager"),200
    except Exception as exc:
        return jsonify(status="unhealthy",error=str(exc)),503

if __name__=="__main__":
    init_db()
    app.run(host="0.0.0.0",port=5000,debug=True)
