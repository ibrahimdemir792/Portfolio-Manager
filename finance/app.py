import os
import json

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd
# Import Pandas
import pandas as pd

# Import Yahoo_Fin Library
from yahoo_fin.stock_info import get_data
import yahoo_fin.stock_info as si

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Show portfolio of stocks"""
    user_id = session.get("user_id")
    portfolio = db.execute("SELECT * FROM portfolio WHERE user_id = ?", user_id)
    users = db.execute("SELECT * FROM users WHERE id = ?", user_id)
    stocks_data = []
    total = 0
    # Define a list to match stocks and current prices
    for stock in portfolio:
        symbol = stock["symbol"]
        id = stock["id"]
        lookupValue = lookup(symbol)
        if lookupValue:
            current_price = lookupValue["price"]
            total += current_price * stock["shares"]
            stocks_data.append({
                "id": id,
                "symbol": symbol,
                "name": stock["name"],
                "shares": stock["shares"],
                "current_price": current_price
            })
    return render_template("index.html", stocks_data=stocks_data, users=users, total=total)

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "GET":
        return render_template("buy.html")
    elif request.method == "POST":
        user_id = session.get("user_id")
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")
        lookupValue = lookup(symbol)
        row = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        # Check if user type correct symbol
        if lookupValue is None:
            return apology("Invalid Symbol")
        # Check if user can afford the buy
        elif lookupValue["price"] * int(shares) > row[0]["cash"]:
            return apology("Can't Afford")
        else:
            # If the stock is in the portfolio, update shares
            symbol_check = db.execute("SELECT * FROM portfolio WHERE user_id = ? AND symbol = ?", user_id, symbol)
            if symbol_check:
                current_shares = symbol_check[0]["shares"]
                new_shares = current_shares + int(shares)
                db.execute("UPDATE portfolio SET shares = ? WHERE id = ?", new_shares, symbol_check[0]["id"])
                db.execute("UPDATE users SET cash = ? where id = ?", (row[0]["cash"] - lookupValue["price"] * int(shares)), user_id)
                # Add to transaction history
                db.execute("INSERT INTO transactions (user_id, symbol, shares, price, transaction_type, name) VALUES(?, ?, ?, ?, ?, ?)", user_id, symbol, shares, lookupValue["price"], "buy", lookupValue["name"])
            else:
                db.execute("INSERT INTO portfolio (user_id, symbol, name, shares) VALUES (?, ?, ?, ?)", user_id, symbol, lookupValue["name"], shares)
                db.execute("UPDATE users SET cash = ? where id = ?", (row[0]["cash"] - lookupValue["price"] * int(shares)), user_id)
                # Add to transaction history
                db.execute("INSERT INTO transactions (user_id, symbol, shares, price, transaction_type, name) VALUES(?, ?, ?, ?, ?, ?)", user_id, symbol, shares, lookupValue["price"], "buy", lookupValue["name"])
        flash(f"Bought {shares} shares of {lookupValue['name']} with the price of {lookupValue['price']}","primary")
        return redirect("/")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_id = session.get("user_id")
    history_data = db.execute("SELECT * FROM transactions WHERE user_id = ? ORDER BY transaction_time DESC", user_id)
    cashHistory = db.execute("SELECT * FROM cashHistory WHERE user_id = ? ORDER BY transaction_time DESC", user_id)
    return render_template("history.html", history_data=history_data, cashHistory=cashHistory)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "GET":
        return render_template("quote.html")
    elif request.method == "POST":
        symbol = request.form.get("symbol")
        lookupValue = lookup(symbol)

        # Check if symbol has fundamental data or not
        try:
            fundamentals = si.get_stats_valuation(symbol)
            fundamentals_data = [{'Attribute': row[0], 'Value': row[1]} for _, row in fundamentals.iterrows()]
        except IndexError:
            fundamentals_data = []

        if lookupValue != None:
            return render_template("quote.html",symbol=symbol, lookupValue=lookupValue, fundamentals_data=fundamentals_data)
        else:
            return apology("Invalid Symbol")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if password != confirmation:
            return apology("Passwords do not match")
        else:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, generate_password_hash(password, method='pbkdf2', salt_length=16))
            return redirect("/")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    user_id = session.get("user_id")
    # Show sell page
    if request.method == "GET":
        stocks = db.execute("SELECT * FROM portfolio WHERE user_id = ?", user_id)
        return render_template("sell.html", stocks=stocks)
    # Do selling when click sell button
    else:
        symbol = request.form.get("symbol")
        shares = int(request.form.get("shares"))
        lookupValue = lookup(symbol)
        row = db.execute("SELECT * FROM portfolio WHERE user_id = ? AND symbol = ?", user_id, symbol)
        current_shares = row[0]["shares"]
        # Check user has enough shares to sell
        if shares > current_shares:
            return apology("Not enough shares")
        else:
            new_shares = current_shares - shares
            rows = db.execute("SELECT * FROM users WHERE id = ?", user_id)
            # Set new value for shares
            db.execute("UPDATE portfolio SET shares = ? WHERE user_id = ? AND symbol = ?", new_shares, row[0]["user_id"], symbol)
            # Add cash to the wallet
            db.execute("UPDATE users SET cash = ? WHERE id = ?", (rows[0]["cash"] + lookupValue["price"] * int(shares)), user_id)
            check_zero = db.execute("SELECT * FROM portfolio WHERE shares=0")
            # Add to transaction history
            db.execute("INSERT INTO transactions (user_id, symbol, shares, price, transaction_type, name) VALUES(?, ?, ?, ?, ?, ?)", user_id, symbol, shares, lookupValue["price"], "sell", lookupValue["name"])
            # Remove the shares from database if no remain
            if check_zero:
                db.execute("DELETE FROM portfolio WHERE shares=0")
        flash(f"Sold {shares} shares of {lookupValue['name']} with the price of {lookupValue['price']}","primary")
        return redirect("/")

@app.route("/cash", methods=["POST"])
@login_required
def cash():
    user_id = session.get("user_id")
    wallet = db.execute("SELECT * FROM users WHERE id = ?", user_id)
    amount = round(float(request.form.get("amount")),2)
    transactionType = request.form.get("transactionType")
    if transactionType == "Deposit":
        db.execute("UPDATE users SET cash = ? WHERE id = ?", (wallet[0]["cash"] + amount), user_id)
        # Save to CashHistory
        db.execute("INSERT INTO cashHistory (user_id, transactionType, amount) VALUES(?, ?, ?)", user_id, transactionType, amount)
        flash(f"{amount} Deposited", "primary")
    elif transactionType == "Withdraw":
        # Check Is There Enough Cash to Withdraw
        if amount > wallet[0]["cash"]:
            return apology("Not Enough Cash to Withdraw")
        else:
            db.execute("UPDATE users SET cash = ? WHERE id = ?", (wallet[0]["cash"] - amount), user_id)
            # Save to cashHistory
            db.execute("INSERT INTO cashHistory (user_id, transactionType, amount) VALUES(?, ?, ?)", user_id, transactionType, amount)
            flash(f"{amount} Withdrawn", "primary")
    return redirect("/")


@app.route("/profileSettings", methods=["GET", "POST"])
@login_required
def profileSettings():
    user_id = session.get("user_id")
    if request.method == "GET": 
        username = db.execute("SELECT * FROM users WHERE id = ?", user_id)
        return render_template("profileSettings.html", username=username)
    elif request.method == "POST":
        row = db.execute("SELECT * FROM users WHERE id = ?", user_id)

        # Change username
        newusername = request.form.get("newusername")
        
        # Change password
        oldpassword = request.form.get("oldpassword")
        newpassword = request.form.get("newpassword")
        newpasswordconfirmation = request.form.get("newpasswordconfirmation")
        
        # Delete account
        deleteAccPassword = request.form.get("deleteAccPassword")
        deleteAccConfirmation = request.form.get("deleteAccConfirmation")
        
        if newusername:
            db.execute("UPDATE users SET username = ? WHERE id = ?", newusername, user_id)
            return redirect("/profileSettings")
        elif oldpassword:
            if len(row) != 1 or not check_password_hash(row[0]["hash"],oldpassword):
                return apology("Invalid current password")
            elif newpassword != newpasswordconfirmation:
                return apology("New Password and Confirmation Do Not Match")
            elif newpassword == newpasswordconfirmation:
                db.execute("UPDATE users SET hash = ? WHERE id = ?", generate_password_hash(newpassword, method='pbkdf2', salt_length=16), user_id)
                flash("Password is successfully changed")
                return redirect("/logout")
        elif deleteAccPassword:
            if len(row) != 1 or not check_password_hash(row[0]["hash"],deleteAccPassword):
                return apology("Invalid password")
            elif deleteAccPassword != deleteAccConfirmation:
                return apology("Password and Confirmation Do Not Match")
            elif deleteAccPassword == deleteAccConfirmation:
                db.execute("DELETE FROM cashHistory WHERE user_id = ?", user_id)
                db.execute("DELETE FROM transactions WHERE user_id = ?", user_id)
                db.execute("DELETE FROM portfolio WHERE user_id = ?", user_id)
                db.execute("DELETE FROM users WHERE id = ?", user_id)
                return redirect("/logout")
        
        


@app.route("/delete", methods=["POST"])
def delete():
    transactionId = request.form.get("transactionId")
    cashId = request.form.get("cashId")
    stockId = request.form.get("stockId")
    if transactionId:
        db.execute("DELETE FROM transactions WHERE id = ?", transactionId)
        flash("Transaction History Deleted")
        return redirect("/history")
    elif cashId:
        db.execute("DELETE FROM cashHistory WHERE id = ?", cashId)
        flash("Cash History Deleted")
        return redirect("/history")
    elif stockId:
        db.execute("DELETE FROM portfolio WHERE id = ?", stockId)
        flash("Stock Deleted")
        return redirect("/")


@app.route("/edit", methods=["POST"])
def edit():
    # Get edit inputs from form
    user_id = session.get("user_id")
    editedShares = int(request.form.get("editShares"))
    editedPrice = float(request.form.get("editPrice"))
    editedTransactionId = int(request.form.get("editTransactionId"))

    # Get tables to make changes
    transaction = db.execute("SELECT * FROM transactions WHERE id = ? AND user_id = ?", editedTransactionId, user_id)
    editedSymbol = transaction[0]["symbol"]
    portfolio = db.execute("SELECT * FROM portfolio WHERE symbol = ? AND user_id = ?", editedSymbol, user_id)
    userData = db.execute("SELECT * FROM users WHERE id = ?", user_id)
    userWallet = userData[0]["cash"]

    # Get current values for math
    originalShares = transaction[0]["shares"]
    originalPrice = transaction[0]["price"]
    transactionType = transaction[0]["transaction_type"]

    # Math
    # Cash Calculation
    transactionValueBefore = originalShares * originalPrice
    transactionValueAfter = editedShares * editedPrice
    cashChange = transactionValueBefore - transactionValueAfter
    # Share count calculation
    shareDifferenceAtTransaction = editedShares - originalShares

    if transactionType == "buy":
        if userWallet + cashChange < 0:
            return apology("Not enough cash")
        # Check the symbol still in portfolio or not
        elif portfolio:
            portfolioShares = portfolio[0]["shares"]
            # Check is there enough shares in portfolio to decrease transaction shares
            if portfolioShares + shareDifferenceAtTransaction < 0:
                return apology("You can't have negative shares of stock")
            else:
                db.execute("UPDATE transactions SET shares = ? , price = ? WHERE id = ? AND user_id = ?", editedShares, editedPrice, editedTransactionId, user_id)
                db.execute("UPDATE portfolio SET shares = ? WHERE symbol = ? AND user_id = ?", (portfolioShares + shareDifferenceAtTransaction), editedSymbol, user_id)
                db.execute("UPDATE users SET cash = ? WHERE id = ?", (userWallet + cashChange), user_id)
                flash("Transaction Edited")
                # Remove shares from database if no remain
                checkZeroShares = db.execute("SELECT * FROM portfolio WHERE shares=0")
                if checkZeroShares:
                    db.execute("DELETE FROM portfolio WHERE shares=0")
                    return redirect("/history")
                return redirect("history")
        else:
            if editedShares - originalShares < 0:
                return apology("You can't have negative shares of stock")
            else:
                db.execute("UPDATE transactions SET shares = ? , price = ? WHERE id = ? AND user_id = ?", editedShares, editedPrice, editedTransactionId, user_id)
                db.execute("INSERT INTO portfolio (user_id, symbol, name, shares) VALUES (?, ?, ?, ?)", user_id, editedSymbol, transaction[0]["name"], (editedShares - originalShares))
                db.execute("UPDATE users SET cash = ? WHERE id = ?", (userWallet + cashChange), user_id)
                flash("Transaction Edited")
                checkZeroShares = db.execute("SELECT * FROM portfolio WHERE shares=0")
                if checkZeroShares:
                    db.execute("DELETE FROM portfolio WHERE shares=0")
                    return redirect("/history")
                return redirect("/history")
            
    elif transactionType == "sell":
        # Check the symbol still in portfolio or not
        if portfolio:
            portfolioShares = portfolio[0]["shares"]
            # Check is there enough shares in portfolio to sell more shares
            if portfolioShares - shareDifferenceAtTransaction < 0:
                return apology("You can't have negative shares of stock")
            else:
                db.execute("UPDATE transactions SET shares = ? , price = ? WHERE id = ? AND user_id = ?", editedShares, editedPrice, editedTransactionId, user_id)
                db.execute("UPDATE portfolio SET shares = ? WHERE symbol = ? AND user_id = ?", (portfolioShares - shareDifferenceAtTransaction), editedSymbol, user_id)
                db.execute("UPDATE users SET cash = ? WHERE id = ?", (userWallet - cashChange), user_id)
                flash("Transaction Edited")
                # Remove shares from database if no remain
                checkZeroShares = db.execute("SELECT * FROM portfolio WHERE shares=0")
                if checkZeroShares:
                    db.execute("DELETE FROM portfolio WHERE shares=0")
                    return redirect("/history")
                return redirect("history")
        else:
            if editedShares > originalShares:
                return apology("You can't have negative shares of stock")
            else:
                db.execute("UPDATE transactions SET shares = ? , price = ? WHERE id = ? AND user_id = ?", editedShares, editedPrice, editedTransactionId, user_id)
                db.execute("INSERT INTO portfolio (user_id, symbol, name, shares) VALUES (?, ?, ?, ?)", user_id, editedSymbol, transaction[0]["name"], (originalShares - editedShares))
                db.execute("UPDATE users SET cash = ? WHERE id = ?", (userWallet - cashChange), user_id)
                flash("Transaction Edited")
                checkZeroShares = db.execute("SELECT * FROM portfolio WHERE shares=0")
                if checkZeroShares:
                    db.execute("DELETE FROM portfolio WHERE shares=0")
                    return redirect("/history")
                return redirect("/history")

            


# Define the get_stock_data function
def get_stock_data(symbol):
    try:
        # Get stock data using yahoo_fin.stock_info
        data = get_data(symbol, start_date="09/30/2023", end_date="10/30/2023", index_as_date = True, interval="1d")
        
        # Convert the DataFrame to JSON
        json_data = data.to_json(orient='table')
        return json_data

    except Exception as e:
        return str(e)
    
@app.route('/get_stock_data', methods=['GET', 'POST'])
def fetch_stock_data():
    symbol = request.args.get('symbol')
    stock_data = get_stock_data(symbol)
    return stock_data