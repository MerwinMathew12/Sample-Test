import pandas as pd

# ---------------------------------------------------------------
# 1. Load
# ---------------------------------------------------------------
df = pd.read_csv("Nike_Sales_Uncleaned.csv")

# Drop rows that are entirely empty except Order_ID (truncated tail rows)
df = df.dropna(subset=["Gender_Category", "Product_Line", "Product_Name"], how="all")

# ---------------------------------------------------------------
# 2. Strip whitespace from string columns
# ---------------------------------------------------------------
str_cols = ["Gender_Category", "Product_Line", "Product_Name", "Size",
            "Sales_Channel", "Region"]
for c in str_cols:
    df[c] = df[c].astype("string").str.strip()

# ---------------------------------------------------------------
# 3. Normalise Region (casing + spelling variants)
# ---------------------------------------------------------------
region_map = {
    "hyd": "Hyderabad", "hyderbad": "Hyderabad", "hyderabad": "Hyderabad",
    "bengaluru": "Bangalore", "bangalore": "Bangalore",
    "mumbai": "Mumbai", "pune": "Pune", "delhi": "Delhi",
    "kolkata": "Kolkata",
}
df["Region"] = df["Region"].str.lower().map(region_map)

# ---------------------------------------------------------------
# 4. Normalise Sales_Channel
# ---------------------------------------------------------------
df["Sales_Channel"] = df["Sales_Channel"].str.title()   # Online / Retail

# ---------------------------------------------------------------
# 5. Parse mixed date formats
# ---------------------------------------------------------------
def parse_date(x):
    if pd.isna(x):
        return pd.NaT
    x = str(x).strip()
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d"):
        try:
            return pd.to_datetime(x, format=fmt)
        except ValueError:
            continue
    return pd.NaT

df["Order_Date"] = df["Order_Date"].apply(parse_date)

# ---------------------------------------------------------------
# 6. Numeric coercion
# ---------------------------------------------------------------
num_cols = ["Units_Sold", "MRP", "Discount_Applied", "Revenue", "Profit"]
for c in num_cols:
    df[c] = pd.to_numeric(df[c], errors="coerce")

# ---------------------------------------------------------------
# 7. Size: separate numeric size from letter size
# ---------------------------------------------------------------
def clean_size(s):
    if pd.isna(s):
        return pd.NA
    s = str(s).strip()
    # numeric sizes kept as int-like strings
    try:
        return str(int(float(s)))
    except ValueError:
        return s.upper()

df["Size"] = df["Size"].apply(clean_size)

# ---------------------------------------------------------------
# 8. Fix invalid Units_Sold (negatives -> NaN)
# ---------------------------------------------------------------
df.loc[df["Units_Sold"] < 0, "Units_Sold"] = pd.NA

# ---------------------------------------------------------------
# 9. Fix Discount_Applied outside [0, 1]
#     - values > 1 look like they were entered as e.g. 1.17
#       meaning 17%?  No reliable rule -> flag them as NaN
#       (keeps data honest rather than inventing values)
# ---------------------------------------------------------------
df.loc[(df["Discount_Applied"] < 0) | (df["Discount_Applied"] > 1),
       "Discount_Applied"] = pd.NA

# ---------------------------------------------------------------
# 10. Revenue: 0.0 with missing Units/MRP is not a real sale
#     - keep 0.0 only when Units_Sold == 0
# ---------------------------------------------------------------
mask_zero_rev = (df["Revenue"] == 0) & (df["Units_Sold"].fillna(0) != 0)
df.loc[mask_zero_rev, "Revenue"] = pd.NA

# ---------------------------------------------------------------
# 11. Duplicate Order_IDs
#     Strategy: keep the row with the most non-null fields
#     (fallback: keep first)
# ---------------------------------------------------------------
df["_nonnull"] = df.notna().sum(axis=1)
df = (df.sort_values("_nonnull", ascending=False)
        .drop_duplicates(subset="Order_ID", keep="first")
        .drop(columns="_nonnull")
        .sort_values("Order_ID")
        .reset_index(drop=True))

# ---------------------------------------------------------------
# 12. Final dtype housekeeping
# ---------------------------------------------------------------
df["Order_ID"] = df["Order_ID"].astype("int64")
df["Units_Sold"] = df["Units_Sold"].astype("Int64")   # nullable int
for c in ["MRP", "Discount_Applied", "Revenue", "Profit"]:
    df[c] = df[c].astype("float64")

# ---------------------------------------------------------------
# 13. Save
# ---------------------------------------------------------------
df.to_csv("Nike_Sales_Cleaned.csv", index=False)
print(df.info())
print(df.head())