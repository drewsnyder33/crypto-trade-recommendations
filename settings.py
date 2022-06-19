# COINS_TO_MONITOR = ['bitcoin', 'ethereum', 'cardano', 'litecoin', 'bitcoin-cash', 'polkadot']
COINS_TO_MONITOR = ['bitcoin', 'ethereum', 'cardano']

# Price targets
PRICE_TARGET = {
    'bitcoin': 48000,
    'ethereum': 1500,
    'cardano': .55 # 3/4-3/7: 1.23 | 3/8: 1.13 | 3/9-3/11: 1.17 | 3/13-3/14: 1.12 | 3/14-3/16 : 1.10 | 3/16: 1.14 | 6/3/2022: 1.37
}

# Account value, for trade sizing
# ACCOUNT_VALUE = 7500
ACCOUNT_VALUE = 5000

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# Inverse logistic allocation function parameters
# ------------------------------------------------------------------------------

# # Choose exponential aggressiveness parameter to be values like 5, 10, or 20,
# # where higher values cause allocations to change more drastically from one day
# # to the next
# EXPONENTIAL_AGGRESSIVENESS_PARAM = 20

# WEIGHT_PREVIOUS_DAYS_MARKET_MOVE = 0.25
# WEIGHT_SECURITY_LEVEL_VS_PRICE_TARGET = 1 - WEIGHT_PREVIOUS_DAYS_MARKET_MOVE
# ------------------------------------------------------------------------------
