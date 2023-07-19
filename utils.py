import glob
import os
import pandas as pd
from sklearn.model_selection import train_test_split


def read_dataset(train_feature_path):
    if train_feature_path.startswith("/"):
        # local file
        if '*' in train_feature_path:
            return pd.concat(map(pd.read_csv, glob.glob(os.path.join('', train_feature_path))))
        else:
            return pd.read_csv(train_feature_path)
    else:
        raise Exception("remote files is unsupported")


# assume that the first column is the label
def prepare_dataset(train_df, seed, test_size):
    # drop column label
    X_data = train_df.drop('is_attribute', axis=1)
    y = train_df.is_attribute

    # Split the dataset into train and Test
    return train_test_split(
        X_data, y, test_size=test_size, random_state=seed
    )
