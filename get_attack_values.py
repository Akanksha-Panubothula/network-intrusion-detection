import pandas as pd

df = pd.read_csv(
    "preprocessing/final/deduplicated_dataset.csv"
)

features = [
    "Source Port",
    "Destination Port",
    "Protocol",
    "Flow Duration",
    "Total Fwd Packets",
    "Total Backward Packets",
    "Total Length of Fwd Packets",
    "Total Length of Bwd Packets",
    "Flow Bytes/s",
    "Flow Packets/s"
]

# Choose an attack
attack_name = "DDoS"

attack_rows = df[
    df["Label"].astype(str).str.strip().str.lower()
    == attack_name.lower()
]

print("Number of DDoS records:", len(attack_rows))

if len(attack_rows) > 0:

    row = attack_rows.iloc[0]

    print("\n========== DDoS SAMPLE ==========\n")

    for feature in features:
        print(feature, "=", row[feature])

    print("\nLabel =", row["Label"])

else:
    print("DDoS label not found.")

    print("\nAvailable labels:")
    print(df["Label"].unique())