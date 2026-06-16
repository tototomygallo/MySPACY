import pandas as pd
from scipy.stats import pearsonr

df_entr = pd.read_csv("ENTR_SPACY_SW.csv")
df_lsm  = pd.read_csv("LSM_SPACY_SW.csv")

# merge
df = df_lsm.merge(df_entr, on="archivo", how="inner")

# limpieza
df = df.dropna()

print("Diálogos finales:", len(df))

# correlación entre métricas
r1, p1 = pearsonr(df["lsm_model"], df["entr1"])
r2, p2 = pearsonr(df["lsm_model"], df["entr2"])

print("\nLSM vs ENTR1")
print("r =", r1, "p =", p1)

print("\nLSM vs ENTR2")
print("r =", r2, "p =", p2)