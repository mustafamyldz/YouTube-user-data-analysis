import os
from copy import deepcopy
import pandas as pd
import googleapiclient.discovery
import googleapiclient.errors

from pandas import json_normalize

with open('config.txt', 'r') as file:
    key = file.read().strip()

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

df = pd.read_json('Takeout\\YouTube and YouTube Music\\history\\watch-history.json')

url_list = df.titleUrl.values.tolist()

modified_list = []


for item in url_list:
    # Convert the item to a string
    item_str = str(item)
    # Slice the string to remove the first n characters
    modified_item = item_str[32:]
    # Append the modified item to the new list
    modified_list.append(modified_item)

yeezus = deepcopy(modified_list)


def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "0"

    api_service_name = "youtube"
    api_version = "v3"
    api_key = key

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=api_key)

    yee=0

    df2 = pd.DataFrame()
    while yee <= len(yeezus):
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=yeezus[yee:yee+50]
        )
        response = request.execute()

        temp_df = pd.DataFrame(response['items'])

        df2 = pd.concat([df2, temp_df], ignore_index=True)

        print(yee)
        yee = yee+50


    df2.to_json(r'hist_df.json')



if __name__ == "__main__":
    main()
