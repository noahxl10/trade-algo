import matplotlib.pyplot as plt 
import matplotlib.animation as anim
import time
import pandas as pd
from datetime import datetime
from datetime import timezone
import timestamp as ts
import yfinance as yf
import alpaca_trade_api as tradeapi
import numpy as np    
import random
from progressbar import ProgressBar
import os
from iexfinance.stocks import Stock
import pandas_datareader as web
import seaborn as sb
from scipy import stats



global api
api = tradeapi.REST(
'PKVG70CAQ8HCKBXIP1GK',
'P2ZHaYfMdswgx23wcs7yv/BBWP6QIXJizyJTmG7d',
'https://paper-api.alpaca.markets')

global account
account = api.get_account()

global pbar
pbar = ProgressBar()
global dir_path
dir_path = os.path.dirname(os.path.realpath(__file__))

global mytoken
mytoken = "pk_cdd7add9c93d40308f8f38319307c98e"

def get_data(count):
    barset = api.get_barset(ticker, 'minute', limit=count)
    data = barset[ticker]
    return data

def current_close():
    a = Stock(ticker, token=mytoken)
    return a.get_quote()['latestPrice']
    
def position():
    pos = api.get_position(ticker)
    #print(f'Number of shares: {pos.qty}\n Market Value: {pos.market_value}\nProfit/Loss: {pos.change_today}' ) 
    return pos

def checkhours():
    clock = api.get_clock()
    print('The market is {}'.format('open.' if clock.is_open else 'closed.'))

def checkbal():
    cur_bal = float(account.equity)
    #balance_change = float(account.equity) - float(account.last_equity)
    return cur_bal #, balance_change

def minsofdata():
    startofday = datetime.now(timezone.utc).replace(hour=13, minute=30,second=0, microsecond=0)
    curtime = datetime.now(timezone.utc)
    mins_of_data = int(((curtime - startofday).seconds)/60)
    return mins_of_data

def currenttime():
    curtime = datetime.now(timezone.utc)
    return curtime

def max_shares():
    maxshares = checkbal() / current_close()
    return int(maxshares)

def longmarket(shares):
    print('Going long!')
    try:
        api.submit_order(symbol = ticker, qty = shares, 
            side = 'buy', type = 'market', time_in_force = 'gtc')
        print('Order confirmed.') 
        time.sleep(3)
        if int(position().qty) > 0:
            print(f'Long position open for {ticker}')
    except:
        print('Long market order failed.')

def longlimit(shares):
    print('Going long!')
    try:
        api.submit_order(symbol = ticker, qty = shares, 
            side = 'buy', type = 'limit', time_in_force = 'gtc', 
            limit_price = current_close())
        print('Order confirmed.')
        time.sleep(3)
        if int(position().qty) > 0:
            print(f'Long position open for {ticker}')
    except:
        print('Long limit order failed.')


def short(shares):
    print('Going short!')
    try: 
        api.submit_order(symbol = ticker, qty=shares, side = 'sell', type = 'market', time_in_force = 'gtc')
        print('Order confirmed.')
        
        # if int(position().qty) < 0:
        #     print(f'Short position open for {ticker}')
    except:
        print('Short order failed.')


def algo():

    # if minutes since 9:30am is greater than 2 mins, execute algo
    if minsofdata() > 2 and minsofdata() < (6.5*60):
        
        #last_data_time = data[-1].t.to_pydatetime()

        # while during market session (minutes less than total mins in trading session)
        while minsofdata() < (6.5*60):
            data = get_data(minsofdata())
            lastvol = data[-2].v
            curvol = data[-1].v
            print(f'Last vol is {lastvol} \n and curvol is {curvol}')
            print('Point 1)')
            # create average volume over last 10 minutes
            if len(data) >= 10:
                print('Point 2)')
                countsum=0
                for i in range(10): countsum+=data[-i].v    
                avg10min = countsum/10
            
            if curvol > lastvol:
                print('Point 3)')
                firstclose = current_close()
                
                while True:
                    time.sleep(5)
                    if current_close() < firstclose:
                        print('Point 4)')
                        short(max_shares())
                        time.sleep(2)
                        stoploss(position().side)
                        break
                    elif current_close() > firstclose:
                        print('Point 5)')
                        longmarket(max_shares())
                        stoploss(position().side)
                        break
            else:
                print('Volume smaller than previous.')
                time.sleep(61)
        print('Done')
    else:
        print('Not yet in trading session')

def closeposition(typetoclose):
    print('Closing position...')
    if typetoclose == 'short':
        api.submit_order(symbol = ticker, qty = -int(position().qty), 
            side = 'buy', type = 'market', time_in_force = 'gtc')
        time.sleep(3)
        try: 
            if position() == 0:
                print("Position didn't close")
        except:
            print(f'Short position in {ticker} closed.')
            
    if typetoclose == 'long':
        api.submit_order(symbol = ticker, qty = int(position().qty), 
            side = 'sell', type = 'market', time_in_force = 'gtc')
        
        time.sleep(3)
        try:
            if position() == 0:
                print("Position didn't close")
                
        except:
            print(f'Long position in {ticker} closed.')
            

def stoploss(typetoclose):
    entry = float(position().avg_entry_price)
    lowcheck = (entry - .5)
    highcheck = (entry +.5)
    print(f'lowcheck: {lowcheck} \n highcheck: {highcheck}')

    print('Stop loss activated.')
    print('Reading data...')
    while True:

        percent_gain_loss = round((float(position().unrealized_pl)/float(position().market_value)),3) * 100
        cur_price = float(position().current_price)
        
        print(f'Percent gain or loss is: {percent_gain_loss}%')
        print(cur_price)
        if typetoclose == 'long':
            if cur_price < lowcheck:
                closeposition(position().side)
                #short(max_shares())
                #stoploss('short')
                break
            if cur_price > entry:
                entry = cur_price

                lowcheck = (entry - .15)
                print(f'Stop loss set to {lowcheck} for long')

        elif typetoclose == 'short':

            if cur_price > highcheck:
                closeposition(position().side)
                #longmarket(max_shares())
                #stoploss('long')
                break
            if cur_price < entry:
                entry = cur_price

                highcheck = (entry +.15)
                print(f'Stop loss set to {highcheck} for short')
            
        time.sleep(2)


def prob_of_movement_day(qty): ## THIS IS FOR A WHOLE OPEN TO CLOSE DAY PERIOD
    filename = dir_path + '\\' + 'tickers.csv'
    df = pd.read_csv(filename)

    l =  list(df['Symbol'])
    #ticks = random.sample(l, 1)
    highest_probs = []
    probarray = []
    start_time_main = time.time()
    print('Pulling data...')
    if qty == 'length':
        num_stocks = range(len(l))
    else:
        num_stocks = range(qty)

    for j in num_stocks:
        #can do random.choice(lis) to get one name
        data = yf.Ticker(l[j])

        start_time = time.time()

        stock = data.history(period='1d', start='2010-3-25', end='2020-3-25')
        stock['Date'] = stock.index
        stock.reset_index(drop=True, inplace=True)
        n = 20

        stock['pctchange'] = stock['Open'].pct_change()[1:]
        largest = stock.nlargest(n, ['pctchange']) 
        smallest = stock.nsmallest(n, ['pctchange'])

        try:
            index = []
            for row in largest.index:
                x = int(row)+1
                index.append(x) 
            gainers = stock.iloc[index]
            count = 0
            for i in gainers['pctchange']:
                if i < 0:
                    count+=1
            probability_pos = count/n
            #print('Possiblity of negative after big positive day', probability_pos)
        except:
            probability_pos = 0
            #print('Out of range')

        try:
            index = []
            for row in smallest.index:
                x = int(row)+1
                index.append(x)
                losers = stock.iloc[index]
                count = 0
            for i in losers['pctchange']:
                if i > 0:
                    count+=1
            probability_neg = count/n
            #print('Possiblity of positive after big negative day', probability_neg)

        except: 
            probability_neg = 0
           
        
        if (probability_neg >.5) or (probability_pos > .5):

            testlist = [probability_pos, probability_neg]
            testlist.sort()
            if probability_pos > probability_neg:
                end_time = time.time()
                tempar = [ l[j], testlist[1], '- after +', (end_time - start_time) ]
            if probability_neg > probability_pos:
                end_time = time.time()
                tempar = [ l[j], testlist[1], '+ after -', (end_time - start_time) ]
            probarray.append(tempar)

    end_time_main = time.time()   
    print(f'Total minutes elapsed to do {num_stocks} stocks: ', (end_time_main-start_time_main)/60)   
    df = pd.DataFrame(probarray, columns = ['Ticker', 'Highest Probability', 'Type of Movement', 'Data Retrieval Time'])
    df = df.nlargest(10, ['Highest Probability'])  
    return df

def prob_of_movement_hourly(qty):
    filename = dir_path + '\\' + 'tickers.csv'
    df = pd.read_csv(filename)

    l =  list(df['Symbol'])
    #ticks = random.sample(l, 1)
    highest_probs = []
    probarray = []
    start_time_main = time.time()
    print('Pulling data...')


    data = yf.Ticker(ticker)

    start_time = time.time()

    stock = data.history(interval='30m', start='2020-2-15', end='2020-4-9')
    stock['Date'] = stock.index
    stock.reset_index(drop=True, inplace=True)
    n = 20

    stock['pctchange'] = stock['Open'].pct_change()[1:]
    largest = stock.nlargest(n, ['pctchange']) 
    smallest = stock.nsmallest(n, ['pctchange'])

    try:
        index = []
        for row in largest.index:
            x = int(row)+1
            index.append(x) 
        gainers = stock.iloc[index]
        count = 0
        for i in gainers['pctchange']:
            if i < 0:
                count+=1
        probability_pos = count/n
        print('Possiblity of negative after big positive day', probability_pos)
    except:
        probability_pos = 0
        print('Out of range')

    try:
        index = []
        for row in smallest.index:
            x = int(row)+1
            index.append(x)
            losers = stock.iloc[index]
            count = 0
        for i in losers['pctchange']:
            if i > 0:
                count+=1
        probability_neg = count/n
        print('Possiblity of positive after big negative day', probability_neg)

    except: 
        probability_neg = 0
        print('Out of range')

    end_time = time.time()   

    testlist = [probability_pos, probability_neg]
    testlist.sort()
    tempar = [ticker, testlist[0], '- after +', (end_time - start_time) ]
    probarray.append(tempar)
    tempar = [ticker, testlist[1], '+ after -', (end_time - start_time) ]
    probarray.append(tempar)

    #print(f'Total minutes elapsed to do {num_stocks} stocks: ', (end_time_main-start_time_main)/60)   
    df = pd.DataFrame(probarray, columns = ['Ticker', 'Highest Probability', 'Type of Movement', 'Data Retrieval Time'])
    df = df.nlargest(2, ['Highest Probability'])  
    return df

def print_entry():# (type, price, count):
    print('This will be for keeping track of bid/ask in time and sales') 
    new_entry = 0
    filename = dir_path + '/' + 'prints.xlsx'
    print(filename)

    orig_length = len(pd.read_excel(filename))
    while new_entry == 0:
        df = pd.read_excel(filename)
        if len(df) > orig_length:
            new_entry = (len(df) - orig_length)
            #print('New entry detected.')
            break
        #print('No new entries')
        time.sleep(2)
    return df[-1:]

def print_trader():
    prints = print_entry()

    global ticker
    ticker = (prints.iloc[0]['Ticker']).upper()
    print(ticker)
    bid_ask = (prints.iloc[0]['Bid/Ask']).upper()
    price = prints.iloc[0]['Price']
    PB = prints.iloc[0]['Pullback']
    PT = prints.iloc[0]['Pricetarget']

    threshhold = .2 # willing to go within 20% if pullback, so if $1 pulblack, go 80 cents

    while True:
        if bid_ask == 'ASK':
            if current_close() < (price - PB*(1-threshhold)):
                print('going long!')
                longmarket(100)
                break
            else:
                print('Pullback hasnt happened yet.')   
        elif bid_ask == 'BID':
            if current_close() > (price + PB*(1-threshhold)):
                print('going short!')
                short(100)
                break
            else:
                print('Pullback hasnt happened yet.')
        else:
            print('Faulty entry. Try again.')
            break
        time.sleep(60)

    print('Order executed. Stop loss function going.')


def tickerpicker():

    def SingleBeta(stock, index):
        stock = stock['Close']
        bench = index[0]['Close']
        stock_ret = stock.pct_change()[1:]
        bench_ret = bench.pct_change()[1:]


        ## SCATTER PLOTTER
        # sb.regplot(bench_ret,stock_ret)
        # plt.xlabel("Benchmark Returns")
        # plt.ylabel(f"{ticks[0]} Returns")
        # plt.title(f"% Returns Regression for {ticks[0]} vs {ticks[1]} for {dates_2[0]} to {dates_2[1]}")
        # plt.show()


        (beta, alpha) = stats.linregress(bench_ret.values,
                    stock_ret.values)[0:2]
        return beta, alpha

    def data():
        data = []
        for i in ticks:
            DAT = yf.Ticker(i)
            data.append(DAT)
        
        stock = data[0].history(period='1d', start=dates_st[0], end=dates_st[1])
        index = []
        for i in range(len(ticks)):
            try:
                sr = 'index' + str(i+1)
                sr = data[i+1].history(period='1d', start=dates_ind[0], end=dates_ind[1])
                index.append(sr)
            except:
                print('')

        return stock, index
        
    def plot(stock, index1):
        index = index1[0]

        stockstr = '{} Close'.format(ticks[0])
        indexstr = '{} Close'.format(ticks[1])
        stock[stockstr] = stock['Close']
        index[indexstr] = index['Close']

        df = stock.merge(index, on='Date')
        df = df[[indexstr, stockstr]]
        inc = []
        for i in df[indexstr]:
            increase = (i - df[indexstr][0])/ df[indexstr][0] + 1
            inc.append(increase*100)
        
        df['{} Returns'.format(ticks[1])] = inc
        inc = []
        for i in df[stockstr]:
            increase = (i - df[stockstr][0])/ df[stockstr][0] + 1
            inc.append(increase*100)
        
        df['{} Returns'.format(ticks[0])] = inc
        df['Date'] = df.index
        fig, ax = plt.subplots()
        df.plot(x = 'Date', y = ['{} Returns'.format(ticks[1]), '{} Returns'.format(ticks[0])], color =['#068bac', 'black'],ax=ax)
        plt.title(f"{ticks[0]} vs Benchmark % Returns for {dates_2[0]} to {dates_2[1]}")
        plt.ylabel('Return %')

        ## THIS WORKS FOR JUST HORIZONTAL GRID
        # axes = plt.gca()
        # axes.yaxis.grid()

        ax.grid()
        plt.show()


    global dates_st, dates_ind, dates_2, ticks
    dates_st = ['2020-1-01','2020-4-26']
    dates_ind = ['2020-1-01','2020-4-26']
    x,y = dates_st[0].replace('-', ' ').split(' '), dates_st[1].replace('-', ' ').split(' ')
    dates_2 = [(x[1]+'/' + x[2]+'/' + x[0]), (y[1]+'/' + y[2]+'/' + y[0])]

    # ticks = [stock, benchmark]
    

    filename = dir_path + '/' + 'tickers.csv'
    df = pd.read_csv(filename)

    l =  list(df['Symbol'])

    l = random.sample(l, 5) # random sample of 25 tickers
    beta_ar = []
    ticker_ar = []
    for i in l:
        ticks = [i, 'SPY']
        stock, index = data()
        #### FOR INDEX VS. STOCK PLOT ####
        #plot(stock, index)

        #### FOR BETA ####
        beta, alpha = SingleBeta(stock, index)
        ticker_ar.append(i)
        beta_ar.append(beta)
    
    df = pd.DataFrame({'ticker':ticker_ar, 'beta':beta_ar})
    largest = df.nlargest(1, ['beta'])  # top 1 betas
    return (largest['ticker'].values[0])
    


global ticker
ticker = tickerpicker()


## UNCOMMENT TO DEACTIVATE FULLY AUTONOMOUS ALGO TRADER ##

while True:
    algo()

