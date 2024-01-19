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
def get_all_liked_videos(youtube):
    liked_videos = []
    request = youtube.videos().list(part="snippet", myRating="like", maxResults=50)
    while request is not None:
        response = request.execute()
        liked_videos += response.get('items', [])
        request = youtube.videos().list_next(request, response)
    return liked_videos
def extract_video_ids(liked_videos):
    return [video['id'] for video in liked_videos]
def add_liked_column(df, liked_video_ids):
    df['liked'] = df['id'].isin(liked_video_ids)
    return df

def main():
    youtube = youtube_authenticate()
    liked_videos = get_all_liked_videos(youtube)
    liked_video_ids = extract_video_ids(liked_videos)

    # Load your existing DataFrame
    df = pd.read_csv('hist_cleaned.csv')  # Adjust the file path as needed

    # Add the 'liked' column
    df = add_liked_column(df, liked_video_ids)

    # Save or process your updated DataFrame
    df.to_csv('hist_with_likes.csv', index=False)  # Save to a new CSV file

if __name__ == "__main__":
    main()
