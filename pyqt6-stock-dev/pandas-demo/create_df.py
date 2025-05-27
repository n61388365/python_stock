import pandas as pd


my_dict = {
    'timestamp': [1748568600000,1748568660000],
    'amount_total': [1.968652e+10, 2.591950e+10],
    'sh_sz_amount_total': [564.21, 725.69],
    'sh_sz_amount_total_change': [121.57, 89.35],
    'sh_sz_amount_total_change_diff': [0.00, -32.23],
    'sh_sz_amount_total_last': [442.63, 636.35]
}

df = pd.DataFrame(my_dict)
print(df)