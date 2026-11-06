                     ################ EDA ######################

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# FILE PATH
FILE_PATH = r"C:\Users\prash\OneDrive\Desktop\Medical_Inventory_Masked dataset.xlsx"
EDA_OUTPUT_PATH = r"C:\Users\prash\OneDrive\Desktop\Numeric_EDA_Report.xlsx"

# READ DATA
data = pd.read_excel(FILE_PATH)

#  FIRST MOMENT OF BUSINESS DECISION

# Mean
columns_to_calculate_mean = ['Quantity', 'ReturnQuantity', 'Final_Cost', 'Final_Sales', 'RtnMRP']
mean_values = data[columns_to_calculate_mean].mean()
print("Mean Values:\n", mean_values, "\n")

# Median
columns_to_calculate_median = ['Quantity', 'ReturnQuantity', 'Final_Cost', 'Final_Sales', 'RtnMRP']
median_values = data[columns_to_calculate_median].median()
print("Median Values:\n", median_values, "\n")

# Mode
columns_to_calculate_mode = [
    'Typeofsales', 'DrugName', 'SubCat', 'SubCat1',
    'Quantity', 'ReturnQuantity', 'Final_Cost', 'Final_Sales', 'RtnMRP'
]

print("\n---- Mode Values ----")
mode_values = {}  # ✅ create dictionary to store modes
for column in columns_to_calculate_mode:
    if column in data.columns:
        mode_column = data[column].mode()
        if not mode_column.empty:
            mode_val = mode_column.iloc[0]
            mode_values[column] = mode_val
            print(f"Mode of {column}: {mode_val}")
        else:
            mode_values[column] = None
            print(f"Mode of {column}: No mode found")
    else:
        print(f"⚠️ Column '{column}' not found in dataset")


#  SECOND MOMENT OF BUSINESS DECISION

# Variance
columns_to_calculate_var = ['Quantity', 'ReturnQuantity', 'Final_Cost', 'Final_Sales', 'RtnMRP']
var_values = data[columns_to_calculate_var].var()
print("Variance Values:\n", var_values, "\n")

# Standard Deviation
column_to_calculate_std = ['Quantity', 'ReturnQuantity', 'Final_Cost', 'Final_Sales', 'RtnMRP']
std_values = data[column_to_calculate_std].std()
print("Standard Deviation Values:\n", std_values, "\n")

# Range
columns_to_calculate_range = ['Quantity', 'ReturnQuantity', 'Final_Cost', 'Final_Sales', 'RtnMRP']
range_values = {}
for column in columns_to_calculate_range:
    column_range = data[column].max() - data[column].min()
    range_values[column] = column_range

print("Range Values:")
for column, value in range_values.items():
    print(f"Range of {column}: {value}")
print("\n")

# Minimum
columns_to_calculate_min = ['Quantity', 'ReturnQuantity', 'Final_Cost', 'Final_Sales', 'RtnMRP']
min_values = data[columns_to_calculate_min].min()
print("Minimum Values:\n", min_values, "\n")

# Maximum
columns_to_calculate_max = ['Quantity', 'ReturnQuantity', 'Final_Cost', 'Final_Sales', 'RtnMRP']
max_values = data[columns_to_calculate_max].max()
print("Maximum Values:\n", max_values, "\n")

#  THIRD MOMENT OF BUSINESS DECISION 

# Skewness
columns_to_calculate_skewness = ['Quantity', 'ReturnQuantity', 'Final_Cost', 'Final_Sales', 'RtnMRP']
skew_values = data[columns_to_calculate_skewness].skew()
print("Skewness Values:\n", skew_values, "\n")

# Visualization for Final_Cost
plt.figure(figsize=(8, 5))
sns.histplot(data['Final_Cost'], kde=True, color='orange', bins=20)
plt.title("Distribution of Final_Cost (shows skewness)")
plt.xlabel("Final_Cost")
plt.ylabel("Frequency")
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()

skew_value = data['Final_Cost'].skew()
print(f"Skewness of Final_Cost: {skew_value:.2f}\n")

#  FOURTH MOMENT OF BUSINESS DECISION 

columns_to_calculate_kurtosis = ['Quantity', 'ReturnQuantity', 'Final_Cost', 'Final_Sales', 'RtnMRP']
kurt_values = data[columns_to_calculate_kurtosis].kurt()
print("Kurtosis Values:\n", kurt_values)



# Convert mode dictionary to a pandas Series (only for numeric columns that exist)
mode_series = pd.Series(mode_values)
mode_series = mode_series.reindex(columns_to_calculate_mean)  # keep order consistent

summary_data = pd.DataFrame({
    "Mean": mean_values,
    "Median": median_values,
    "Mode": mode_series,
    "Variance": var_values,
    "Std_Dev": std_values,
    "Range": pd.Series(range_values),
    "Skewness": skew_values,
    "Kurtosis": kurt_values
})

# Reset index for clean display
summary_data.reset_index(inplace=True)
summary_data.rename(columns={"index": "Column"}, inplace=True)

#  DISPLAY & SAVE 
print("\n--- FULL NUMERICAL EDA REPORT ---")
print(summary_data.to_markdown(index=False))

# Save to Excel
try:
    summary_data.to_excel(EDA_OUTPUT_PATH, index=False, float_format="%.4f")
    print(f"\n✅ EDA Report SAVED SUCCESSFULLY to: {EDA_OUTPUT_PATH}")
except Exception as e:
    print(f"\n❌ ERROR saving Excel file. Check path or permissions: {e}")

























