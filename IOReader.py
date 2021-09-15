import pandas as pd

data = pd.DataFrame()

def open_file(filename):
    try:
        data = pd.read_csv(filename)
    except IOError:
        print("File not found!")
    finally:
        return data