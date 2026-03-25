import pandas as pd

df = pd.read_csv("Dissertation/Albert Skalinski - Dissertation/data/originalData.csv")

sampleDF = df.sample(n = 1000, random_state = 42)
sampleDF.to_csv("Dissertation/Albert Skalinski - Dissertation/data/sampleData.csv", index = False)