import csv
import os
import pathlib


def main():
    print("Start processing.")
    with open("/opt/ml/processing/input/input.csv") as f:
        reader = csv.reader(f)
        input = [i for i in reader]
    print(f"Input: {input}")
    output_dir = pathlib.Path("/opt/ml/processing/output/")
    os.makedirs(output_dir, exist_ok=True)
    with open(output_dir / "output.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(input)
    print("Finish processing.")


if __name__ == "__main__":
    main()
