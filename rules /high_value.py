# rules/high_value.py
def high_value_rule(df):
    return df.filter(df.amount > 10000)
