import requests
import pandas as pd
from datetime import datetime, timedelta
import zipfile
import io

def fetch_caiso_prices(start_date, end_date, node='TH_NP15_GEN-APND', verbose=True):
    """
    Fetch day-ahead LMP prices from CAISO
    
    Args:
        start_date: 'YYYYMMDD' format
        end_date: 'YYYYMMDD' format  
        node: CAISO node name (default is NP15 trading hub)
    """
    
    base_url = "http://oasis.caiso.com/oasisapi/SingleZip"
    
    params = {
        'queryname': 'PRC_LMP',
        'startdatetime': f'{start_date}T00:00-0000',
        'enddatetime': f'{end_date}T00:00-0000',  # Changed from 23:00 to 00:00
        'version': '1',
        'market_run_id': 'DAM',
        'node': node,
        'resultformat': '6'
    }
    
    print(f"Fetching data from {start_date} to {end_date}...")
    
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        if verbose:
            print("Data downloaded successfully!")
        return response.content
    else:
        print(f"Error: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        return None

import xml.etree.ElementTree as ET

def fetch_multiple_months(start_date, end_date, node='TH_NP15_GEN-APND'):
    from datetime import timedelta
    import time

    all_data = []
    current_start = start_date
    chunk_num = 0

    while current_start < end_date:
        chunk_num += 1
        current_end = min(current_start + timedelta(days=30), end_date)

        start_str = current_start.strftime('%Y%m%d')
        end_str = current_end.strftime('%Y%m%d')

        print(f"\n[Chunk {chunk_num}] Fetching: {start_str} to {end_str}")
        
        data = fetch_caiso_prices(start_str, end_str, node, verbose=False)

        if data:
            df_chunk = extract_and_parse_zip(data)
            all_data.append(df_chunk)
            print(f"[Chunk {chunk_num}] success - {len(df_chunk)} records")
        else:
            print(f"[Chunk {chunk_num}] FAILED")

        current_start = current_end + timedelta(days=1)

        #Delay to avoid rate-limiting
        if current_start < end_date:
            time.sleep(2)
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        print(f"Total records fetched: {len(combined_df)}")
        return combined_df
    else:
        return None

def extract_and_parse_zip(zip_content):
    """
    Extract CSV from ZIP and load into pandas DataFrame
    """
    # Open the ZIP file from memory
    with zipfile.ZipFile(io.BytesIO(zip_content)) as z:
        print("Files in ZIP:", z.namelist())
        
        # Get the first file
        data_file = z.namelist()[0]
        print(f"Reading file: {data_file}")
        
        # Read it into pandas
        with z.open(data_file) as f:
            df = pd.read_csv(f)
            
    return df

def save_to_csv(df, filename='caiso_prices.csv'):
    """
    Save DataFrame to CSV file
    """
    # Create data directory if it doesn't exist
    import os
    os.makedirs('data', exist_ok=True)
    
    filepath = f'data/{filename}'
    df.to_csv(filepath, index=False)
    print(f"Data saved to {filepath}")
    return filepath

def validate_completeness(df, start_date, end_date):
    from datetime import timedelta

    lmp_data = df[df['LMP_TYPE'] == 'LMP'].copy()

    lmp_data['timestamp'] = pd.to_datetime(lmp_data['INTERVALSTARTTIME_GMT'])
    lmp_data = lmp_data.sort_values('timestamp')

    total_days = (end_date - start_date).days
    expected_hours = total_days*24
    actual_hours = len(lmp_data)

    print("\n" + "="*60)
    print("DATA COMPLETENESS CHECK")
    print("="*60)
    print(f"Date range: {start_date.date()} to {end_date.date()}")
    print(f"Expected hours: {expected_hours}")
    print(f"Actual hours: {actual_hours}")
    print(f"Completeness: {(actual_hours/expected_hours)*100:.1f}%")

    if actual_hours < expected_hours:
        print(f"\n Missing {expected_hours - actual_hours} hours of data")

        lmp_data['time_diff'] = lmp_data['timestamp'].diff()
        gaps = lmp_data[lmp_data['time_diff'] > timedelta(hours=1)]

        if len(gaps) > 0:
            print(f"\nFound {len(gaps)} gap(s):")
            for idx, row in gaps.iterrows():
                print(f"  Gap detected at: {row['timestamp']}")
    else:
        print("\n Data is complete.")

    return actual_hours == expected_hours
    
#DEBUG
def explore_xml(zip_content):
    """
    Explore the XML structure to understand it
    """
    with zipfile.ZipFile(io.BytesIO(zip_content)) as z:
        xml_file = z.namelist()[0]
        with z.open(xml_file) as f:
            xml_content = f.read()
    
    # Parse and print first 2000 characters to see structure
    print("XML Content Preview:")
    print(xml_content.decode('utf-8')[:2000])
    print("\n" + "="*50 + "\n")
    
    # Parse it
    root = ET.fromstring(xml_content)
    
    # Print root tag and attributes
    print(f"Root tag: {root.tag}")
    print(f"Root attributes: {root.attrib}")
    
    # Print all children of root
    print("\nDirect children of root:")
    for child in root:
        print(f"  - {child.tag}")
        # Print their children too
        for grandchild in child:
            print(f"      - {grandchild.tag}")

#testing
if __name__ == "__main__":
    from datetime import datetime, timedelta

    #calculate and format dates
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)

    print(f"Fetching data from {start_date.date()} to {end_date.date()}")
    
    # Fetch all data
    df = fetch_multiple_months(start_date, end_date)

    if df is not None:
        is_complete = validate_completeness(df, start_date, end_date)

        print(f"\nDataFrame shape: {df.shape}")
        save_to_csv(df, 'caiso_prices_90days.csv')