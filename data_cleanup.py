import pandas as pd
import isodate

# Load the dataset
file_path = 'hist_df.json'  # Replace with your file path
df = pd.read_json(file_path)

# Extract nested data
df_snippet = pd.json_normalize(df['snippet'])
df_content_details = pd.json_normalize(df['contentDetails'])
df_statistics = pd.json_normalize(df['statistics'])

# Merge extracted data
df_cleaned = pd.concat([df.drop(['snippet', 'contentDetails', 'statistics'], axis=1),
                        df_snippet, df_content_details, df_statistics], axis=1)

# Convert duration to total seconds
df_cleaned['duration_sec'] = df_cleaned['duration'].apply(lambda x: isodate.parse_duration(x).total_seconds())

# Convert numerical strings to integers
numerical_columns = ['viewCount', 'likeCount', 'favoriteCount', 'commentCount']
if 'dislikeCount' in df_cleaned.columns:
    numerical_columns.append('dislikeCount')
df_cleaned[numerical_columns] = df_cleaned[numerical_columns].apply(pd.to_numeric, errors='coerce', axis=1)

df_cleaned.to_csv('hist_cleaned.csv')
