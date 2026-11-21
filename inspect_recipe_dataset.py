
import pandas as pd
from pathlib import Path

file_path = Path(
    r"D:\pythonproject\AI_Meal_Grocery_Planner\recipes_extended.csv"
)

print("Loading dataset...")

df = pd.read_csv(
    file_path,
    encoding="utf-8",
    low_memory=False
)

print("\n========== DATASET INFORMATION ==========")
print("Shape:", df.shape)

print("\n========== COLUMN NAMES ==========")
for column in df.columns:
    print(f"- {column}")

print("\n========== DATA TYPES ==========")
print(df.dtypes)

print("\n========== FIRST 3 RECIPES ==========")
for index, row in df.head(3).iterrows():
    print(f"\nRecipe {index + 1}")
    for column in df.columns:
        print(f"{column}: {str(row[column])[:300]}")

