from datasets import load_dataset
import pandas as pd
import ast

print("Downloading MAMS data...")
dataset = load_dataset("NEUDM/mams", trust_remote_code=True)

print("Converting to initial DataFrames...")
df_train_raw = pd.DataFrame(dataset["train"])
df_val_raw = pd.DataFrame(dataset["validation"])

# Sanity Checks
print("--- Actual Columns ---")
print(df_train_raw.columns.tolist())
print(f"Training Raw Samples: {len(df_train_raw)}")
print(f"Validation Raw Samples: {len(df_val_raw)}")


def parsing_data(source_df) -> pd.DataFrame:
    transformed_data = []

    rows = source_df.to_dict("records")
    skipped_rows = 0

    for r in rows:
        # extract sentence
        raw_input = r["input"]
        # Handle cases where input might be a list or a string
        sentence = raw_input[0] if isinstance(raw_input, list) else raw_input

        # extract aspect and sentiment
        try:
            aspect_pairs = ast.literal_eval(r["output"])
        except:
            skipped_rows += 1
            continue

        # create new row for each aspect found in the sentence
        for pair in aspect_pairs:
            if len(pair) < 2:
                continue

            aspect = pair[0]
            sentiment_str = pair[1]

            transformed_data.append(
                {
                    "text": sentence,
                    "aspect": aspect,
                    "label": sentiment_str,
                }
            )

    if skipped_rows > 0:
        print(f"⚠️  Total count of skipped rows: {skipped_rows}")

    return pd.DataFrame(transformed_data)


# Execution
print("\nParsing Training Data...")
df_train_parsed = parsing_data(df_train_raw)
print(f"✅ Successfully extracted {len(df_train_parsed)} training pairs.")
print(df_train_parsed.head())

print("\nParsing Validation Data...")
df_val_parsed = parsing_data(df_val_raw)
print(f"✅ Successfully extracted {len(df_val_parsed)} validation pairs.")

# Save
print("-" * 50)
df_train_parsed.to_csv("Data/mams_train_parsed.csv", index=False)
df_val_parsed.to_csv("Data/mams_val_parsed.csv", index=False)
print("✅ Files saved to disk.")
