import pandas as pd
import os
import numpy as np
import csv
from datetime import datetime



def data_extract():
  data = "data"
  p_vs = [d for d in os.listdir(data) if os.path.isdir(os.path.join(data, d))]
  DCCT1_booster_current = p_vs.pop(p_vs.index("BO-DI-DCCT1_getDcctCurrent"))
  p_vs.append( DCCT1_booster_current)
  return p_vs, data


def intervals_extract():
  with open("intervals.txt", "r") as intervalsFile:
      lines = [line.strip() for line in intervalsFile if line.strip()]
  intervals = []
  for line in lines:
     start_str, end_str = line.split("#")
     start_pre_form = datetime.strptime(start_str, "%Y-%m-%dT%H:%M:%S.%fZ")
     start_formated = start_pre_form.strftime("%Y.%m.%d %H:%M:%S")
     end_pre_form = datetime.strptime(end_str, "%Y-%m-%dT%H:%M:%S.%fZ")
     end_formated = end_pre_form.strftime("%Y.%m.%d %H:%M:%S")
     start = pd.Timestamp(start_formated)
     end = pd.Timestamp(end_formated)
     ts_range = pd.date_range(start=start, end=end, freq="1s")
     intervals.append(ts_range)
  return intervals


def data_unstamped(intervals, p_vs, data):
 unstamped_data = []
 for i in range(len(intervals)):
    unstamped_data_for_single_interval = []
    for parameter in p_vs:
        file_path = os.path.join(data, parameter , f"interval{str(i+1)}")
        with open(file_path , "r") as DataFile:
            lines = [float(line.strip()) for line in DataFile]
            unstamped_data_for_single_interval.append(lines)
    unstamped_data.append(unstamped_data_for_single_interval)
    unstamped_data_array = np.array(unstamped_data, dtype=object)
 return unstamped_data_array


def data_stamping(intervals, p_vs, unstamped_data):
  stamped_data = []
  for i in range(len(intervals)):
     stamped_data_for_single_interval = []
     for j in range(len(intervals[i])):
         stamped_data_for_single_stamp = [intervals[i][j]]
         for k in range(len(p_vs)):
             stamped_data_for_single_stamp.append(unstamped_data[i][k][j])
         stamped_data_for_single_interval.append(stamped_data_for_single_stamp)
     #print(np.array(stamped_data_for_single_interval).shape)
     print(f"Interval {i+1}: {np.array(stamped_data_for_single_interval, dtype=object).shape}")
     stamped_data.append(stamped_data_for_single_interval)
     stamped_data_array = np.array(stamped_data, dtype=object)
     #print(stamped_data_array.shape)
  return stamped_data_array



#print(stamped_data_array.shape)
#print(stamped_data_array[0][0][:27])
#print(len(stamped_data_array))
#print(p_vs)


def csv_writing(stamped_data_array, p_vs):
 CSV_dir = "CSVFiles"
 os.makedirs(CSV_dir, exist_ok=True)
 for i in range(len(stamped_data_array)):
    CSVfile = os.path.join(CSV_dir, f"interval{i+1}.csv")
    with open(CSVfile, mode = 'w', newline= "") as csvfile:
        csvwriter = csv.writer(csvfile)
        header = ["Timestamp"] + p_vs
        csvwriter.writerow(header)
        for row in stamped_data_array[i]:
            csvwriter.writerow(row)


    print(f"Interval {i+1} written to {CSVfile}")
    

def main():
  p_vs, data = data_extract()
  intervals = intervals_extract()
  unstamped_data = data_unstamped(intervals, p_vs, data)
  stamped_data_array = data_stamping(intervals, p_vs, unstamped_data)
  csv_writing(stamped_data_array, p_vs)


if __name__ == "__main__":
    main()