import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

compounds = ['Caffeine', 'Emtricitabine', 'Propranolol', 'Fluconazole', 'Fluoxetine', 'Caffeine Isotope',
             'Emtricitabine Isotope', 'Propranolol Isotope', 'Fluconazole Isotope', 'Fluoxetine Isotope']


def prepare_ml_file(clean_file, compromised_file, new_file_path, n_clean, n_compromised):
    """Combines the clean and compromised datasets, averages scan-by-scan values to represent ROI and saves and returns
    the combined dataframe"""
    df1 = pd.read_csv(clean_file, header=0)  # Reads in clean QC data CSV file as dataframe1
    df2 = pd.read_csv(compromised_file, header=0)  # Reads in compromised QC data CSV file as dataframe2

    clean_list = ['Clean' for c in range(int(n_clean))]  # Creates list of 'Clean' of length equal to the number clean ROIs
    compromised_list = ['Compromised' for i in range(int(n_compromised))]  # Creates list of 'Compromised' of length equal to the number compromised ROIs

    df1 = df1.drop('Scan', axis=1)  # Drops scan number column from dataframe1
    df2 = df2.drop('Scan', axis=1)  # Drops scan number column from dataframe2

    df4 = pd.DataFrame()  # Creates empty dataframe as dataframe4
    df5 = pd.DataFrame()  # Creates empty dataframe as dataframe5

    df4.insert(0, 'Condition', clean_list) # Adds column in the first position called Condition with the values from clean_list to dataframe4
    df5.insert(0, 'Condition', compromised_list)  # Adds column in the first position called Condition with the values from compromised_list to dataframe5

    """Averaging scan values to represent as a single ROI value"""
    index = 1  # Set initial index to 1
    for column in df1.columns:  # Iterates through the columns of dataframe1
        column_lst = []  # Creates empty list as column_lst
        start = 0  # Sets initial start value to 0
        end = 400  # Sets initial end value to 4000
        for _ in range(int(df1.shape[0]/400)):  # Iterates for as many sets of 400 rows in the dataset. ex. 800 rows in data set this will happen twice (800/400=2)
           column_lst.append(np.mean(df1[column][start:end])) # Adds the mean of the values from the start row (0 first iteration) to the end row (400 first iteration) for the current column to the list column_lst
           start += 400  # Increases the start value by 400
           end += 400  # Increases the end value by 400
        df4.insert(index, column, column_lst)  # Adds current column at the current index position to dataframe4 with the mean values from column_lst
        index += 1

    index = 1
    for column in df2.columns:  # Same as above comments with dataframe2 and dataframe5
        column_lst = []
        start = 0
        end = 400
        for _ in range(int(df2.shape[0]/400)):
           column_lst.append(np.mean(df2[column][start:end]))
           start += 400
           end += 400
        df5.insert(index, column, column_lst)
        index += 1

    drop_cols = [x + ' m/z' for x in compounds]  # Creates a list with the m/z column names to be dropped later

    df_final = pd.concat([df4, df5], axis=0)  # Combines dataframe4 and dataframe5
    df_final = df_final.drop(columns=['File', 'Day'] + drop_cols, axis=1)  # Drops file, day, and all m/z columns from final dataframe

    df_final.to_csv(new_file_path, index=False)  # Saves final dataframe to a CSV file without row numbers

    return df_final


def split_and_scale_ml_data(combined_data, test_size):
    """Takes combined dataset, splits it into training and testing sets based on the given test size. Returns
    the training and testing dataframes."""
    X = combined_data.drop('Condition', axis=1)  # Saves all columns except Condition as X
    y = combined_data["Condition"]  # Saves Condition column as y

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=float(test_size), random_state=100) # Splits data into training and testing sets in a 67:33 split respectively

    scaler = StandardScaler()  # Initiates StandardScaler as scaler (z-scaling)
    scaler.fit(X_train, y_train)  # Fits the scaler to the training data
    X_train_scaled = scaler.transform(X_train)  # Scales training data
    X_test_scaled = scaler.transform(X_test)  # Scales testing data based on training data

    scaled_train_df = pd.DataFrame(X_train_scaled, index=X_train.index, columns=X_train.columns)  # Creates dataframe containing the scaled X training data
    scaled_train_df.insert(0, 'Condition', y_train)  # Adds y training labels to the training dataframe
    scaled_train_df = scaled_train_df.sort_values(by=['Condition'])  # Sorts rows of training dataframe according to Condition values

    scaled_test_df = pd.DataFrame(X_test_scaled, index=X_test.index, columns=X_test.columns)  # Creates dataframe containing the scaled X testing data
    scaled_test_df.insert(0, 'Condition', y_test)  # Adds y testing labels to the testing dataframe
    scaled_test_df = scaled_test_df.sort_values(by=['Condition'])  # Sorts rows of testing dataframe according to Condition values

    return scaled_train_df, scaled_test_df


def save_train_test_sets(scaled_train_df, scaled_test_df, train_file_path, test_file_path):
    """Saves training and testing sets to csv files at given locations"""
    scaled_train_df.to_csv(train_file_path, index=False)  # Saves training dataframe as a CSV file without row numbers
    scaled_test_df.to_csv(test_file_path, index=False)  # Saves testing dataframe as a CSV file without row numbers
