import os
import pandas as pd
import datetime

def generateNewestIronConorsEV(folder_name):
    try:
        # Set the path to the files directory in your project folder
        data_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), ".", folder_name)

        # Get the list of CSV files in the files directory
        csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]

        # Find the most recent CSV file based on the file creation time
        newest_file = max(csv_files, key=lambda f: os.path.getctime(os.path.join(data_dir, f)))
        # Load the CSV file into a DataFrame
        df = pd.read_csv(os.path.join(data_dir, newest_file))

        df['Probability'] = df['Probability'].str.strip('%').astype(float) / 100

        df['ExpectedValue'] = (df['Max Profit'] * df['Probability']) + ((df['Max Loss'] * -1) * (1 - df['Probability']))
        df = df.sort_values(by=['ExpectedValue'], ascending=False)

        # Save the DataFrame with the ExpectedValue column to a new CSV file with today's date as the filename
        today = datetime.date.today().strftime('%Y-%m-%d')
        result_file = os.path.join(data_dir, f'{today}.csv')
        df.to_csv(result_file, index=False)

        # Load the CSV file back into a new DataFrame that contains the ExpectedValue column
        df = pd.read_csv(result_file)

        # Calculate the Kelly Criterion and add it as a new column
        bp = df['Max Profit'] / df['Max Loss']
        q = df['Probability']
        b = 1 - q
        df['KellyCriterion'] = (bp * q - b) / bp

        # Save the DataFrame with the KellyCriterion column to the same CSV file with today's date as the filename
        df.to_csv(result_file, index=False)
    except:
        return("No data available")


# generateNewestIronConorsEV("BearCall")
# generateNewestIronConorsEV("BullPut")
# generateNewestIronConorsEV("IronCon")