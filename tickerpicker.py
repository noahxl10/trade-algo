import numpy as np  
import pandas as pd 
import os
import yfinance as yf
import random
import seaborn as sb
from scipy import stats


global dir_path
dir_path = os.path.dirname(os.path.realpath(__file__))
#__pypi-AgENdGVzdC5weXBpLm9yZwIkZDM5MmIwZmItYzc1OC00YTY1LTgxZTItOTVmYjVhYmI0MDljAAIleyJwZXJtaXNzaW9ucyI6ICJ1c2VyIiwgInZlcnNpb24iOiAxfQAABiBk2lnK_RpCh4129LcYNZJ7SE0QZlcKOiWkXyERfHbO0w__
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
