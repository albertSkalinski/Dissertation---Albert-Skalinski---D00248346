import os
import time
import base64
import requests
import pandas as pd

CLIENT_ID = "d1fa3ead0baf487790ebc846061c18fb"
CLIENT_SECRET = "d9c194a04a2b48688f705e358111fdf8"

TOKEN_URL = "https://accounts.spotify.com/api/token"
TRACK_URL = "https://api.spotify.com/v1/tracks/{track_id}"


def get_access_token(client_id: str, client_secret: str) -> str:
    auth_str = f"{client_id}:{client_secret}"
    auth_b64 = base64.b64encode(auth_str.encode()).decode()

    r = requests.post(
        TOKEN_URL,
        headers={
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={"grant_type": "client_credentials"},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["access_token"]


def get_track_release_date(track_id: str, token: str, max_retries: int = 3) -> dict:
    if pd.isna(track_id) or str(track_id).strip() == "":
        return {
            "track_id": track_id,
            "release_date": None,
            "release_year": None,
            "release_date_precision": None,
            "status": "missing_track_id",
        }

    track_id = str(track_id).strip()

    for attempt in range(max_retries):
        r = requests.get(
            TRACK_URL.format(track_id=track_id),
            headers={"Authorization": f"Bearer {token}"},
            timeout=30,
        )

        print(f"track_id={track_id} status={r.status_code}")

        if r.status_code == 429:
            retry_after = int(r.headers.get("Retry-After", 2))
            print(f"Rate limited on {track_id}. Retry-After: {r.headers.get('Retry-After')} seconds")
            time.sleep(retry_after)
            continue

        if r.status_code == 401 and attempt < max_retries - 1:
            token = get_access_token(CLIENT_ID, CLIENT_SECRET)
            continue

        if r.status_code == 404:
            return {
                "track_id": track_id,
                "release_date": None,
                "release_year": None,
                "release_date_precision": None,
                "status": "not_found",
            }

        r.raise_for_status()
        data = r.json()

        release_date = data["album"].get("release_date")
        precision = data["album"].get("release_date_precision")

        year = None
        if release_date and len(release_date) >= 4:
            try:
                year = int(release_date[:4])
            except ValueError:
                year = None

        return {
            "track_id": track_id,
            "release_date": release_date,
            "release_year": year,
            "release_date_precision": precision,
            "status": "ok",
        }

    return {
        "track_id": track_id,
        "release_date": None,
        "release_year": None,
        "release_date_precision": None,
        "status": "failed_after_retries",
    }


def add_release_dates_to_df(df: pd.DataFrame, track_id_col: str = "track_id") -> pd.DataFrame:
    if track_id_col not in df.columns:
        raise ValueError(f"Column '{track_id_col}' not found in DataFrame")

    token = get_access_token(CLIENT_ID, CLIENT_SECRET)

    results = []
    for track_id in df[track_id_col]:
        row = get_track_release_date(track_id, token)
        results.append(row)

    release_df = pd.DataFrame(results)

    # merge back onto original df
    out_df = df.merge(release_df, on="track_id", how="left")
    return out_df


# Example usage
if __name__ == "__main__":
    # input CSV must have a column called track_id
    df = pd.read_csv("Dissertation/Albert Skalinski - Dissertation/data/sampledDataBatch2.csv")

    out_df = add_release_dates_to_df(df, track_id_col="track_id")

    # save result
    out_df.to_csv("Dissertation/Albert Skalinski - Dissertation/data/sampledDataWithDatesBatch2.csv", index=False)

    print(out_df.head())