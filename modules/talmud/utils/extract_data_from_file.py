import pandas as pd

def extract_credentials(file):
    data = pd.read_excel(file, header=None)

    username = data.iloc[2, 0]
    password = data.iloc[2, 1]

    return username, password