from library import *
from ZingMP3 import *
from Spotify import *
from NhacCuaTui import *
from YouTube import *
from YTMusic import *
from AppleMusic import *
st.set_page_config(page_title="Tool lấy link",page_icon="▶️", layout="wide")

def normalize_string(s):
    s = s.lower()
    s = re.sub(r"[^a-zA-Z0-9\s]", "", s)
    s = s.strip()
    return s
def get_channel_name(channel_input):
    """Fetch channel name based on user input (URL, @username, or Channel ID)."""
    # Handle different input formats: Channel URL, @username, or Channel ID
    if channel_input.startswith('https://www.youtube.com/channel/'):
        # If URL format, extract the channel ID
        channel_id = channel_input.split('channel/')[1]
    elif channel_input.startswith('@'):
        # If @username, we need to handle it (could use YouTube API to resolve it)
        channel_id = channel_input[1:]
    else:
        # Assume it's a Channel ID directly
        channel_id = channel_input

    # Here you would use the YouTube API or scrape the channel to fetch the name, for example:
    # This part is just an example placeholder.
    # You can use YouTube API to get the channel name using channel_id.
    channel_name = f"Channel name for {channel_id}"  # Replace with actual name resolution

    return channel_name
def search_artist_on_nhaccuatui(artist_name):
    driver = webdriver.Chrome()
    artist_page = search_artist_nhaccuatui(driver, artist_name)

    if artist_page:
        artist_song_page = artist_page.replace(".html", ".bai-hat.html")
        artist_album_page = artist_page.replace(".html", ".playlist.html")

        artist_songs = get_artist_songs(driver, artist_song_page)
        albums = get_artist_albums(driver, artist_album_page)

        all_songs = artist_songs[:]
        for album_link in albums:
            album_songs = get_album_songs(driver, album_link)
            all_songs.extend(album_songs)

        df_nct = pd.DataFrame(all_songs, columns=["album_name", "tracklist(danh sách bài hát)", "Link bài hát"])
        return df_nct, "v1"
    else:
        songs, playlists = search_nhaccuatui(artist_name)
        data = []

        for song_title, song_link, _ in songs:
            data.append([song_title, song_title, song_link])

        for album_name, playlist_songs, link in playlists:
            for title, song_link in playlist_songs:
                data.append([album_name, title, song_link])

        df_nct = pd.DataFrame(data, columns=["album_name", "tracklist(danh sách bài hát)", "Nhaccuatui"])
        return df_nct, "v2"

    driver.quit()

def main():
    
    st.markdown("""
        <style>
        .st-emotion-cache-18w1b6t { bottom: 65px !important; position: relative; }
        .st-emotion-cache-kj6hex { bottom: 50px !important;top: 0px; position: relative; }
        .st-emotion-cache-1wtqxho {bottom: 80px !important;}
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.image("D:\\ToolLink\\logo.png", width=1000)
        selected_platform = option_menu(
            "", ["", "ZingMP3", "Spotify", "Nhaccuatui", "AppleMusic", "YouTube", "YouTubeMusic"],
            icons=['', 'vinyl-fill', 'spotify', 'headphones', 'apple', 'youtube', 'play-circle-fill'],
            menu_icon="cast", default_index=0, orientation="vertical"
        )
        st.markdown("""<br><br><hr><p style='font-size: 12px; color: #999;'>© 2025 V.K Entertainment. All rights reserved.</p>""", unsafe_allow_html=True)

    if not selected_platform:
        st.write("Vui lòng chọn một nền tảng từ thanh menu bên trái để bắt đầu.")
        return

    platforms = ["zingmp3", "spotify", "nhaccuatui", "applemusic", "youtube", "youtubemusic"]
    for platform in platforms:
        st.session_state[f"show_{platform}_input"] = (selected_platform.lower() == platform)



    if st.session_state.get("show_zingmp3_input"):
        st.subheader("Tìm kiếm bài hát trên ZingMP3")

        # Thêm một nút mở ZingMP3 để người dùng tìm kiếm nghệ sĩ
        st.markdown("[Tìm kiếm nghệ sĩ trên ZingMP3](https://zingmp3.vn) để lấy Mã Định Danh Nghệ Sĩ hoặc URL của nghệ sĩ", unsafe_allow_html=True)

        artist_input = st.text_input("Nhập Mã Định Danh Nghệ Sĩ (ví dụ: Tien-Cookie) hoặc Link ZingMP3 (ví dụ: https://zingmp3.vn/Tien-Cookie)", key="zingmp3_input")
        
        # Dùng container để canh chuẩn layout
        with st.container():
            search_clicked = st.button("Tìm", key="zingmp3_search")

        if search_clicked:
            if artist_input.strip():
                # Kiểm tra nếu người dùng nhập URL
                url_match = re.match(r"https://zingmp3.vn/([^/]+)", artist_input.strip())
                if url_match:
                    artist_input = url_match.group(1).lower()  # Lấy tên nghệ sĩ từ URL và chuyển thành chữ thường

                st.markdown(f"🔍 Đang tìm kiếm bài hát cho mã định danh nghệ sĩ <strong>{artist_input}</strong> trên ZingMP3...", unsafe_allow_html=True)
                df_zing = fetch_artist_songs(artist_input.strip())
                if df_zing is not None and not df_zing.empty:
                    st.success(f"✅ Tìm thấy {len(df_zing)} bài hát.")
                    # Bảng hiển thị
                    st.dataframe(df_zing, use_container_width=True)
                    st.markdown("###")
                    output_file = f"{artist_input}_zingmp3.xlsx"
                    df_zing.to_excel(output_file, index=False)
                    with open(output_file, "rb") as f:
                        st.download_button(
                            "📥 Tải kết quả về (.xlsx)", 
                            f, 
                            output_file, 
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                else:
                    st.warning("⚠️ Không tìm thấy bài hát nào.")
            else:
                st.error("Vui lòng nhập tên nghệ sĩ hoặc URL ZingMP3.")


    # Nếu chọn Spotify
    if st.session_state.get("show_spotify_input", False):
        st.subheader("Tìm kiếm bài hát trên Spotify")
        spotify_input = st.text_input("Nhập Tên Nghệ Sĩ (ví dụ: Tiên Cookies)", key="spotify_input")
        if st.button("Tìm", key="spotify_search"):
            keyword = spotify_input.strip()
            if keyword:
                st.markdown(f"🔍 Đang tìm kiếm bài hát cho nghệ sĩ **{keyword}** trên Spotify...")
                df_spotify = get_artist_tracks_all(keyword)
                df_spotify['distribute'] = df_spotify['distribute'].apply(extract_licensing_provider)

                df_spotify['normalized_album_name'] = df_spotify['album_name'].apply(normalize_string)
                df_spotify.sort_values(by=["normalized_album_name"], ascending=True, inplace=True)
                df_spotify.drop(columns=["normalized_album_name"], inplace=True)
                df_spotify.reset_index(drop=True, inplace=True)
                if df_spotify is not None and not df_spotify.empty:
                    st.success(f"✅ Tìm thấy {len(df_spotify)} bài hát.")
                    st.dataframe(df_spotify, use_container_width=True)
                    st.markdown("###")
                    output_file = f"{keyword}_spotify.xlsx"
                    df_spotify.to_excel(output_file, index=False)

                    with open(output_file, "rb") as f:
                        st.download_button(
                            label="📥 Tải kết quả về (.xlsx)",
                            data=f,
                            file_name=output_file,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                else:
                    st.warning("⚠️ Không tìm thấy bài hát nào.")
            else:
                st.error("Vui lòng nhập từ khóa tìm kiếm.") 

    # Nếu chọn Nhaccuatui
    if st.session_state.get("show_nhaccuatui_input", False):
        st.subheader("Tìm kiếm bài hát trên Nhaccuatui")
        nct_artist_input = st.text_input("Nhập Tên Nghệ Sĩ (ví dụ: Tiên Cookies)", key="nct_input")
        
        if st.button("Tìm", key="nct_search"):
            nct_artist_name = nct_artist_input.strip()
            
            if nct_artist_name:
                st.markdown(f"🔍 Đang tìm kiếm bài hát cho nghệ sĩ **{nct_artist_name}** trên Nhaccuatui...")
                try:
                    df_nct, method = search_artist_on_nhaccuatui(nct_artist_name)
                    st.markdown(f"Đã tìm thấy bài hát cho nghệ sĩ    **{nct_artist_name}** bằng phương pháp {method}")

                    # Hiển thị bảng dữ liệu
                    st.dataframe(df_nct, use_container_width=True)
                    st.markdown("###")
                    # Chuẩn bị buffer và thêm nút tải file ngay dưới bảng
                    buffer = io.BytesIO()
                    df_nct.to_excel(buffer, index=False, engine='openpyxl')
                    buffer.seek(0)

                    st.download_button(
                        label="📥 Tải kết quả về (.xlsx)",
                        data=buffer,
                        file_name=f"{nct_artist_name}_NhacCuaTui_{method}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                except Exception as e:
                    st.error(f"Lỗi khi tìm kiếm nghệ sĩ: {e}")
            else:
                st.error("Vui lòng nhập tên nghệ sĩ.") 

    if st.session_state.get("show_applemusic_input"):
        st.subheader("Tìm kiếm bài hát trên Apple Music")

        # Ô nhập ID nghệ sĩ
        artist_id = st.text_input("Nhập Mã Định Danh Nghệ Sĩ (Ví dụ: 1297259948):", value="")

        if st.button("Tìm kiếm") and artist_id.strip():
            with st.spinner("Đang lấy dữ liệu từ Apple Music..."):
                try:
                    df_tracks, artist_name = get_artist_tracks_dataframe(artist_id)
                    artist_name = artist_name.replace("_", " ")
                    st.success(f"Đã lấy được {len(df_tracks)} bài hát cho nghệ sĩ `{artist_name}`")

                    # Hiển thị bảng dữ liệu
                    st.dataframe(df_tracks, use_container_width=True)

                    # Nút tải về
                    def convert_df(df):
                        output = BytesIO()
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            df.to_excel(writer, index=False, sheet_name="Tracks")
                        return output.getvalue()

                    excel_data = convert_df(df_tracks)
                    st.download_button(
                        label="📥 Tải về Excel",
                        data=excel_data,
                        file_name=f"{artist_name}_song_Apple.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                except Exception as e:
                    st.error(f"Lỗi khi lấy dữ liệu: {str(e)}")
    if st.session_state.get("show_youtube_input"):
        st.subheader("Tìm kiếm video từ kênh YouTube")

        user_input = st.text_input("Nhập @username, đường dẫn hoặc Channel ID:", key="channel_input")

        if st.button("Tìm"):
            user_input = user_input.strip()

            if user_input:
                st.info(f"🎬 Đang tìm video từ: **{user_input}**")
                
                # Get the actual channel name or ID
                channel_name = get_channel_name(user_input)
                st.info(f"📺 Kênh: {channel_name}")

                # Now, fetch the videos using the extracted channel ID or username
                df = get_channel_videos(user_input)  # Assuming get_channel_videos works with user_input

                if not df.empty:
                    st.success(f"✅ Tìm thấy {len(df)} video.")
                    st.dataframe(df, use_container_width=True)
                    st.markdown("###")

                    # Tạo buffer Excel để tải
                    buffer = io.BytesIO()
                    df.to_excel(buffer, index=False, engine="openpyxl")
                    buffer.seek(0)

                    st.download_button(
                        label="📥 Tải về danh sách video (.xlsx)",
                        data=buffer,
                        file_name=f"{user_input.replace('@','').replace('/','_')}_videos.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                        st.warning("⚠️ Không tìm thấy video nào.")
            else:
                    st.error("⚠️ Vui lòng nhập dữ liệu.")
    if st.session_state.get("show_youtubemusic_input"):
        st.subheader("Tìm kiếm nhạc từ kênh YouTube Music")
        channel_music_url = st.text_input("Nhập link hoặc Channel ID của kênh YouTube Music:", key="ytmusic_input")

        if st.button("Tìm"):
            channel_music_url = channel_music_url.strip()
            if channel_music_url:
                if channel_music_url.startswith("http"):
                    st.info(f"🔍 Đang tìm kiếm bài hát từ **link**: {channel_music_url}")
                else:
                    st.info(f"🔍 Đang tìm kiếm bài hát từ **Channel ID**: {channel_music_url}")

                try:
                    # Scrape the YouTube music data
                    df, artist_name = scrape_youtube_music(channel_music_url)

                    if not df.empty:
                        st.success(f"✅ Tìm thấy {len(df)} bài hát.")
                        st.dataframe(df, use_container_width=True)
                        st.markdown("###")

                        # Create the download button with the correct artist name in the file
                        buffer = io.BytesIO()
                        df.to_excel(buffer, index=False, engine="openpyxl")
                        buffer.seek(0)

                        # Sanitize artist name to avoid file name issues
                        artist_name = artist_name if artist_name != "unknown_artist" else "artist"
                        sanitized_artist_name = re.sub(r'[\\/*?:"<>|]', "_", artist_name)

                        st.download_button(
                            label="📥 Tải danh sách bài hát (.xlsx)",
                            data=buffer,
                            file_name=f"{sanitized_artist_name}_youtube_music_tracks.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                except Exception as e:
                    st.error(f"❌ Lỗi xảy ra: {e}")
            else:
                    st.error("⚠️ Vui lòng nhập đường dẫn kênh YouTube Music.")
        

if __name__ == "__main__":
    main()
