# Import Stock Data
from yahoo_fin.stock_info import get_data
import yahoo_fin.stock_info as si
import pandas as pd
import json

#ticker_list = ["nvda", "tsla"]
#historical_datas ={}
#for ticker in ticker_list:
#    historical_datas[ticker] = get_data(ticker)
#print(historical_datas)
#dow_list = si.tickers_dow()
#print(historical_datas)
#print(dow_list, len(dow_list))
#quote_table = si.get_quote_table("nvda",dict_result=True)
#print(quote_table["Forward Dividend & Yield"])
#funda = si.get_stats_valuation("nvda")
#fundamentals_data = [{'Attribute': row[0], 'Value': row[1]} for _, row in funda.iterrows()]
#income = si.get_income_statement("aapl", yearly = True)
#print(funda)
#print(fundamentals_data)
#income

#balance = si.get_cash_flow("aapl")
#print(balance)

stock = get_data("nvda")
print(stock)


