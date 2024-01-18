import csv
import numpy as np
with open("./pattern_raw.csv", "r") as f:
        pattern = [int(int(row[1])/1.5) for row in csv.reader(f) if row[1] != "job_name"]
days = []
for i in range(7):
    days.append(np.array(pattern[i*24: (i+1)*24]))
days = np.array(days)
days = list(np.mean(days, axis=0))
days = days + [days[0]]

with open("./pattern.csv", "w") as f:
      writer = csv.writer(f)
      writer.writerow(["hour", "rate"])
      for id, val in enumerate(days):
            writer.writerow([id, val])