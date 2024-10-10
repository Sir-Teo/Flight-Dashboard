import pandas as pd

def load_and_process_data(file_path):
    data = pd.read_csv(file_path)
    # No aggregation needed, use the provided columns directly
    return data
