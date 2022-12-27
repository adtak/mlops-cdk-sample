import pickle

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split


def main() -> None:
    print("Start training.")
    df = pd.read_csv("/opt/ml/input/data/data.csv")
    X = df.values[:, :-1]
    y = df.values[:, -1]
    X_train, _, y_train, _ = train_test_split(X, y, test_size=0.2)
    model = LinearRegression().fit(X_train, y_train)
    with open("/opt/ml/model/model.pickle", "wb") as f:
        pickle.dump(model, f)
    print("Finish training.")


if __name__ == "__main__":
    main()
