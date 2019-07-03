from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp

from helpers import *

# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# custom filter
app.jinja_env.filters["usd"] = usd

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

@app.route("/")
@login_required
def index():
    wallet = db.execute("SELECT stock_symbol, number_of_shares FROM wallet WHERE user_id is :user_id", user_id = session.get("user_id"))
    for idx, share in enumerate(wallet):
        symbol = lookup(wallet[idx]["stock_symbol"])
        if symbol == None:
            return apology("could not load your wallet, {}".format(wallet[idx]["stock_symbol"]))
        upwallet = db.execute ("UPDATE wallet SET lkprice = :price, share_value = :value WHERE user_id = :id AND stock_symbol = :stock", 
                             price = symbol["price"], value = symbol["price"] * wallet[idx]["number_of_shares"], id = session.get("user_id"),
                             stock = wallet[idx]["stock_symbol"])
    cash = db.execute ("SELECT cash FROM users WHERE id is :id", id=session.get("user_id"))
    wallet = db.execute("SELECT stock_symbol, number_of_shares, lkprice, share_value FROM wallet WHERE user_id is :user_id", user_id = session.get("user_id"))
    
    sum = db.execute ("SELECT sum(share_value) FROM wallet WHERE user_id is :user_id", user_id = session.get("user_id"))
    if sum[0]["sum(share_value)"] == None:
        value = 0
        return render_template("wallet.html", WALLET = wallet, CASH = cash[0]["cash"], SUM = value)
    else:
        value = sum[0]["sum(share_value)"]
        return render_template("wallet.html", WALLET = wallet, CASH = cash[0]["cash"], SUM = value)
        
    


        
    

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock."""
    
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure stock symbol was submitted
        if len(request.form.get("stockname")) != 4:
            return apology("must provide 4-letter symbol")

        # ensure number of shares was submitted
        if not request.form.get("quantity"):
            return apology("must provide number of shares")
            
        # validate if number of shares is a positive number
        try:
            if int(request.form.get("quantity")) < 1:
                return apology("must provide positive number of stocks")
        except ValueError:
            return apology("must provide positive numerical quantity of shares")
        stock_number = int(request.form.get("quantity"))
        
        # look for stock symbol, check if exists and get data
        stock_look = lookup(request.form.get("stockname"))
        
        if stock_look == None:
            return apology("Stock not found or error occured")
        
        # query database for cash
        Actual_cash = db.execute("SELECT cash FROM users WHERE id = :id", id=session.get("user_id"))
        
        # check if enough money to buy a new share
        if Actual_cash[0]["cash"] < stock_look["price"] * stock_number:
            return apology("You can't afford to buy it")
        new_cash = db.execute("UPDATE users SET cash = :updated_cash WHERE id = :id", 
                                 updated_cash = Actual_cash[0]["cash"] - stock_look["price"]*stock_number, \
                                 id = session.get("user_id") )
        
        # finish transaction, insert to database,
        transaction = db.execute("INSERT INTO transactions\
                                (user_id, stock_symbol, number_stocks, unit_price, total_price) \
                                VALUES (:user_id, :stock_symbol, :number_stocks, :unit_price, :total_price)",\
                                user_id=session.get("user_id"), stock_symbol=stock_look["symbol"],\
                                number_stocks=stock_number, unit_price=stock_look["price"],\
                                total_price = 0 - stock_number * stock_look["price"])
        
        # look into wallet table if user already has some shares of this stock
        check_wallet = db.execute("SELECT * FROM wallet WHERE stock_symbol is :stock_symbol AND user_id is :user_id",
                                 stock_symbol = stock_look["symbol"], user_id = session.get("user_id"))
        
        if len(check_wallet) == 0:
            add_stock = db.execute("INSERT INTO wallet\
                                (user_id, stock_symbol, number_of_shares) \
                                VALUES (:user_id, :stock_symbol, :number_of_shares)",\
                                user_id=session.get("user_id"), stock_symbol=stock_look["symbol"],\
                                number_of_shares=stock_number)
        else:
            update_stock = db.execute("UPDATE wallet SET number_of_shares = number_of_shares + :updated_share WHERE user_id is :user_id AND stock_symbol = :stock_symbol",
                                      updated_share = stock_number, stock_symbol = stock_look["symbol"], 
                                      user_id = session.get("user_id"))
        flash("Bought")

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("buy.html")
    

@app.route("/history")
@login_required
def history():
    """Show history of transactions."""
    
    # read the transactions table
    history = db.execute("SELECT * FROM transactions WHERE user_id is :user_id", user_id = session.get("user_id"))
    
    return render_template("history.html", HISTORY = history)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return apology("invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))

@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    
    # if user reached route via POST
    if request.method == "POST":
        
        if len (request.form.get("stockname")) != 4:
            return apology("You need to provide 4-letter symbol")
        
        stock = lookup((request.form.get("stockname")).upper())
        
        if stock == None:
            return apology("Stock not found or error occured")
        else:
            return render_template("quoted.html", name = stock["name"], price = stock["price"], symbol = stock["symbol"])
        
    
    # else if user reached route via GET
    else:
        return render_template("quote.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""
    
        # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")
            
        elif not request.form.get("password") == request.form.get("repeat password"):
            return apology("repeat same password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) >= 1:
            return apology("username already exists")
        
        # insert new user into table
        try:
            result= db.execute("INSERT INTO users (username, hash) \
                            VALUES (:username, :hash)", \
                            username=request.form.get("username"), \
                            hash=pwd_context.hash(request.form.get("password")))
            flash("Registered. Enjoy! ")
        except RuntimeError:
            return apology("Error. Could not register")
            
        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/changepassw", methods=["GET", "POST"])
@login_required
def changepassw():
    """change password."""
    
        # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure old password was submitted
        if not request.form.get("old password"):
            return apology("must provide old password")

        # ensure new password was submitted
        elif not request.form.get("new password"):
            return apology("must provide new password")
            
        elif not request.form.get("new password") == request.form.get("repeat new password"):
            return apology("repeat same password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE id = :id", id=session.get("user_id"))
        if rows[0]["hash"] == None:
            return apology("could not read your current password")

        # ensure password is correct
        if not pwd_context.verify(request.form.get("old password"), rows[0]["hash"]):
            return apology("invalid old password")
        
        # update new password into table
        try:
            result= db.execute("UPDATE users SET hash = :hash WHERE id = :id", id=session.get("user_id"), hash=pwd_context.hash(request.form.get("new password")))
        except RuntimeErro:
            return apology("database error, could not store your new password")
        
        if result == 1:
            flash(" new password stored")
            # redirect user to home page
            return redirect(url_for("login"))
        else:
            return apology("something's wrong with your new password")

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("newpassword.html")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock."""
    
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure stock symbol was submitted
        if len(request.form.get("stockname")) != 4:
            return apology("must provide 4-letter symbol")
        stockname = request.form.get("stockname")
        stockname = stockname.upper()

        # ensure number of shares was submitted
        if not request.form.get("quantity"):
            return apology("must provide number of shares")
            
        # validate if number of shares is a positive number
        try:
            if int(request.form.get("quantity")) < 1:
                return apology("must provide positive number of stocks")
        except ValueError:
            return apology("must provide positive numerical quantity of shares")
        stock_number = int(request.form.get("quantity"))
        
        # look into wallet table if user really has some shares of this stock
        check_wallet = db.execute("SELECT * FROM wallet WHERE stock_symbol is :stock_symbol AND user_id is :user_id",
                                 stock_symbol = stockname, user_id = session.get("user_id"))
        
        # if no shares in wallet 
        if len(check_wallet) == 0:
            return apology ("The stock is not found in your wallet")
        
        # check if if user has enough shares to sell
        elif check_wallet[0]["number_of_shares"] < stock_number:
            return apology (" You're trying to sell more than you have in your wallet")
            
        
        # look for stock symbol, check if exists and get data
        stock_look = lookup(stockname)
        
        if stock_look == None:
            return apology("Stock not found or error occured")
        
        # updating cash
        new_cash = db.execute("UPDATE users SET cash = cash + :sell_cash WHERE id = :id", 
                                 sell_cash = stock_look["price"]*stock_number, \
                                 id = session.get("user_id") )
        
        # finish transaction, insert to transactions,
        transaction = db.execute("INSERT INTO transactions\
                                (user_id, stock_symbol, number_stocks, unit_price, total_price) \
                                VALUES (:user_id, :stock_symbol, :number_stocks, :unit_price, :total_price)",\
                                user_id=session.get("user_id"), stock_symbol=stock_look["symbol"],\
                                number_stocks=stock_number, unit_price=stock_look["price"],\
                                total_price = stock_number * stock_look["price"])
        
        # updating shares in wallet
        update_stock = db.execute("UPDATE wallet SET number_of_shares = number_of_shares - :updated_share WHERE user_id is :user_id AND stock_symbol is :stock_symbol ",
                                updated_share = stock_number, user_id = session.get("user_id"), stock_symbol = stockname)
        
        # check if number of stock is zero, if yes delete the record from the table                              
        check_zero = db.execute("SELECT number_of_shares FROM wallet WHERE user_id is :user_id AND stock_symbol is :stock_symbol", 
                                user_id = session.get("user_id"), stock_symbol = stockname)
        
        if check_zero[0]["number_of_shares"] == 0: 
            delete_record = db.execute("DELETE FROM wallet WHERE user_id is :user_id AND stock_symbol is :stock_symbol", 
                                user_id = session.get("user_id"), stock_symbol = stockname)
            flash(" You sold the whole stock. Record deleted from your wallet")
        else:
            flash(" Sold ")

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("sell.html")
