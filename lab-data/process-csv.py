import pandas as pd

# Read the CSV file with specific parameters
df = pd.read_csv('sample-data.csv',
                 encoding='utf-8',
                 escapechar='\\',
                 quotechar='"')

# Convert to Parquet format
# You can optionally compress the output
df.to_parquet('sample-data.parquet',
              compression='snappy')  # snappy is a good balance between compression and speed
