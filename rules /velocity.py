# rules/velocity.py
def velocity_rule(df):
    return df.filter(df.velocity > 5)
