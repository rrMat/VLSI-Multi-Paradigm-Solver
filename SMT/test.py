import csv


# Read CSV file
with open(r"C:\Users\matte\Desktop\project\Combinatorial_Project\SMT\Timings\parallel.csv") as fp:
    reader = csv.reader(fp, delimiter=" ", quotechar='"')
    # next(reader, None)  # skip the headers
    data_read = [row for row in reader]


print(data_read)