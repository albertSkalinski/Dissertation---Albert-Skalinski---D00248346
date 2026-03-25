# Importing necessary libraries
import pandas as pd

# Reading in the original dataset
df = pd.read_csv("Dissertation/Albert Skalinski - Dissertation/data/originalData.csv")

# Sampling the dataset (one thousand songs, seed -> 42)
# Source for the code below: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.sample.html
sampleDF = df.sample(n = 500, random_state = 42) # The first batch -> seed = 42.

# Outputting the sampled dataset
sampleDF.to_csv("Dissertation/Albert Skalinski - Dissertation/data/sampledData.csv", index = False)