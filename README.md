
## Hello, welcome to tradingalgorithm, a Python package for easy algorithmic trading on Alpaca
### This package allows one to check account status, make long orders, make short orders, run a custom momentum-based algorithm, and automatically calculate the best tickers to trade in the S&P500 based off of probability of returns and betas. 
### **To run this package, you will need an IEX Finance key, as well as an Alpaca API key**

To install the algorithm: 

```
$ pip install alpaca-trading-algorithm
```

### To pick a stock ticker:

```
from alpaca_trading_algorithm import tickerpicker

ticker = tickerpicker.tickerpicker()
```
### To create a stock class:

```
from alpaca_trading_algorithm import trader

ticker = 'AAPL'

aapl = trader.stock(alpacaKey, alpacaSecretKey, iexKey, ticker)

```
### Methods in the class:

```
aapl.position()
# output: Number of shares:  
#         Market Value: 
#         Profit/Loss: 

aapl.checkhours()
# output: The market is (open or close)
```

### Returns maximum amount of shares that you can trade of the ticker based on market value of cash portfolio

```
aapl.max_shares()
```

### Takes AAPL (or chosen ticker) long at the current market price and specified share amount

```
aapl.longmarket(shares)
```

### Takes AAPL (or chosen ticker) long at the current close of the stock

```
aapl.longlimit(shares)
```

### Takes AAPL (or chosen ticker) short at the current market price

```
aapl.short(shares)
```

### Closes entire short or long position in AAPL (or chosen ticker) based on whether you specify "long" or "short" as the typetoclose

```
aapl.closeposition(typetoclose)
```

### Runs a momentum algorithm ONE TIME based on volume and time&sales, will take a stock short, long, close position, re-position, and employs a custom stop-loss

```
aapl.algo()
```

### Runs the same momentum algorithm CONTINUOUSLY for the set amount of minutes

```
aapl.trade(minutes)

```
