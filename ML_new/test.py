import pandas as pd

df = pd.DataFrame(columns={"Potatoes", "Tomatoes"})
df.loc[len(df),:] = [3,4]
df.loc[len(df),:] = [3,5]
print(df)
print(df[(df['Tomatoes']==3) & (df['Potatoes']==4)])
