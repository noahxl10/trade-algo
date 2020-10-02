import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="alpaca_trading_algorithm",
    version="0.0.5",
    author="Noah Alex",
    author_email="noahxl10@gmail.com",
    description="A package to trade for you!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/noahxl10/trade-algo",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.1',
    package_data={  # Optional
        'alpaca_trading_algorithm': ['tickers.csv'],
            },
    #package_data={'capitalize': ['data/cap_data.txt']},
    install_requires=['scipy', 'numpy', 'pandas', 'yfinance', 'seaborn', 'datetime', 'iexfinance', 'alpaca_trade_api']
)