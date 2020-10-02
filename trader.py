import alpaca_trade_api as tradeapi
import time
from iexfinance.stocks import Stock
import yfinance as yf
from datetime import datetime
from datetime import timezone

class stock:


    def __init__(self, alpacaKey, alpacaSecretKey, iexKey, ticker):
        self.iexKey = iexKey
        self.ticker = ticker
        #self.shares = shares
        self.api = tradeapi.REST(
                alpacaKey,
                alpacaSecretKey,
                'https://paper-api.alpaca.markets')
        self.yfin = Stock(ticker, token = iexKey)
        self.account = self.api.get_account()


    def position(self):
        try:
            pos = self.api.get_position(self.ticker)
            print(f'Number of shares: {self.pos.qty}\n Market Value: {self.pos.market_value}\nProfit/Loss: {self.pos.change_today}' ) 
            return pos
        except:
            print('No position found.')


    def current_close(self):
        return yfin.get_quote()['latestPrice']


    def get_data(self, count):
        barset = self.api.get_barset(self.ticker, 'minute', limit=count)
        data = self.barset[self.ticker]
        return  data


    def checkhours(self):
        clock = self.api.get_clock()
        print('The market is {}'.format('open.' if clock.is_open else 'closed.'))

    def checkbal(self):
        cur_bal = float(self.account.equity)
        #balance_change = float(account.equity) - float(account.last_equity)
        return cur_bal #, balance_change

    def minsofdata(self):
        startofday = datetime.now(timezone.utc).replace(hour=13, minute=30,second=0, microsecond=0)
        curtime = datetime.now(timezone.utc)
        mins_of_data = int(((curtime - startofday).seconds)/60)
        return mins_of_data


    def max_shares(self):
        maxshares = self.checkbal() / self.current_close()
        return int(maxshares)


    def currenttime(self):
        curtime = datetime.now(timezone.utc)
        return curtime


    def longmarket(self, shares):
        print('Going long!')
        try:
            self.api.submit_order(symbol = self.ticker, qty = shares, 
                side = 'buy', type = 'market', time_in_force = 'gtc')
            print('Order confirmed.') 
            time.sleep(3)
            if int(self.position().qty) > 0:
                print(f'Long position open for {ticker}')
        except:
            print('Long market order failed.')


    def longlimit(self, shares):
        print('Going long!')
        try:
            self.api.submit_order(symbol = self.ticker, qty = shares, 
                side = 'buy', type = 'limit', time_in_force = 'gtc', 
                limit_price = self.current_close())
            print('Order confirmed.')
            time.sleep(3)
            if int(self.position().qty) > 0:
                print(f'Long position open for {self.ticker}')
        except:
            print('Long limit order failed.')


    def short(self, shares):
        print('Going short!')
        try: 
            self.api.submit_order(symbol = self.ticker, qty = shares, side = 'sell', type = 'market', time_in_force = 'gtc')
            print('Order confirmed.')
            
            if int(self.position().qty) < 0:
                print(f'Short position open for {self.ticker}')
        except:
            print('Short order failed.')


    def closeposition(self, typetoclose):
        print('Closing position...')
        if typetoclose == 'short':
            self.api.submit_order(symbol = self.ticker, qty = -int(self.position().qty), 
                side = 'buy', type = 'market', time_in_force = 'gtc')
            time.sleep(3)
            try: 
                if self.position() == 0:
                    print("Position didn't close")
            except:
                print(f'Short position in {ticker} closed.')
                
        if typetoclose == 'long':
            self.api.submit_order(symbol = self.ticker, qty = int(self.position().qty), 
                side = 'sell', type = 'market', time_in_force = 'gtc')
            
            time.sleep(3)
            try:
                if self.position() == 0:
                    print("Position didn't close")
                    
            except:
                print(f'Long position in {ticker} closed.')
                

    def stoploss(self, typetoclose):
        entry = float(self.position().avg_entry_price)
        lowcheck = (entry - .5)
        highcheck = (entry +.5)
        print(f'lowcheck: {lowcheck} \n highcheck: {highcheck}')

        print('Stop loss activated.')
        print('Reading data...')
        while True:

            percent_gain_loss = round((float(self.position().unrealized_pl)/float(self.position().market_value)),3) * 100
            cur_price = float(self.position().current_price)
            
            print(f'Percent gain or loss is: {percent_gain_loss}%')
            print(cur_price)
            if typetoclose == 'long':
                if cur_price < lowcheck:
                    self.closeposition(self.position().side)
                    #short(max_shares())
                    #stoploss('short')
                    break
                if cur_price > entry:
                    entry = cur_price

                    lowcheck = (entry - .15)
                    print(f'Stop loss set to {lowcheck} for long')

            elif typetoclose == 'short':

                if cur_price > highcheck:
                    self.closeposition(self.position().side)
                    #longmarket(max_shares())
                    #stoploss('long')
                    break
                if cur_price < entry:
                    entry = cur_price

                    highcheck = (entry +.15)
                    print(f'Stop loss set to {highcheck} for short')
                
            time.sleep(2)


    def algo(self):
    # if minutes since 9:30am is greater than 2 mins, execute algo
        if self.minsofdata() > 2 and self.minsofdata() < (6.5*60):
            
            #last_data_time = data[-1].t.to_pydatetime()

            # while during market session (minutes less than total mins in trading session)
            while self.minsofdata() < (6.5*60):
                data = self.get_data(self.minsofdata())
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
                    firstclose = self.current_close()
                    
                    while True:
                        time.sleep(5)
                        if self.current_close() < firstclose:
                            print('Point 4)')
                            self.short(self.max_shares())
                            time.sleep(2)
                            self.stoploss(self.position().side)
                            break
                        elif self.current_close() > firstclose:
                            print('Point 5)')
                            self.longmarket(self.max_shares())
                            self.stoploss(self.position().side)
                            break
                else:
                    print('Volume smaller than previous.')
                    time.sleep(61)
            print('Done')
        else:
            print('Not yet in trading session')
            print('Try again when the market is open')
            return False

    def trade(self, minutes):
        curtime = time.time()
        fintime = time.time()
        while (fintime-curtime)/60 < minutes:
            if self.algo() == False:
                break
            else:
                self.algo()