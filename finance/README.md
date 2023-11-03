# PORTFOLIO TRACKING APP
#### Video Demo: https://youtu.be/xpppm8EFSlY
#### Description:
<p>This app helps user to track his market moves. With this app user can do several things:<br>
1. Buy or sell stock <br>
2. Quote stock and check fundamental data of the stock<br>
3. See monthly stock chart<br>
4. Deposit or withdraw cash<br>
5. Save transaction and cash history<br>
6. Edit transaction history (all math will be done by the app)<br>
7. Get live prices of the shares on the main page<br>
8. See cash holdings and total portfolio value by seperate<br>
9. Change username or password or delete account<br>
10. Switch between light and dark mode<br>

Flask is used to run the app with python and on the web side HTML, css and javascript are used. Yahoo_fin API is used to get historical prices and fundamental stock data.The data returns from yahoo_fin API as DataFrame. Pandas library is used to convert it to the python list. Also to save storage, historical prices and fundamentals are not stored. Instead of storing data into file, everytime user clicks the stock name, it request historical data from yahoo_fin API and insert it to the chart's x and y axis. But the trade of here is if there were many users, there would be over load to request data from API however this is a local project and I am the only user so I decide to code this way.<br>

"Echarts" is used to plot stock's monthly chart, "DataTables" library is used to create sortable portfolio table and it allows to user search into portfolio. "Font awesome" library is used to get editi delete and settings button icons.<br>

 FUNCTIONS
- QUOTE: User can check stock's current price and it's fundamentals by typing the symbol of stock.
- BUY: User can buy stocks from the current price by typing symbol and number of the shares. Buy function prevents user to buy more than user can afford.
- SELL: User can sell stocks which are bought before. This page prevent user to sell more shares than user has.
- HISTORY: User can watch or edit the transaction history. Transactions are colorized according to transaction type (sell or buy) to make view more clear. When user edit the transaction, app does math automatically according to transaction type and refresh user's portfolio and cash holdings. It is also prevent user to add more shares that user can afford and sell more than user has. Deleting a transaction does not do math automatically so be carefull while deleting any of these.
- DEPOSIT or WITHDRAW CASH: User can deposit or withdraw cash with using deposit or withdraw button. This function also prevents user to withdraw cash more than holdings.
- LIGHT OR DARK UI: User can change the UI color mode between light or dark mode.
- PROFILE SETTINGS: User can change username and password. Also the account can be deleted.<br>

 BACKGROUND FILES
- app.py: Runs the flask session with the bunch of route and functions. 
    - L:425, The most significant route and function here is the "get_stock_data" function which request historical prices from yahoo_fin API and converts it to json_data from dataframe. 
    * L:327, "edit" route does math for editing transaction and updating the portfolio.
- layout.html: It creates layout for all other pages.
    - L:37, validateName function prevents user to register with invalid characters.
- index.html: Creates portfolio table with using jinja2 for loop and hidden container for the stock charts. It also creates hidden deposit or withdraw cash div. 
- script.js: Creates dynamic interactions that allow the user to interact with the site in various ways. 
    - Single javascript code is written that works for different pages. It is segmented with the if function to avoid errors.
