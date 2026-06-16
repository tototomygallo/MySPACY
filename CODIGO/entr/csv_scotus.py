import pandas as pd
from scipy.stats import pearsonr

df_entr = pd.read_csv("ENTR_SPACY_SCOTUS.csv")
df_lsm  = pd.read_csv("LSM_SPACY_SCOTUS.csv")

# merge
df = df_lsm.merge(df_entr, on="id_virtual", how="inner")

# limpieza
df = df.dropna()

print("Pares finales:", len(df))

# correlación entre métricas
r1, p1 = pearsonr(df["lsm_model"], df["entr1"])
r2, p2 = pearsonr(df["lsm_model"], df["entr2"])

print("\nLSM vs ENTR1")
print("r =", r1, "p =", p1)

print("\nLSM vs ENTR2")
print("r =", r2, "p =", p2)