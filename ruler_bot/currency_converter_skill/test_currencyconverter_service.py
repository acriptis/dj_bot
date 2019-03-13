from currency_converter import CurrencyConverter
c = CurrencyConverter()
print(c.convert(1, 'USD', 'RUB'))
print(c.currencies)
# {'ZAR', 'INR', 'PHP', 'CHF', 'BGN', 'EUR',
# 'MXN', 'SKK', 'DKK', 'IDR', 'NOK', 'HRK', 'ILS',
# 'KRW', 'SIT', 'ISK', 'RON', 'CNY', 'TRL', 'SGD',
# 'USD', 'NZD', 'CYP', 'SEK', 'RUB', 'BRL', 'ROL',
# 'HUF', 'AUD', 'THB', 'MYR', 'JPY', 'LTL', 'EEK',
# 'CAD', 'GBP', 'PLN', 'LVL', 'MTL', 'CZK', 'HKD',
# 'TRY'}