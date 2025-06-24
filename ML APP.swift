import pandas as pd 

f = pd.read_csv("study_habit_classifier_dataset.csv")

print(f.head())
print(f.columns) 

f.isnull().sum()
f.info()
f.describe(include='all')