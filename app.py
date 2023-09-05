import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from help import login_required, apology, usd
from random import randint

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///data.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response
# chart.js

@app.route("/budgets")
@login_required
def budgets():
    return render_template("budgets.html")

def available_calc():
    available = db.execute("SELECT SUM(budget_cash) FROM budgets WHERE user_id == ?", session["user_id"])
    user_money = db.execute("SELECT cash FROM users WHERE id==?", session["user_id"])
    if available[0]['SUM(budget_cash)'] != None:
        available = float(user_money[0]['cash'])-float(available[0]['SUM(budget_cash)'])
    else:
        available = user_money[0]['cash']
    return available

@app.route("/budget_add", methods=["GET", "POST"])
@login_required
def budget_add():
    if request.method == "POST":

        budget_name = request.form.get("budget_name")
        budget_name_check = db.execute("SELECT budget_name FROM budgets WHERE budget_name == ? AND user_id == ?", budget_name, session["user_id"])
        print(budget_name_check)

        budget_cash = request.form.get("budget_cash")
        available = available_calc()

        cash_limit = request.form.get("cash_limit")

        if not budget_name or not budget_cash or not cash_limit:
            return apology("You need to feel all fields.")
        if float(budget_cash) > available:
            return apology("You have available " + str(available) + "$.")
        if budget_name in budget_name_check:
            return apology("Budget already exist.")
        if budget_cash.isnumeric() != True or cash_limit.isnumeric() != True or float(cash_limit) <0 or float(budget_cash) <0:
            return apology("Incorrect cash limit or budget money.")

        check_box = request.form.get("goals")
        if check_box == "goal":
            cash_goal = request.form.get("cash_goal")
            date_end = datetime.strptime(request.form.get("date_end"), "%Y-%m-%d")
            print(date_end)
            if datetime.now() > date_end:
                return apology("Incorrect date")
            if not cash_goal or not date_end:
                return apology("You need to feel a goal fields.")
            if cash_goal.isnumeric() != True or float(cash_goal) <0:
                return apology("Incorrect cash goal.")
            else:
                db.execute("INSERT INTO budgets(user_id, budget_name, budget_cash, cash_limit) VALUES (?, ?, ?, ?)", session["user_id"], budget_name, budget_cash, cash_limit)
                budget_id = db.execute("SELECT id FROM budgets WHERE user_id==? AND budget_name==?", session["user_id"], budget_name)
                db.execute("INSERT INTO goals(budget_id, cash_goal, date_start, date_end) VALUES (?, ?, ?, ?)", budget_id[0]['id'], cash_goal, datetime.now().strftime("%Y-%m-%d") ,date_end)

        else:
            db.execute("INSERT INTO budgets(user_id, budget_name, budget_cash, cash_limit) VALUES (?, ?, ?, ?)", session["user_id"], budget_name, budget_cash, cash_limit)

        budget_id = db.execute("SELECT id FROM budgets WHERE user_id==? AND budget_name==?", session["user_id"], budget_name)
        db.execute("INSERT INTO budgets_history(budget_id, money_use, operation, op_date) VALUES (?, ?, ?, ?)", budget_id[0]['id'], budget_cash, "create", datetime.now().strftime("%Y-%m-%d"))
        db.execute("INSERT INTO account_history(user_id, budget_name, money_use, operation, op_date) VALUES (?, ?, ?, ?, ?)", session["user_id"], budget_name, budget_cash, "create budget", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return redirect("/budgets")

    else:
        return render_template("budget_add.html",budgets=budgets)

@app.route("/edit")
@login_required
def edit():
    return render_template("edit.html")

@app.route("/edit_add", methods=["GET", "POST"])
@login_required
def edit_add():
    if request.method == "POST":
        money = request.form.get("money")
        if not money or not money.isnumeric() or float(money)<=0:
            return apology("Invalit amount of money.")
        else:
            dat = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
            result = float(money) + float(dat[0]['cash'])
            db.execute("UPDATE users SET cash = ? WHERE id = ?", result, session["user_id"])

            db.execute("INSERT INTO account_history(user_id, budget_name, money_use, account_balance, operation, op_date) VALUES (?, ?, ?, ?, ?, ?)", session["user_id"], "main", money, result, "add", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            return redirect("/")

    else:
        return render_template("edit_add.html")

@app.route("/edit_remove", methods=["GET", "POST"])
@login_required
def edit_remove():
    if request.method == "POST":
        money = request.form.get("money")
        status = db.execute("SELECT cash FROM users WHERE id == ?", session["user_id"])
        print(status)
        if not money or not money.isnumeric() or float(money)<=0:
            return apology("Invalit amount of money.")
        if float(status[0]["cash"]) - float(money) < 0:
            return apology("You don't have enought money.")
        else:
            dat = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
            result = float(dat[0]['cash']) - float(money)
            db.execute("UPDATE users SET cash = ? WHERE id = ?", result, session["user_id"])

            db.execute("INSERT INTO account_history(user_id, budget_name, money_use, account_balance, operation, op_date) VALUES (?, ?, ?, ?, ?, ?)", session["user_id"], "main", "-"+money, result, "remove", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            return redirect("/")

    else:
        return render_template("edit_remove.html")

def add(*args):
    db.execute("UPDATE budgets SET budget_cash = budget_cash + ? WHERE id == ?", args[1], args[0])
    db.execute("INSERT INTO budgets_history(budget_id, money_use, operation, op_date) VALUES (?, ?, ?, ?)", args[0], args[1], args[2], args[3])

def remov(*args):
    db.execute("UPDATE budgets SET budget_cash = budget_cash - ? WHERE id == ?", args[1], args[0])
    db.execute("INSERT INTO budgets_history(budget_id, money_use, operation, op_date) VALUES (?, ?, ?, ?)", args[0],'-' +  args[1], args[2], args[3])

# add history
@app.route("/edit_budget", methods=["GET", "POST"])
@login_required
def edit_budget():
    if request.method == "POST":
        budget_name = request.form.get("budget_name")
        action = request.form.get("add_subtract")
        cash = request.form.get("cash")
        cash_limit = request.form.get("cash_limit")
        goals = request.form.get("goals")

        budget_id = db.execute("SELECT id FROM budgets WHERE budget_name == ?", budget_name)

        if not budget_name or not action or not cash:
            return apology("You need to feel all fields.")

        #to validate
        if action == "add":
            add(budget_id[0]['id'], cash, "add", datetime.now().strftime("%Y-%m-%d"))
        if action == "subtract":
            remov(budget_id[0]['id'], cash, "subtract", datetime.now().strftime("%Y-%m-%d"))
        #####

        if goals:
            cash_goal = request.form.get("cash_goal")
            date_end = request.form.get("date_end")
            if not cash_goal or not date_end:
                return apology("You need to feel all fields.")
            if not db.execute("SELECT budget_id FROM goals WHERE budget_id == ?", budget_id[0]['id']):
                db.execute("INSERT INTO goals(budget_id, cash_goal, date_start, date_end) VALUES (?, ?, ?, ?)", budget_id[0]['id'], cash_goal, datetime.now().strftime("%Y-%m-%d") ,date_end)
            else:
                db.execute("UPDATE goals SET cash_goal = ?, date_end = ? WHERE budget_id == ?", cash_goal, date_end, budget_id[0]['id'])
        #####
        return redirect("/")

    else:
        data = db.execute("SELECT budget_name FROM budgets WHERE user_id==?", session["user_id"])
        return render_template("edit_budget.html", data=data)

@app.route("/budget_remove", methods=["GET", "POST"])
@login_required
def budget_remove():
    if request.method == "POST":
        to_delete = request.form.get("budget_name")
        if not to_delete:
            return apology("Incorrect choose.")
        else:
            db.execute("DELETE FROM budgets WHERE user_id==? AND budget_name==?", session["user_id"], to_delete)
            db.execute("INSERT INTO account_history(user_id, budget_name, money_use, operation, op_date) VALUES (?, ?, ?, ?, ?)", session["user_id"], to_delete, 0, "budget delete", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return redirect("/")

    else:
        data = db.execute("SELECT budget_name FROM budgets WHERE user_id==?", session["user_id"])
        return render_template("budget_remove.html", data=data)

@app.route("/history")
@login_required
def history():
    return render_template("history.html")

def random_color(quantity):
    a = []
    for i in range(quantity):
        r = str(randint(0,255))
        g = str(randint(0,255))
        b = str(randint(0,255))
        text = f"rgb({r},{g},{b})"
        a.append(text)
    return a


@app.route("/history_budgets", methods=["GET", "POST"])
@login_required
def history_budgets():
    table = db.execute("SELECT b.budget_name, h.money_use, h.operation, h.op_date FROM budgets_history h INNER JOIN budgets b ON h.budget_id = b.id WHERE b.user_id == ?", session["user_id"])
    if not table:
        table = None
    else:
        count = db.execute("SELECT COUNT(budget_name) FROM budgets WHERE user_id == ?", session["user_id"])
        colors = random_color(int(count[0]['COUNT(budget_name)']))
        value = db.execute("SELECT budget_cash ,budget_name FROM budgets WHERE user_id == ?", session["user_id"])
        values = [i['budget_cash'] for i in value]
        names = [i['budget_name'] for i in value]
        available = available_calc()
        values.append(available)
        names.append("Not assigned")
        colors.append("#5a5a5a")
        print(f"{values}    {colors}")

    return render_template("history_budgets.html", table=table, colors=colors, values=values, names=names)

@app.route("/account_history")
@login_required
def account_history():
    graph = db.execute("SELECT account_balance, op_date FROM account_history WHERE user_id == ? AND account_balance != 0", session["user_id"])
    print(graph)
    if graph:
        values = [i["account_balance"] for i in graph]
        labels = [i["op_date"] for i in graph]
    else:
        values = None
        labels = None
    data = db.execute("SELECT budget_name, money_use, operation, op_date FROM account_history WHERE user_id == ?", session["user_id"])
    if not data:
        data = None
    return render_template("account_history.html", data=data, values=values, labels=labels)

@app.route("/")
@login_required
def index():
    user_info = db.execute("SELECT * FROM users WHERE id == ?", session["user_id"])
    budgets = db.execute("SELECT * FROM budgets WHERE user_id == ?", session["user_id"])
    goals = db.execute("SELECT * FROM goals JOIN budgets ON goals.budget_id = budgets.id WHERE budgets.user_id = ?;", session["user_id"])
    if not budgets:
        budgets = None
    return render_template("home.html", cash=user_info[0]['cash'], budgets=budgets, goals=goals)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Must provide username.", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Must provide password.", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("Invalid username and/or password.", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        print(session)
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        username = request.form.get("username")
        password1 = request.form.get("password")
        password2 = request.form.get("confirmation")

        #checks that all fields are filled in
        if not username:
            return apology("Must provide username.", 400)

        elif not password1:
            return apology("Must provide password.", 400)

        elif not password2:
            return apology("Must provide repeat password.", 400)
        # check passwords and user name
        else:
            if db.execute("SELECT username FROM users WHERE username==?",username):
                return apology("User already exists", 400)

            elif password1 != password2:
                return apology("Passwords must by the same", 400)

            elif password1 == username:
                return apology("The password cannot be the same as the username.", 400)

            else:
                password_hash = generate_password_hash(password1, method='pbkdf2:sha256', salt_length=8)
                db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, password_hash)
                return redirect("/login")

    else:
        return render_template("register.html")