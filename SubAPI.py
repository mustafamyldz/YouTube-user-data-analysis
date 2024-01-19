import os
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pandas as pd

def youtube_authenticate():
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secret.json",
                scopes=["https://www.googleapis.com/auth/youtube.readonly"]
            )
            flow.run_local_server(port=8080, prompt="consent", authorization_prompt_message="")
            creds = flow.credentials
            with open("token.pickle", "wb") as token:
                pickle.dump(creds, token)

    return build("youtube", "v3", credentials=creds)
def get_all_subscribed_channels(youtube):
    subscribed_channels = []
    request = youtube.subscriptions().list(part="snippet", mine=True, maxResults=50)
    while request is not None:
        response = request.execute()
        subscribed_channels += response.get('items', [])
        request = youtube.subscriptions().list_next(request, response)
    return subscribed_channels
def extract_channel_ids(subscribed_channels):
    return [channel['snippet']['resourceId']['channelId'] for channel in subscribed_channels]
def add_subscribed_column(df, subscribed_channel_ids):
    df['subscribed'] = df['channelId'].isin(subscribed_channel_ids)
    return df

def main():
    youtube = youtube_authenticate()
    subscribed_channels = get_all_subscribed_channels(youtube)
    subscribed_channel_ids = extract_channel_ids(subscribed_channels)

    # Load your existing DataFrame
    df = pd.read_csv('hist_cleaned.csv')  # Adjust the file path as needed

    # Check if the 'channelId' column exists in df
    if 'channelId' not in df.columns:
        print("The DataFrame does not contain a 'channelId' column.")
        return

    # Add the 'subscribed' column
    df = add_subscribed_column(df, subscribed_channel_ids)

    # Save or process your updated DataFrame
    df.to_csv('hist_with_subscriptions.csv', index=False)  # Save to a new CSV file

if __name__ == "__main__":
    main()
