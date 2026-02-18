import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def csv_to_dataframe(csv_dir, csv_file):
    csv_path = os.path.join(csv_dir, csv_file)
    df = pd.read_csv(csv_path)
    df = df.drop(columns=["Timestamp"], errors='ignore')
    return df

def pv_vs_pv(df, x_col, y_col, title):
    plt.figure(figsize=(12, 6))
    plt.plot(df[x_col], df[y_col], label=y_col)
    plt.title(title)
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
    plt.tight_layout()
    plt.show()

def plot_all_pvs(df, title="All PV Plot"):
    plt.figure(figsize=(14, 7))
    for col in df.columns:
        plt.plot(df.index, df[col], label=col)
    plt.title(title)
    plt.xlabel("Iteration")
    plt.ylabel("Values")
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
    plt.tight_layout()
    plt.show()

def plot_single_pv(df, pv_name, title="Single PV Plot"):
    if pv_name not in df.columns:
        raise ValueError(f"PV '{pv_name}' does not exist in the dataframe.")
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df[pv_name], label=pv_name)
    plt.title(title)
    plt.xlabel("Iteration")
    plt.ylabel("Value")
    plt.legend()
    plt.tight_layout()
    #plt.show(block=False)
    #plt.pause(1)  # Pause to allow the plot to update
    


def main():
    csv_dir = "CSVFiles"  # Adjust the directory path if needed
    #csv_file = "interval1.csv"  # Replace with the desired CSV file
    df = []
    files = [f for f in os.listdir(csv_dir) if os.path.isfile(os.path.join(csv_dir, f))]
    for i in range(len(files)):
        csv_file = f"interval{i+1}.csv"
        d_f = csv_to_dataframe(csv_dir, csv_file)
        df.append(d_f)
    df = pd.concat(df, ignore_index=True)
    pvs_names = list(df.columns)
    pvs_number = len(pvs_names)
    for i in range(pvs_number):
        pv_to_plot = pvs_names[i]
        plot_single_pv(df, pv_to_plot, title=f"Plot for {pv_to_plot}")
    plt.show()
    #pv_to_plot = "BO-PS-QF_getGain"  # Replace with the desired column name
    #plot_single_pv(df, pv_to_plot)
    #pv_vs_pv(df, "BO-PS-QF_getGain", "BO-DI-DCCT1_getDcctCurrent", "QF vs DCCT Plot")


if __name__ == "__main__":
    main()
