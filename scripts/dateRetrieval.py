import os
import time
import requests
import pandas as pd

CLIENT_ID = "66082423e3be4c50ad36b900d23557a9"
CLIENT_SECRET = "a216d7b36dd246ec92f82549880338ad"

INPUT_CSV = "Dissertation/Albert Skalinski - Dissertation/data/sampledData.csv"
OUTPUT_CSV = "Dissertation/Albert Skalinski - Dissertation/data/sampledDataWithDates.csv"
TRACK_ID_COLUMN = "track_id"


def get_access_token(client_id: str, client_secret: str) -> str:
    url = "https://accounts.spotify.com/api/token"
    response = requests.post(
        url,
        data={"grant_type": "client_credentials"},
        auth=(client_id, client_secret),
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["access_token"]

def get_track_release_info(track_id: str, token: str) -> dict:
    url = f"https://api.spotify.com/v1/tracks/{track_id}"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers, timeout=30)

    if response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", 2))
        time.sleep(retry_after)
        response = requests.get(url, headers=headers, timeout=30)

    if response.status_code == 404:
        return {
            "release_date": None,
            "release_date_precision": None,
            "release_year": None,
            "album_name": None,
            "spotify_error": "not_found",
        }

    response.raise_for_status()
    data = response.json()

    album = data.get("album", {})
    release_date = album.get("release_date")
    release_date_precision = album.get("release_date_precision")
    album_name = album.get("name")

    release_year = None
    if release_date and len(release_date) >= 4:
        try:
            release_year = int(release_date[:4])
        except ValueError:
            release_year = None

    return {
        "release_date": release_date,
        "release_date_precision": release_date_precision,
        "release_year": release_year,
        "album_name": album_name,
        "spotify_error": None,
    }


def main():
    df = pd.read_csv(INPUT_CSV)

    if TRACK_ID_COLUMN not in df.columns:
        raise ValueError(f"Column '{TRACK_ID_COLUMN}' not found in CSV")

    token = get_access_token(CLIENT_ID, CLIENT_SECRET)

    release_dates = []
    precisions = []
    years = []
    album_names = []
    errors = []

    for i, track_id in enumerate(df[TRACK_ID_COLUMN].astype(str)):
        try:
            info = get_track_release_info(track_id, token)
        except requests.HTTPError as e:
            # token may have expired or another API issue occurred
            if getattr(e.response, "status_code", None) == 401:
                token = get_access_token(CLIENT_ID, CLIENT_SECRET)
                info = get_track_release_info(track_id, token)
            else:
                info = {
                    "release_date": None,
                    "release_date_precision": None,
                    "release_year": None,
                    "album_name": None,
                    "spotify_error": f"http_{getattr(e.response, 'status_code', 'unknown')}",
                }
        except Exception as e:
            info = {
                "release_date": None,
                "release_date_precision": None,
                "release_year": None,
                "album_name": None,
                "spotify_error": str(e),
            }

        release_dates.append(info["release_date"])
        precisions.append(info["release_date_precision"])
        years.append(info["release_year"])
        album_names.append(info["album_name"])
        errors.append(info["spotify_error"])

        if (i + 1) % 100 == 0:
            print(f"Processed {i + 1} tracks")

    df["release_date"] = release_dates
    df["release_date_precision"] = precisions
    df["release_year"] = years
    df["album_name"] = album_names
    df["spotify_error"] = errors

    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Saved: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()