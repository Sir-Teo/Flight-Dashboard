import pandas as pd

def load_and_process_data(file_path):
    data = pd.read_csv(file_path)
    grouped_data = data.groupby(['Client Name', 'country_code_origin', 'origincity_code', 'origincity_lat', 'origincity_long', 'competitors'])['Depart Days Count'].agg(['sum']).reset_index()
    return grouped_data