from library import *


TEAM_ID = '6A3CSCZ9M6'
KEY_ID = '2VLJH6R856'
PRIVATE_KEY_PATH = r'D:\AuthKey_2VLJH6R856.p8'

def generate_apple_music_token():
    with open(PRIVATE_KEY_PATH, "r") as key_file:
        private_key = key_file.read()

    payload = {
        "iss": TEAM_ID,
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
    }

    token = jwt.encode(payload, private_key, algorithm="ES256", headers={"alg": "ES256", "kid": KEY_ID})
    return token

APPLE_MUSIC_TOKEN = generate_apple_music_token()

def get_album_tracks(album_id, storefront="us"):
    url = f"https://api.music.apple.com/v1/catalog/{storefront}/albums/{album_id}/tracks"
    headers = {"Authorization": f"Bearer {APPLE_MUSIC_TOKEN}"}
    tracks = []

    while url:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            break
        data = response.json()
        for track in data.get("data", []):
            try:
                attributes = track.get("attributes", {})
                tracks.append({
                    "album_id": album_id,
                    "tracklist(danh sách bài hát)": attributes.get("name"),
                    "apple music": attributes.get("url"),
                    "Song artist(nghệ sĩ tham gia bài hát)": ", ".join(
                        [artist["attributes"]["name"] for artist in track.get("relationships", {}).get("artists", {}).get("data", [])]
                    ) if track.get("relationships", {}).get("artists") else attributes.get("artistName", "None")
                })
            except Exception as e:
                print(f"Lỗi khi xử lý track: {e}")

        url = data.get("next")
        if url and not url.startswith("http"):
            url = f"https://api.music.apple.com{url}"

    return tracks


def get_artist_albums(artist_id, storefront="us"):
    url = f"https://api.music.apple.com/v1/catalog/{storefront}/artists/{artist_id}/albums"
    headers = {"Authorization": f"Bearer {APPLE_MUSIC_TOKEN}"}
    albums = []

    while url:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            break
        data = response.json()
        for album in data.get("data", []):
            try:
                attributes = album.get("attributes", {})
                if not attributes:
                    continue

                album_id = album.get("id")
                album_name = attributes.get("name", "Unknown Album")
                genre = ", ".join(attributes.get("genreNames", [])) or "Unknown"
                album_url = attributes.get("url", "")
                is_single = attributes.get("isSingle", False)
                release_date = attributes.get("releaseDate", "1970-01-01")
                distribute = attributes.get("copyright", "Unknown")

                tracks = get_album_tracks(album_id, storefront)
                num_tracks = len(tracks)

                if is_single or num_tracks <= 3:
                    medium = "Single"
                elif 4 <= num_tracks <= 6:
                    medium = "EP"
                else:
                    medium = "Regular"

                albums.append({
                    "album_id": album_id,
                    "album_name": album_name,
                    "release_date": release_date,
                    "medium": medium,
                    "genre": genre,
                    "album_url": album_url,
                    "distribute": distribute,
                })
            except Exception as e:
                print(f"Lỗi khi xử lý album: {e}")

        url = data.get("next")
        if url and not url.startswith("http"):
            url = f"https://api.music.apple.com{url}"

    return albums



def get_artist_name(artist_id, storefront="us"):
    url = f"https://api.music.apple.com/v1/catalog/{storefront}/artists/{artist_id}"
    headers = {"Authorization": f"Bearer {APPLE_MUSIC_TOKEN}"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json().get("data", [])
        if data:
            return data[0]["attributes"]["name"]
    return artist_id

import re  # thêm ở đầu file nếu chưa có

def clean_distribute(copyright_text):
    if not copyright_text:
        return "Unknown"
    # Xoá chuỗi bắt đầu bằng "℗ " và năm (4 chữ số)
    cleaned = re.sub(r"^℗\s*\d{4}\s*", "", copyright_text).strip()
    return cleaned if cleaned else "Unknown"

def get_artist_tracks_dataframe(artist_id):
    albums_data = get_artist_albums(artist_id)
    tracks_data = []

    with ThreadPoolExecutor() as executor:
        results = executor.map(lambda album: get_album_tracks(album["album_id"]), albums_data)

        for album, track_list in zip(albums_data, results):
            for track in track_list:
                try:
                    distribute_raw = album.get("distribute", "")
                    distribute_clean = clean_distribute(distribute_raw)

                    track.update({
                        "album_name": album.get("album_name"),
                        "album type(loại album)":"digital",
                        "release_date": album.get("release_date", "1970-01-01"),
                        "status_code": "Normal",
                        "class": "DIGITAL",
                        "genre": album.get("genre", "Unknown"),
                        "medium": album.get("medium", "Unknown"),
                        "distribute": distribute_clean,
                    })
                    tracks_data.append(track)
                except Exception as e:
                    print(f"Lỗi khi gộp thông tin track: {e}")

    df_tracks_apple = pd.DataFrame(tracks_data)
    df_tracks_apple["release_date"] = pd.to_datetime(df_tracks_apple["release_date"], errors="coerce").dt.strftime("%d/%m/%Y")
    artist_name = get_artist_name(artist_id).replace(" ", "_")
    column_order = [
        "album_id",
        "album_name",
        "album type(loại album)",
        "tracklist(danh sách bài hát)",
        "Song artist(nghệ sĩ tham gia bài hát)",
        "release_date",
        "status_code",
        "class",
        "genre",
        "medium",
        "distribute",
        "apple music",
        "album_url",
    ]
    # Chỉ giữ những cột có tồn tại thực tế trong DataFrame
    column_order = [col for col in column_order if col in df_tracks_apple.columns]
    df_tracks_apple = df_tracks_apple[column_order]
    df_tracks_apple.drop_duplicates(subset=["album_id", "tracklist(danh sách bài hát)"], inplace=True)
    return df_tracks_apple, artist_name

