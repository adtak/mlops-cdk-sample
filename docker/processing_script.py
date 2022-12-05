import csv


def main() -> None:
    print("Start processing.")
    with open("/opt/ml/processing/input/input.csv") as f:
        reader = csv.reader(f)
        input = [i for i in reader]
    print(f"Input: {input}")
    with open("/opt/ml/processing/output/output.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(input)
    print("Finish processing.")


if __name__ == "__main__":
    main()
