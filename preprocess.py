# preprocess.py
import pandas as pd
import datetime as dt
import os

def preprocess_and_save_data(input_file='data/online_retail_II.CSV'):
    """
    Performs the heavy, one-time data processing and saves the results
    to efficient Parquet files.
    """
    if not os.path.exists('assets'):
        os.makedirs('assets')
        
    print("Starting pre-processing...")
    
    print("Loading raw data...")
    df = pd.read_csv(input_file, encoding="ISO-8859-1", dtype={'Customer ID': str, 'Invoice': str})
    
    print("Cleaning data...")
    df.dropna(subset=['Customer ID'], inplace=True)

    # --- ** THE FIX IS HERE: Filter out manual adjustments and non-product entries ** ---
    # Convert Description to lowercase to make matching easier
    df['Description_lower'] = df['Description'].str.lower()
    
    # Create a list of keywords that indicate a non-product entry
    non_product_keywords = [
        'adjustment', 'manual', 'postage', 'discount', 'bank charges', 
        'credit', 'write off', 'carriage', 'dotcom', 'amazon fee'
    ]
    
    # Create a filter condition (a "boolean mask")
    is_non_product = df['Description_lower'].str.contains('|'.join(non_product_keywords), na=False)
    
    # Keep only the rows where the condition is NOT met
    print(f"Removing {is_non_product.sum()} non-product entries...")
    df = df[~is_non_product]
    
    # We can now drop the temporary lowercase column
    df.drop(columns=['Description_lower'], inplace=True)
    # --- END OF FIX ---

    df = df[~df['Invoice'].str.startswith('C', na=False)]
    df = df[(df['Quantity'] > 0) & (df['Price'] > 0)]
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    df['TotalPrice'] = df['Quantity'] * df['Price']
    df['InvoiceYearMonth'] = df['InvoiceDate'].dt.to_period('M').astype(str)

    print("Creating sales data subset...")
    sales_data = df[['Country', 'Customer ID', 'InvoiceYearMonth', 'Description', 'Quantity', 'TotalPrice']].copy()

    print("Calculating RFM data...")
    snapshot_date = df['InvoiceDate'].max() + dt.timedelta(days=1)
    rfm_data = df.groupby('Customer ID').agg({
        'InvoiceDate': lambda date: (snapshot_date - date.max()).days,
        'Invoice': 'nunique',
        'TotalPrice': 'sum'
    }).rename(columns={'InvoiceDate': 'Recency', 'Invoice': 'Frequency', 'TotalPrice': 'MonetaryValue'})
    
    rfm_data['R_Score'] = pd.qcut(rfm_data['Recency'], 5, labels=[5, 4, 3, 2, 1])
    rfm_data['F_Score'] = pd.qcut(rfm_data['Frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
    rfm_data['M_Score'] = pd.qcut(rfm_data['MonetaryValue'], 5, labels=[1, 2, 3, 4, 5])
    rfm_data['Segment'] = (rfm_data['R_Score'].astype(str) + rfm_data['F_Score'].astype(str))
    segment_map = {
        r'[1-2][1-2]': 'Hibernating', r'[1-2][3-4]': 'At Risk', r'[1-2]5': 'Cannot Lose',
        r'3[1-2]': 'About to Sleep', r'33': 'Needs Attention', r'[3-4][4-5]': 'Loyal Customers',
        r'41': 'Promising', r'51': 'New Customers', r'[4-5][2-3]': 'Potential Loyalists',
        r'5[4-5]': 'Champions'
    }
    rfm_data['Segment'] = rfm_data['Segment'].replace(segment_map, regex=True)
    rfm_data.reset_index(inplace=True)
    
    print("Saving processed data to Parquet files...")
    sales_data.to_parquet('assets/sales_data.parquet')
    rfm_data.to_parquet('assets/rfm_data.parquet')
    
    print("Pre-processing complete! Files saved in 'assets' folder.")

if __name__ == '__main__':
    preprocess_and_save_data()