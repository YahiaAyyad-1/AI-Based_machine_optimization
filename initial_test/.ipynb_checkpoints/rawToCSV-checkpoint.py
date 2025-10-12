import pandas as pd
import os
import numpy as np
import csv

data = "data"

parameters = [d for d in os.listdir(data) if os.path.isdir(os.path.join(data, d))]

DCCT1_BoosterCurrent = parameters.pop(15)
parameters.append( DCCT1_BoosterCurrent)



with open("intervals.txt", "r") as intervalsFile:
    
    lines = [line.strip() for line in intervalsFile if line.strip()]


intervals = []



for line in lines:

    start_str, end_str = line.split("#")

    start = pd.Timestamp(start_str)

    end = pd.Timestamp(end_str)

    ts_range = pd.date_range(start=start, end=end, freq="1S")

    intervals.append(ts_range)





UnStampedData = []


for i in range(len(intervals)):

    UnStampedDataForSingleInterval = []

    for parameter in parameters:


        file_path = os.path.join(data, parameter , f"interval{str(i+1)}")

        with open(file_path , "r") as DataFile:

            lines = [float(line.strip()) for line in DataFile]

            UnStampedDataForSingleInterval.append(lines)


    UnStampedData.append(UnStampedDataForSingleInterval)

    






StampedData = []

for i in range(len(intervals)):

    StampedDataForSingleInterval = []


    for j in range(len(intervals[i])):

        StampedDataForSingleStamp = [intervals[i][j]]


        for k in range(len(parameters)):

            StampedDataForSingleStamp.append(UnStampedData[i][k][j])
            

        StampedDataForSingleInterval.append(StampedDataForSingleStamp)


    print(np.array(StampedDataForSingleInterval).shape)
    
    print(f"Interval {i+1}: {np.array(StampedDataForSingleInterval, dtype=object).shape}")


    StampedData.append(StampedDataForSingleInterval)


StampedDataArray = np.array(StampedData, dtype=object)

print(StampedDataArray.shape)

print(StampedDataArray[0][0][:27])

print(len(StampedDataArray))

print(parameters)



CSV_dir = "CSVFiles"

os.makedirs(CSV_dir, exist_ok=True)

for i in range(len(StampedDataArray)):

    CSVfile = os.path.join(CSV_dir, f"interval{i+1}.csv")

    with open(CSVfile, mode = 'w', newline= "") as csvfile:

        csvwriter = csv.writer(csvfile)

        header = ["Timestamp"] + parameters

        csvwriter.writerow(header)


        for row in StampedDataArray[i]:

            csvwriter.writerow(row)


    #print(f"Interval {i+1} written to {CSVfile}")
    




