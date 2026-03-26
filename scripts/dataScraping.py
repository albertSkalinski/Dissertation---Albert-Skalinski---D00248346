# The script below has been generated with ChatGPT
# Sources: https://chatgpt.com/share/69c4fb95-09cc-8390-b715-5c30969797d0
#          https://chatgpt.com/share/69c4fe84-e40c-838d-8fd2-8064be4892bf

# Importing necessary libraries
import os
from dotenv import load_dotenv
import time
import base64
import requests
import pandas as pd

# Declaring the ID and the secret key, which are stored as environmental variables
load_dotenv("Dissertation/Albert Skalinski - Dissertation/misc/variables.env")
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# Raising an error in case of missing credentials
if not CLIENT_ID or not CLIENT_SECRET:
    raise ValueError("Missing Spotify credentials.")

# Necessary URLs
TOKEN_URL = "https://accounts.spotify.com/api/token"
TRACK_URL = "https://api.spotify.com/v1/tracks/{track_id}"

# Getting the token to access Spotify's database
def getAccessToken(clientID : str, clientSecret : str) -> str:
    authStr = f"{clientID}:{clientSecret}"
    authb64 = base64.b64encode(authStr.encode()).decode()

    r = requests.post(TOKEN_URL, headers = {"Authorization" : f"Basic {authb64}",
                     "Content-Type" : "application/x-www-form-urlencoded",}, data = {"grant_type" : "client_credentials"},
                     timeout = 30,)
    r.raise_for_status()
    return r.json()["access_token"]

# Scraping the release date
def getTrackReleaseDate(trackID : str, token : str, maxRetries : int = 3) -> dict:
    if pd.isna(trackID) or str(trackID).strip() == "":
        return {"track_id" : trackID, "release_date" : None, "release_year" : None, "release_date_precision" : None,
               "status" : "missing_track_id",}

    trackID = str(trackID).strip()

    # Sending a request
    for attempt in range(maxRetries):
        r = requests.get(TRACK_URL.format(track_id = trackID), headers = {"Authorization" : f"Bearer {token}"}, timeout = 30,)

        # Checking the current track the script is working on (and its status)
        print(f"track_id = {trackID}, status = {r.status_code}")

        # The rate is limited
        if r.status_code == 429:
            retryAfter = int(r.headers.get("Retry-After", 2))
            print(f"Rate limited on {trackID}. Retry-After: {r.headers.get("Retry-After")} seconds")
            time.sleep(retryAfter)
            continue
        
        # Authorisation issue
        if r.status_code == 401 and attempt < maxRetries - 1:
            token = getAccessToken(CLIENT_ID, CLIENT_SECRET)
            continue
        
        # Invalid/missing track_id
        if r.status_code == 404:
            return {"track_id" : trackID, "release_date" : None, "release_year" : None, "release_date_precision" : None,
                   "status" : "not_found",}

        r.raise_for_status()
        data = r.json()

        releaseDate = data["album"].get("release_date")
        precision = data["album"].get("release_date_precision")

        year = None
        if releaseDate and len(releaseDate) >= 4:
            try:
                year = int(releaseDate[:4])
            except ValueError:
                year = None

        return {"track_id" : trackID, "release_date" : releaseDate, "release_year" : year, "release_date_precision" : precision,
               "status" : "ok",}

    return {"track_id" : trackID, "release_date" : None, "release_year" : None, "release_date_precision" : None,
           "status" : "failed_after_retries",}

# Creating a dataframe out of scraped data
def makeDF(df : pd.DataFrame, trackIDColumn : str = "track_id") -> pd.DataFrame:
    if trackIDColumn not in df.columns:
        raise ValueError(f"Column '{trackIDColumn}' not found in the DataFrame")

    token = getAccessToken(CLIENT_ID, CLIENT_SECRET)

    results = []
    for trackID in df[trackIDColumn]:
        row = getTrackReleaseDate(trackID, token)
        results.append(row)

    releaseDF = pd.DataFrame(results)

    outDF = df.merge(releaseDF, on = "track_id", how = "left")
    return outDF

# Actually making the files with the logic above
if __name__ == "__main__":
    df = pd.read_csv("Dissertation/Albert Skalinski - Dissertation/data/sampledDataBatch1.csv")
    outDF = makeDF(df, trackIDColumn = "track_id")

    # Saving the results to a .csv file
    outDF.to_csv("Dissertation/Albert Skalinski - Dissertation/data/sampledDataWithDatesBatch2.csv", index = False)

    print(outDF.head())