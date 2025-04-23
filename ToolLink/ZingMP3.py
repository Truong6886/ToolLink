from library import *

def normalize_string(s):
    return re.sub(r'[^a-zA-Z0-9]', '', s.lower())

def fetch_artist_songs(artist_name):
    url = f"http://localhost:5000/api/artistsongs?name={artist_name}"
    response = requests.get(url)

    if response.status_code != 200:
        print("Error fetching data:", response.status_code)
        return None

    data = response.json()
    songs = data.get("songs", [])

    records = []
    album_tracks = defaultdict(set)

    for song in songs:
        album_link = song.get("albumLink", "")
        album_name = song.get("album") or song.get("title", "N/A")
        tracklist = song.get("tracklist") or [{"title": song.get("title", "N/A"), "link": song.get("link", "N/A")}]
        album_type = song.get("albumType", "Unknown")
        album_id = song.get("albumId", "Unknown")

        for track in tracklist:
            track_title = track.get("title", "N/A")
            album_tracks[album_id].add(track_title)

            records.append({
                "album_name": album_name,
                "album type (loại album)": "digital",
                "Album artist (nghệ sĩ sở hữu album)*": song.get("albumOwner", "Unknown"),
                "tracklist(danh sách bài hát)": track_title,
                "Song artist(nghệ sĩ tham gia bài hát)": song.get("featuredArtists", "Unknown"),
                "release_date": song.get("releaseDate", "Unknown"),
                "distribute": song.get("providedBy", "Unknown"),
                "status_code":"Normal",
                "class":"DIGITAL",
                "medium": album_type,
                "Mã định danh album zingmp3": album_id,
                "ZingMP3": track.get("link", "N/A"),
            })

    df = pd.DataFrame(records)
    df.drop_duplicates(subset=["Mã định danh album zingmp3", "tracklist(danh sách bài hát)"], inplace=True)

    # Thêm các cột chuẩn hoá để sắp xếp chính xác
    df['normalized_album_name'] = df['album_name'].apply(normalize_string)
    df['normalized_track_title'] = df['tracklist(danh sách bài hát)'].apply(normalize_string)

    # Sắp xếp theo album trước, sau đó theo tên bài hát trong album (A-Z)
    df.sort_values(by=["normalized_album_name", "normalized_track_title"], ascending=[True, True], inplace=True)

    df.drop(columns=["normalized_album_name", "normalized_track_title"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    
    return df
