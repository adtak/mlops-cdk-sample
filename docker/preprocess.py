import csv
import os


def main():
    print("Start preprocessing.")
    with open("./input.csv") as f:
        reader = csv.reader(f)
        input = [i for i in reader]
    output = ["".join(i) for i in input]
    os.makedirs("output")
    with open("./output/output.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(output)
    print("Finish preprocessing.")


if __name__ == "__main__":
    main()
