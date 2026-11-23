
"""
csv_to_postgres.py
------------------
Load Nike_Sales_Uncleaned.csv into PostgreSQL.
Handles data cleaning, table creation and duplicate records.
"""

import pandas as pd
import psycopg2


# ------------------------------------------------
# 1. Configuration
# ------------------------------------------------

CSV_PATH = "Nike_Sales_Uncleaned.csv"

DB_CONFIG = {
    "host": "localhost",
    "database": "cleantable",
    "user": "postgres",
    "password": "root",
    "port": "5432"
}


# ------------------------------------------------
# 2. Date Cleaning Function
# ------------------------------------------------

def parse_mixed_date(x):

    if pd.isna(x):
        return None

    x = str(x).strip()

    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d"):

        try:
            return pd.to_datetime(x, format=fmt).date()

        except ValueError:
            continue

    return None


# ------------------------------------------------
# 3. Data Cleaning Function
# ------------------------------------------------

def clean_dataframe(df):

    # Remove truncated trailing rows
    df = df.dropna(
        subset=["Gender_Category", "Product_Line", "Product_Name"],
        how="all"
    ).copy()

    # Clean string columns
    str_cols = [
        "Gender_Category",
        "Product_Line",
        "Product_Name",
        "Size",
        "Sales_Channel",
        "Region"
    ]

    for col in str_cols:
        df[col] = df[col].astype("string").str.strip()

    # Standardise region names
    region_map = {
        "hyd": "Hyderabad",
        "hyderbad": "Hyderabad",
        "hyderabad": "Hyderabad",
        "bengaluru": "Bangalore",
        "bangalore": "Bangalore",
        "mumbai": "Mumbai",
        "pune": "Pune",
        "delhi": "Delhi",
        "kolkata": "Kolkata"
    }

    df["Region"] = (
        df["Region"].str.lower().map(region_map)
    )

    # Standardise sales channel
    df["Sales_Channel"] = df["Sales_Channel"].str.title()

    # Convert numeric columns
    num_cols = [
        "Units_Sold",
        "MRP",
        "Discount_Applied",
        "Revenue",
        "Profit"
    ]

    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Handle invalid values
    df.loc[df["Units_Sold"] < 0, "Units_Sold"] = pd.NA

    df.loc[
        (df["Discount_Applied"] < 0) |
        (df["Discount_Applied"] > 1),
        "Discount_Applied"
    ] = pd.NA

    # Handle zero revenue
    mask = (
        (df["Revenue"] == 0) &
        (df["Units_Sold"].fillna(0) != 0)
    )

    df.loc[mask, "Revenue"] = pd.NA

    # Convert mixed date formats
    df["Order_Date"] = df["Order_Date"].apply(parse_mixed_date)

    # Convert missing values to None
    df = df.astype(object).where(pd.notna(df), None)

    # Arrange columns
    return df[
        [
            "Order_ID",
            "Gender_Category",
            "Product_Line",
            "Product_Name",
            "Size",
            "Units_Sold",
            "MRP",
            "Discount_Applied",
            "Revenue",
            "Order_Date",
            "Sales_Channel",
            "Region",
            "Profit"
        ]
    ]


# ------------------------------------------------
# 4. Main CSV to PostgreSQL Function
# ------------------------------------------------

def csv_to_postgres():

    conn = None
    cursor = None

    try:

        # Step 1: Read CSV
        print(f"Reading {CSV_PATH} ...")

        df = pd.read_csv(CSV_PATH)

        print(f"Loaded {len(df):,} rows")

        # Step 2: Clean CSV
        df = clean_dataframe(df)

        print(f"Rows after cleaning: {len(df):,}")

        # Step 3: Connect PostgreSQL
        conn = psycopg2.connect(**DB_CONFIG)

        cursor = conn.cursor()

        print("Connected successfully!")

        # Step 4: Create table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nike_sales (
                order_id VARCHAR(50) PRIMARY KEY,
                gender_category VARCHAR(50),
                product_line VARCHAR(100),
                product_name VARCHAR(150),
                size VARCHAR(20),
                units_sold INTEGER,
                mrp NUMERIC(10,2),
                discount_applied NUMERIC(5,2),
                revenue NUMERIC(12,2),
                order_date DATE,
                sales_channel VARCHAR(50),
                region VARCHAR(100),
                profit NUMERIC(12,2)
            )
        """)

        # Step 5: Insert records
        insert_sql = """
            INSERT INTO nike_sales (
                order_id,
                gender_category,
                product_line,
                product_name,
                size,
                units_sold,
                mrp,
                discount_applied,
                revenue,
                order_date,
                sales_channel,
                region,
                profit
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)

            ON CONFLICT (order_id) DO NOTHING
        """

        inserted = 0
        skipped = 0

        for row in df.itertuples(index=False, name=None):

            cursor.execute(insert_sql, row)

            if cursor.rowcount == 1:
                inserted += 1
            else:
                skipped += 1

        # Step 6: Commit
        conn.commit()

        print("\nData import completed!")

        print(f"New records inserted: {inserted:,}")
        print(f"Duplicate records skipped: {skipped:,}")

        # Step 7: Verify records
        cursor.execute("SELECT COUNT(*) FROM nike_sales")

        total_records = cursor.fetchone()[0]

        print(f"\nTotal records in PostgreSQL: {total_records:,}")

        # Check NULL dates
        cursor.execute("""
            SELECT COUNT(*)
            FROM nike_sales
            WHERE order_date IS NULL
        """)

        null_dates = cursor.fetchone()[0]

        print(f"Records with NULL dates: {null_dates:,}")

    except Exception as e:

        if conn:
            conn.rollback()

        print("\nError occurred:", e)

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

        print("\nDatabase connection closed!")


# ------------------------------------------------
# 5. Standalone Execution
# ------------------------------------------------

if __name__ == "__main__":

    csv_to_postgres()
