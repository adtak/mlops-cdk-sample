import csv


def main():
    with open("./input.csv") as f:
        reader = csv.reader(f)
        input = [i for i in reader]
    output = [i+"_out" for i in input]
    with open("./output.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(output)


if __name__ == "__main__":
    main()
