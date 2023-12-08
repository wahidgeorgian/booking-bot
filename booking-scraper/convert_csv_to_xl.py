import pandas as pd

# for conversion csv to excel

read_csv = pd.read_csv("results/booking_all_data.csv")
save_xlx = read_csv.to_excel("results/booking_all_data.xlsx")