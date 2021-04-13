import csv 

if __name__=='__main__':
    with open('nobase.txt', 'r') as in_file:
        stripped = (line.strip() for line in in_file)
        lines = (line.split(",") for line in stripped if line)
        with open('nobase.csv', 'w') as out_file:
            writer = csv.writer(out_file)
            writer.writerow(('ID', 'info'))
            writer.writerows(lines)