from library import *
def get_artist_tracks_all(artist_name):
    client_id = "c7e1fe3ffe674920a01f9b016e6ae5df"
    client_secret = "215c6808dea74656b3629b306182ac4b"
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

    # 🔎 Tìm nghệ sĩ theo tên
    results = sp.search(q=artist_name, type='artist', limit=1)
    if not results['artists']['items']:
        print(f"Không tìm thấy nghệ sĩ với tên '{artist_name}'.")
        return pd.DataFrame()

    artist_id = results['artists']['items'][0]['id']

    track_data = []
    seen_tracks = set()

    offset = 0
    while True:
        albums = sp.artist_albums(artist_id, album_type='album,single,compilation', limit=50, offset=offset)
        if not albums['items']:
            break

        for album in albums['items']:
            album_id = album['id']
            album_name = album['name']
            album_owner = album['artists'][0]['name']

            # Lấy thông tin album chi tiết
            album_info = sp.album(album_id)

            # ✅ Sửa chỗ lỗi ở đây
            album_date_raw = album_info.get('release_date', 'Unknown')
            try:
                album_release_date = pd.to_datetime(album_date_raw, errors='coerce').strftime('%d/%m/%Y')
            except:
                album_release_date = album_date_raw

            # Ưu tiên lấy thông tin nhà phát hành từ copyrights
            copyrights = album_info.get('copyrights', [])
            provider = 'Unknown'
            for c in copyrights:
                if c.get('type') in ('P', 'C') and c.get('text'):
                    provider = c['text']
                    break
            if provider == 'Unknown':
                provider = album_info.get('label', 'Unknown')

            # Lấy tất cả track trong album
            tracks = album_info.get('tracks', {}).get('items', [])
            track_count = len(tracks)

            # Phân loại album dựa trên số lượng bài hát
            if track_count <= 3:
                album_class = "Single"
            elif 4 <= track_count <= 6:
                album_class = "EP"
            else:
                album_class = "Regular"

            # Đưa thông tin bài hát vào track_data
            for track in tracks:
                track_id = track['id']
                if track_id in seen_tracks:
                    continue
                seen_tracks.add(track_id)
                status_code = 'Normal'
                class_Spotify = 'DIGITAL'
                track_title = track['name']
                link_spotify = track['external_urls']['spotify']
                featured_artists = [artist['name'] for artist in track['artists'] if artist['id'] != artist_id]
                featured_artists = ", ".join(featured_artists) if featured_artists else "None"
                album_type = 'digital'
                track_data.append([album_name, album_type, album_owner, track_title, featured_artists, album_release_date, status_code, class_Spotify, album_class, provider, link_spotify])
        offset += 50

    # Lấy top track
    top_tracks = sp.artist_top_tracks(artist_id, country="US")['tracks']
    for track in top_tracks:
        track_id = track['id']
        if track_id in seen_tracks:
            continue
        seen_tracks.add(track_id)

        track_title = track['name']
        link_spotify = track['external_urls']['spotify']
        album = track['album']
        album_name = album['name']
        album_owner = album['artists'][0]['name']

        album_info = sp.album(album['id'])

        album_date_raw = album_info.get('release_date', 'Unknown')
        try:
            album_release_date = pd.to_datetime(album_date_raw, errors='coerce').strftime('%d/%m/%Y')
        except:
            album_release_date = album_date_raw

        copyrights = album_info.get('copyrights', [])
        provider = 'Unknown'
        for c in copyrights:
            if c.get('type') in ('P', 'C') and c.get('text'):
                provider = c['text']
                break
        if provider == 'Unknown':
            provider = album_info.get('label', 'Unknown')

        featured_artists = [artist['name'] for artist in track['artists'] if artist['id'] != artist_id]
        featured_artists = ", ".join(featured_artists) if featured_artists else "None"
       
        track_data.append([album_name, album_type, album_owner, track_title, featured_artists, album_release_date, status_code, class_Spotify, album_class, provider, link_spotify])

    columns = ["album_name", "album type (loại album)", "Album artist (nghệ sĩ sở hữu album)", "tracklist (danh sách bài hát)", "Song artist (nghệ sĩ tham gia bài hát)", "release_date", "status_code", "class", "medium", "distribute", "Link_Spotify"]
    df = pd.DataFrame(track_data, columns=columns)
    df = df.sort_values(by=["album_name"], ascending=True)
    return df


# Hàm xử lý provider
def extract_licensing_provider(provider_info):
    if not provider_info:
        return "Unknown"

    provider_info = re.sub(r"\(C\) \d{4}", "", provider_info)
    provider_info = re.sub(r"\d{4}", "", provider_info)
    provider_info = provider_info.replace("©", "").strip()

    match = re.search(r"(exclusive license|exclusively licensed|exclusive licensed)\s*(?:to)?\s*(.*)", provider_info, re.IGNORECASE)
    
    if match:
        provider = match.group(2).strip()
        provider = re.sub(r"^d\s*", "", provider)
        return provider
    else:
        return provider_info.strip()

def normalize_string(s):
    return re.sub(r'[^a-zA-Z0-9]', '', s.lower())
