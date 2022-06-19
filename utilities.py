from math import exp
import settings
import requests
from json import loads as json_loads
import pandas as pd

# def get_desired_allocation(prev_day_market_move, security_pct_over_target):
#
#     allocation = 1 - 1 / (1 + exp(-1 * settings.EXPONENTIAL_AGGRESSIVENESS_PARAM * (settings.WEIGHT_PREVIOUS_DAYS_MARKET_MOVE * prev_day_market_move + settings.WEIGHT_SECURITY_LEVEL_VS_PRICE_TARGET * security_pct_over_target)))
#
#     return allocation

def get_market_data(coins_to_include=settings.COINS_TO_MONITOR):

    coin_part_of_url = '%2C'.join(coins_to_include)
    # response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin%2Clitecoin%2Cbitcoin-cash%2Ccardano%2Cpolkadot&vs_currencies=usd&include_24hr_change=true&include_last_updated_at=true')
    url = f'https://api.coingecko.com/api/v3/simple/price?ids={coin_part_of_url}&vs_currencies=usd&include_24hr_change=true&include_last_updated_at=true'
    response = requests.get(url)
    return json_loads(response.text)

# def get_desired_allocation(coin):
#
#     market_data = get_market_data(coins_to_include=[coin])
#     coin_spot_price = market_data[coin]['usd']
#     coin_pct_over_target = (coin_spot_price / settings.PRICE_TARGET[coin]) - 1
#
#     allocation = 1 - 1 / (1 + exp(-1 * min(25, max(3, round(1 / (0.03 + abs(coin_pct_over_target)), 2))) * coin_pct_over_target))
#     return round(100 * allocation, 1)
def get_coin_spot_price(coin):

    market_data = get_market_data(coins_to_include=[coin])
    return market_data[coin]['usd']

# def get_coin_price_relative_to_target(coin):
#
#     coin_spot_price = get_coin_spot_price(coin)
#     return (coin_spot_price / settings.PRICE_TARGET[coin]) - 1

def get_immediate_trading_price_target(spot_price, price_target):

    weight_for_med_term_target = 0.67
    return round(weight_for_med_term_target * price_target + (1 - weight_for_med_term_target) * spot_price, 3)

def get_coin_price_relative_to_target(spot_price, price_target):

    return round((spot_price / price_target) - 1, 3)

def get_desired_allocation(coin_price_relative_to_target):

    allocation = 1 - 1 / (1 + exp(-1 * min(25, max(3, round(1 / (0.03 + abs(coin_price_relative_to_target)), 2))) * coin_price_relative_to_target))
    return round(100 * allocation, 1)

# def insert_prices_into_database():
#     pass

# def get_moving_average(coin, days):
#     # Need to solve problem of how to deal with coin that does not yet have enough history in database to comply with number of days asked for
#
#     # Query coin's prices from the database over the previous number of days as specified
#
#     # Calculate coin's average price over specified number of days
#     pass

# def get_naive_price_target(coin):
#     # Need to solve problem of how to deal with coin that does not yet have enough history in database to comply with number of days asked for
#     return 0.25 * get_moving_average(coin=coin, days=5) + 0.5 * get_moving_average(coin=coin, days=15) + 0.25 * get_moving_average(coin=coin, days=90)

def add_percent_to_spot_price(spot_price, percent):
    return round(spot_price * (1 + percent / 100), 3)

def get_order(coins_to_buy_per_dollar_of_account_value, coin_price, account_value=1):
    if coins_to_buy_per_dollar_of_account_value < 0:
        return f'Sell {-1 * round(coins_to_buy_per_dollar_of_account_value * account_value, 3)} coins @ ${coin_price}'
    elif coins_to_buy_per_dollar_of_account_value > 0:
        return f'Buy {round(coins_to_buy_per_dollar_of_account_value * account_value, 3)} coins @ ${coin_price}'
    else:
        return ''

def get_allocation_report(coin):

    # Print out a spray of coin prices around the current spot price, and the desired allocation at each of those prices
    coin_spot_price = get_coin_spot_price(coin)
    coin_price_target_medium_term = settings.PRICE_TARGET[coin]
    coin_price_target_immediate = get_immediate_trading_price_target(spot_price=coin_spot_price, price_target=coin_price_target_medium_term)
    coin_price_relative_to_target = get_coin_price_relative_to_target(spot_price=coin_spot_price, price_target=coin_price_target_immediate)

    df = pd.DataFrame(data=[x * 0.5 for x in range(18, -19, -1)], columns=['Market Move'])
    df.index = df['Market Move']
    price_col_name = f'{coin.capitalize()} Price'
    df[price_col_name] = df.apply(lambda x: add_percent_to_spot_price(spot_price=coin_spot_price, percent=x['Market Move']), axis=1)
    df['Price Relative to Target'] = df.apply(
        lambda x: get_coin_price_relative_to_target(spot_price=x[price_col_name], price_target=coin_price_target_immediate), axis=1
    )
    df['Allocation %'] = df['Price Relative to Target'].apply(get_desired_allocation)
    df['Price % Over Target'] = df['Price Relative to Target'] * 100
    df['% to Buy'] = 0
    # df['% to Buy'][df['Market Move'] < 0] = df['Allocation %'].diff(periods=1)
    # df['% to Buy'][df['Market Move'] > 0] = df['Allocation %'].diff(periods=-1)
    df.loc[df['Market Move'] < 0, '% to Buy'] = df['Allocation %'].diff(periods=1)
    df.loc[df['Market Move'] > 0, '% to Buy'] = df['Allocation %'].diff(periods=-1)
    df['Coins to Buy (per dollar of account value)'] = (df['% to Buy'] * 1 / df[price_col_name]) / 100
    df['Order (per dollar of account value)'] = df.apply(
        lambda x: get_order(
            coins_to_buy_per_dollar_of_account_value=x['Coins to Buy (per dollar of account value)'],
            coin_price=x[price_col_name]
        ),
        axis = 1
    )

    df[f'Order (for ${settings.ACCOUNT_VALUE} account value)'] = df.apply(
        lambda x: get_order(
            coins_to_buy_per_dollar_of_account_value=x['Coins to Buy (per dollar of account value)'],
            coin_price=x[price_col_name],
            account_value=settings.ACCOUNT_VALUE
        ),
        axis = 1
    )

    print(f'Current price of {coin.capitalize()}: {coin_spot_price}')
    print(f'Medium-term price target for {coin.capitalize()}: {coin_price_target_medium_term}')
    print(f'Immediate trading price target for {coin.capitalize()}: {coin_price_target_immediate}\n')

    current_suggested_allocation = df['Allocation %'][df['Market Move'] == 0][0]
    print(f"All trades below assume your allocation is currently at {current_suggested_allocation}%, the suggested allocation for the current price.")
    print(f"If not, first make a trade to rebalance your allocation to {current_suggested_allocation}%.\n")

    print(df.drop(['Market Move', 'Price Relative to Target', 'Price % Over Target', '% to Buy', 'Coins to Buy (per dollar of account value)'], axis=1))
