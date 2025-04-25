from library import *
from ZingMP3 import *
from Spotify import *
from NhacCuaTui import *
from YouTube import *
from YTMusic import *
from AppleMusic import *
st.set_page_config(page_title="Tool lấy link",page_icon="▶️", layout="wide")
def convert_df(df):
    output = BytesIO()

   
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name="Tracks") 

def extract_channel_music_id(channel_input: str):

    if 'channel' in channel_input:
        match = re.search(r'\/channel\/([a-zA-Z0-9_-]+)', channel_input)
        if match:
            return match.group(1)
        else:
            raise ValueError("Không thể trích xuất Channel ID từ URL")
    else:
        return channel_input
def sanitize_filename(filename):
  
    return filename.replace(" ", "_").replace("/", "_").replace("\\", "_").replace(":", "_")
def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "_", filename)

def trigger_youtube_music_search():
    input_text = st.session_state["ytmusic_input"].strip()
    if not input_text:
        return

    try:
  
        channel_music_url = extract_channel_music_id(input_text)
        st.session_state.pop("df_youtube_music", None)
        st.session_state["youtube_music_channel_name"] = channel_music_url
        st.session_state["youtube_music_should_search"] = True
        st.session_state["youtube_music_prev_input"] = input_text
    except ValueError as e:
        st.error(f"❌ {str(e)}")

def trigger_youtube_search():
    input_text = st.session_state["youtube_input"].strip()
    if not input_text:
        return

    try:
       
        channel_id = extract_channel_id(input_text)
        
     
        st.session_state.pop("df_youtube", None)  
        st.session_state["youtube_channel_name"] = channel_id
        st.session_state["youtube_should_search"] = True
        st.session_state["youtube_prev_input"] = input_text
    except ValueError as e:
        st.error(f"❌ {str(e)}")

if "zingmp3_prev_input" not in st.session_state:
    st.session_state["zingmp3_prev_input"] = ""
if "zingmp3_force_refresh" not in st.session_state:
    st.session_state["zingmp3_force_refresh"] = False
if "spotify_prev_input" not in st.session_state:
    st.session_state["spotify_prev_input"] = ""
if "spotify_force_refresh" not in st.session_state:
    st.session_state["spotify_force_refresh"] = False
if "applemusic_prev_input" not in st.session_state:
    st.session_state["applemusic_prev_input"] = ""
if "applemusic_force_refresh" not in st.session_state:
    st.session_state["applemusic_force_refresh"] = False
if "youtube_prev_input" not in st.session_state:
    st.session_state["youtube_prev_input"] = ""
if "youtube_music_prev_input" not in st.session_state:
    st.session_state["youtube_music_prev_input"] = ""

if "youtube_music_force_refresh" not in st.session_state:
    st.session_state["youtube_music_force_refresh"] = False
if "youtube_force_refresh" not in st.session_state:
    st.session_state["youtube_force_refresh"] = False
for k, v in {
    "spotify_trigger_search": False,         
    "spotify_force_refresh":  False,         
    "spotify_prev_input":     "",        
}.items():
    if k not in st.session_state:
        st.session_state[k] = v
def normalize_string(s):
    s = s.lower()
    s = re.sub(r"[^a-zA-Z0-9\s]", "", s)
    s = s.strip()
    return s
def get_channel_name(channel_input):
    """Fetch channel name based on user input (URL, @username, or Channel ID)."""

    if channel_input.startswith('https://www.youtube.com/channel/'):
        channel_id = channel_input.split('channel/')[1]
    elif channel_input.startswith('@'):
       
        channel_id = channel_input[1:]
    else:
       
        channel_id = channel_input


    channel_name = f"Channel name for {channel_id}" 

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
        st.image("D:\\Workspace\\ToolLink\\logo.png", width=1000)
        selected_platform = option_menu(
            "", ["", "ZingMP3", "Spotify", "Nhaccuatui", "Apple Music", "YouTube", "YouTubeMusic"],
            icons=['', 'vinyl-fill', 'spotify', 'headphones', 'apple', 'youtube', 'play-circle-fill'],
            menu_icon="cast", default_index=0, orientation="vertical"
        )
        st.markdown("""<br><br><hr><p style='font-size: 12px; color: #999;'>© 2025 V.K Entertainment. All rights reserved.</p>""", unsafe_allow_html=True)

    if not selected_platform:
        st.write("Vui lòng chọn một nền tảng từ thanh menu bên trái để bắt đầu.")
        return

    platforms = ["zingmp3", "spotify", "nhaccuatui", "apple music", "youtube", "youtubemusic"]
    for platform in platforms:
        st.session_state[f"show_{platform}_input"] = (selected_platform.lower() == platform)


    if st.session_state.get("show_zingmp3_input"):
        
        cur_input = st.session_state.get("zingmp3_input", "").strip()
        if cur_input and (
            cur_input != st.session_state["zingmp3_prev_input"]
            or st.session_state["zingmp3_force_refresh"]
        ):
            st.session_state["zingmp3_force_refresh"] = False       
            st.session_state.pop("df_zing", None)                
            st.session_state["zingmp3_artist_name"] = ""
            st.session_state["zingmp3_should_search"] = True

        
        st.subheader("Tìm kiếm bài hát trên ZingMP3")

        st.markdown(
            "[Tìm kiếm nghệ sĩ trên ZingMP3](https://zingmp3.vn) để lấy Mã Định Danh Nghệ Sĩ hoặc đường dẫn URL của nghệ sĩ",
            unsafe_allow_html=True,
        )

    
        if "zingmp3_should_search" not in st.session_state:
            st.session_state["zingmp3_should_search"] = False

        def trigger_search():
            input_text = st.session_state["zingmp3_input"].strip()
            if not input_text:
                return
            url_match = re.match(r"https?://zingmp3.vn/([^/?]+)", input_text)
            artist_name = url_match.group(1) if url_match else input_text

            st.session_state.pop("df_zing", None)         
            st.session_state["zingmp3_artist_name"] = artist_name
            st.session_state["zingmp3_should_search"] = True
            st.session_state["zingmp3_prev_input"] = input_text

        
        st.text_input(
            "Nhập Mã Định Danh Nghệ Sĩ hoặc đường dẫn URL ZingMP3",
            key="zingmp3_input",
            on_change=trigger_search,
        )

        
        if st.button("Tìm", key="zingmp3_search_button"):
            trigger_search()

        
        if st.session_state.get("zingmp3_should_search") and "df_zing" not in st.session_state:
            artist_name = st.session_state["zingmp3_artist_name"]

            with st.spinner(
                f"Đang tìm kiếm bài hát cho mã định danh nghệ sĩ **{artist_name}** trên ZingMP3..."
            ):
                try:
                    df_zing = fetch_artist_songs(artist_name)  # <-- gọi API
                except Exception as e:
                    df_zing = None
                    st.error(f"❌ Đã xảy ra lỗi khi lấy dữ liệu: {e}")

            st.session_state["zingmp3_should_search"] = False  # reset

            if df_zing is not None and not df_zing.empty:
                st.session_state["df_zing"] = df_zing
            else:
                st.warning("⚠️ Không tìm thấy bài hát nào. Có thể mã định danh không hợp lệ.")
    
       
        if cur_input:
            url_match = re.match(r"https?://zingmp3.vn/([^/?]+)", cur_input)
            artist_url = cur_input if url_match else f"https://zingmp3.vn/{cur_input}"
            artist_id = url_match.group(1) if url_match else cur_input
            st.markdown(f"**ID Nghệ sĩ**: {artist_id}")
            st.markdown(f"**Link URL**: {artist_url}")

        if "df_zing" in st.session_state:
            artist_name = st.session_state.get(
                "zingmp3_artist_name", "nghệ sĩ chưa xác định"
            )
            st.success(
                f"✅ Đã tìm thấy {len(st.session_state['df_zing'])} bài hát của **{artist_name}**."
            )
            st.dataframe(st.session_state["df_zing"], use_container_width=True)

         
            output_file = f"{artist_name}_zingmp3.xlsx"
            with open(output_file, "wb") as f_out:
                st.session_state["df_zing"].to_excel(f_out, index=False)
            with open(output_file, "rb") as f:
                st.download_button(
                    "📥 Tải kết quả về (.xlsx)",
                    f,
                    output_file,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

    if st.session_state.get("show_spotify_input", False):
       
        st.subheader("Tìm kiếm bài hát trên Spotify")
        st.markdown(
            "[Tìm kiếm nghệ sĩ trên Spotify](https://spotify.com) để lấy Mã Định Danh Nghệ Sĩ hoặc đường dẫn URL của nghệ sĩ",
            unsafe_allow_html=True,
        )

   
        def trigger_search():
            input_text = st.session_state.get("spotify_input", "").strip()
            if not input_text:
                return

          
            match = re.search(r"(?:open.spotify\.com\/artist\/|artist\/)?([a-zA-Z0-9]+)", input_text)
            artist_id = match.group(1) if match else input_text


            if input_text.startswith("https://") and "spotify.com" in input_text:
                match = re.search(r"artist\/([a-zA-Z0-9]+)", input_text)
                if match:
                    artist_id = match.group(1)
        
            st.session_state["spotify_artist_id"] = artist_id
            st.session_state["spotify_artist_url"] = input_text
            st.session_state["spotify_should_search"] = True
            st.session_state.pop("df_spotify", None)


        st.text_input(
            "Nhập Mã Định Danh Nghệ Sĩ hoặc đường dẫn URL Spotify",
            key="spotify_input",
            on_change=trigger_search,
        )

        if st.button("Tìm", key="spotify_search_button"):
            trigger_search()

        # --- Xử lý tìm kiếm ---
        if st.session_state.get("spotify_should_search") and "df_spotify" not in st.session_state:
            artist_id = st.session_state.get("spotify_artist_id", "")
            artist_url = st.session_state.get("spotify_artist_url", "")
            if artist_id:
                result = get_artist_tracks_all(artist_id)
                if len(result) == 3:
                    df_spotify, artist_id, artist_name = result
                    with st.spinner(f"🔎 Đang tìm kiếm bài hát cho nghệ sĩ **{artist_name}**..."):
                        try:
                          
                            st.session_state["spotify_should_search"] = False

                            if df_spotify is not None and not df_spotify.empty:
                                st.session_state["df_spotify"] = df_spotify
                                st.session_state["spotify_artist_display_name"] = artist_name
                            else:
                                st.warning(f"⚠️ Không tìm thấy bài hát nào cho nghệ sĩ **{artist_name}**.")
                        except Exception as e:
                            st.error(f"❌ Lỗi khi tìm kiếm: {e}")
                else:
                    st.error(f"❌ Lỗi khi gọi API Spotify, không đủ dữ liệu trả về.")
            else:
                st.warning("⚠️ Bạn cần nhập Mã Định Danh hoặc đường dẫn URL của nghệ sĩ.")
                
        # --- Hiển thị kết quả ---
        if "df_spotify" in st.session_state:
            df_spotify = st.session_state["df_spotify"]
            artist_name = st.session_state.get("spotify_artist_display_name", "Nghệ sĩ")
            artist_id = st.session_state.get("spotify_artist_id", "")
            artist_url = st.session_state.get("spotify_artist_url", "")

            st.success(f"✅ Đã tìm thấy {len(df_spotify)} bài hát của **{artist_name}**.")
            st.markdown(f"- **ID Nghệ sĩ:** `{artist_id}`")
            st.markdown(f"- **Link URL:** {artist_url}")

            st.dataframe(df_spotify, use_container_width=True)

      
            output_file = f"{artist_name.replace(' ', '_')}_spotify_tracks.xlsx"
            df_spotify.to_excel(output_file, index=False)
            with open(output_file, "rb") as f:
                st.download_button(
                    "📥 Tải kết quả về (.xlsx)",
                    f,
                    file_name=output_file,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

    

    if st.session_state.get("show_nhaccuatui_input", False):
        st.subheader("Tìm kiếm bài hát trên Nhaccuatui")

        nct_artist_input = st.text_input("Nhập Tên Nghệ Sĩ (ví dụ: Sơn Tùng M-TP)", key="nct_input")

        if st.button("Tìm", key="nct_search"):
            nct_artist_name = nct_artist_input.strip()

            if nct_artist_name:
                st.markdown(f"🔍 Đang tìm kiếm bài hát cho nghệ sĩ **{nct_artist_name}** trên Nhaccuatui...")
                try:
                    df_nct, method = search_artist_on_nhaccuatui(nct_artist_name)
                    st.markdown(f"Đã tìm thấy bài hát cho nghệ sĩ **{nct_artist_name}** bằng phương pháp {method}")

             
                    st.dataframe(df_nct, use_container_width=True)
                    st.markdown("###")

                   
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

    
    if st.session_state.get("show_apple music_input"): 
        st.subheader("Tìm kiếm bài hát trên Apple Music")
        st.markdown(
            "[Tìm kiếm nghệ sĩ trên Apple Music](https://music.apple.com) để lấy Mã Định Danh Nghệ Sĩ hoặc đường dẫn URL của nghệ sĩ",
            unsafe_allow_html=True,
        )
        
        cur_input = st.session_state.get("artist_input", "").strip()
        if cur_input and (
            cur_input != st.session_state["applemusic_prev_input"]
            or st.session_state["applemusic_force_refresh"]
        ):
            
            st.session_state["applemusic_force_refresh"] = False
            st.session_state.pop("df_tracks", None) 
            st.session_state["applemusic_should_search"] = True
            st.session_state["applemusic_prev_input"] = cur_input

        
        
        artist_input = st.text_input(
            "Nhập đường dẫn URL hoặc Mã Định Danh Nghệ Sĩ (Ví dụ: 1297259948 hoặc https://music.apple.com/us/artist/artist-name/1297259948):", 
            value=st.session_state.get("artist_input", ""),  
            on_change=None  
        )

        
        def extract_artist_id(input_str):
            match = re.match(r"https://music\.apple\.com/[a-z]{2}/artist/.+/(\d+)", input_str)
            if match:
                return match.group(1)
            else:
                return input_str.strip()  

        # Search function
        def search_artist():
            artist_id = extract_artist_id(artist_input)

            if artist_id:
                with st.spinner("Đang lấy dữ liệu từ Apple Music..."):
                    try:
                        st.session_state["artist_input"] = artist_input

                       
                        df_tracks, artist_name = get_artist_tracks_dataframe(artist_id)
                        artist_name = artist_name.replace("_", " ")
                        st.success(f"Đã lấy được {len(df_tracks)} bài hát cho nghệ sĩ {artist_name}")

                        st.session_state["df_tracks"] = df_tracks
                        st.session_state["artist_name"] = artist_name

                        st.dataframe(df_tracks, use_container_width=True)

                       
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
            else:
                st.error("Không thể xác định Mã Định Danh Nghệ Sĩ hoặc URL hợp lệ.")

       
        if st.button("Tìm") or artist_input.strip():  
            
            search_artist()

        elif "df_tracks" in st.session_state and "artist_name" in st.session_state:
            
            st.success(f"Đã lấy được {len(st.session_state['df_tracks'])} bài hát cho nghệ sĩ {st.session_state['artist_name']}")
            st.dataframe(st.session_state['df_tracks'], use_container_width=True)

            excel_data = convert_df(st.session_state['df_tracks'])
            st.download_button(
                label="📥 Tải về Excel",
                data=excel_data,
                file_name=f"{st.session_state['artist_name']}_song_Apple.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    if st.session_state.get("show_youtube_input"):
        cur_input = st.session_state.get("youtube_input", "").strip()

        if cur_input and (
            cur_input != st.session_state["youtube_prev_input"]
            or st.session_state["youtube_force_refresh"]
        ):
            st.session_state["youtube_force_refresh"] = False
            st.session_state.pop("df_youtube", None)
            st.session_state["youtube_channel_name"] = ""
            st.session_state["youtube_should_search"] = True

        st.subheader("Tìm kiếm video từ kênh YouTube")

        st.markdown(
            "[Tìm kiếm kênh trên YouTube](https://youtube.com) để lấy @username, đường dẫn URL hoặc Channel ID",
            unsafe_allow_html=True,
        )

   
        if "youtube_should_search" not in st.session_state:
            st.session_state["youtube_should_search"] = False

      
        st.text_input(
            "Nhập @username, đường dẫn URL hoặc Channel ID",
            key="youtube_input",
            on_change=trigger_youtube_search,
        )

        # Search button
        if st.button("Tìm", key="youtube_search_button"):
            trigger_youtube_search()

   
        if st.session_state.get("youtube_should_search") and "df_youtube" not in st.session_state:
            channel_id = st.session_state["youtube_channel_name"]
            channel_info_df, channel_title = get_channel_info(channel_id)
            st.session_state["youtube_channel_title"] = channel_title

            with st.spinner(f"Đang tìm kiếm video từ kênh **{channel_title}** trên YouTube..."):
                try:
              
                    df_youtube = get_channel_videos(channel_id)
                except Exception as e:
                    df_youtube = None
                    st.error(f"❌ Đã xảy ra lỗi khi lấy dữ liệu: {e}")

            st.session_state["youtube_should_search"] = False  

            if df_youtube is not None and not df_youtube.empty:
                st.session_state["df_youtube"] = df_youtube
            else:
                st.warning("⚠️ Không tìm thấy video nào từ kênh YouTube.")

       
        if "df_youtube" in st.session_state:
            channel_id = st.session_state.get("youtube_channel_name", "")
            channel_info_df, channel_title = get_channel_info(channel_id)
            st.success(f"✅ Đã tìm thấy {len(st.session_state['df_youtube'])} video từ kênh **{channel_title}**.")
            st.dataframe(st.session_state["df_youtube"], use_container_width=True)

            
            output_file = f"{sanitize_filename(channel_title)}_youtube.xlsx"
            with open(output_file, "wb") as f_out:
                st.session_state["df_youtube"].to_excel(f_out, index=False)

            with open(output_file, "rb") as f:
                st.download_button(
                    "📥 Tải kết quả về (.xlsx)",
                    f,
                    output_file,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

    if "youtube_music_prev_input" not in st.session_state:
        st.session_state["youtube_music_prev_input"] = ""

    if "youtube_music_force_refresh" not in st.session_state:
        st.session_state["youtube_music_force_refresh"] = False

    if "youtube_music_should_search" not in st.session_state:
        st.session_state["youtube_music_should_search"] = False

    if "df_youtube_music" not in st.session_state:
        st.session_state["df_youtube_music"] = None

    if st.session_state.get("show_youtubemusic_input"):
        st.subheader("Tìm kiếm nhạc từ kênh YouTube Music")

       
        channel_music_url = st.text_input("Nhập link hoặc Channel ID của kênh YouTube Music:", key="ytmusic_input")
        cur_input = channel_music_url.strip()
        prev_input = st.session_state.get("youtube_music_prev_input", "")

      
        if cur_input and (cur_input != prev_input or st.session_state.get("youtube_music_force_refresh", False)):
            st.session_state["youtube_music_force_refresh"] = False
            st.session_state.pop("df_youtube_music", None)
            st.session_state["youtube_music_channel_name"] = ""
            st.session_state["youtube_music_should_search"] = True

        
        if st.button("Tìm", key="ytmusic_search_button"):
            st.session_state["youtube_music_should_search"] = True
            st.session_state["youtube_music_channel_name"] = cur_input  

        
        if st.session_state.get("youtube_music_should_search", False) and "df_youtube_music" not in st.session_state:
            with st.spinner("🔍 Đang tìm kiếm bài hát từ kênh YouTube Music..."):
                try:
                    
                    df, artist_name = scrape_youtube_music(cur_input)

                    if df is not None and not df.empty:
                        st.session_state["df_youtube_music"] = df
                        st.session_state["youtube_music_channel_name"] = artist_name
                        st.session_state["youtube_music_prev_input"] = cur_input
                        st.success(f"✅ Tìm thấy {len(df)} bài hát.")
                        st.dataframe(df, use_container_width=True)

                        buffer = io.BytesIO()
                        df.to_excel(buffer, index=False, engine="openpyxl")
                        buffer.seek(0)

                        sanitized_artist_name = sanitize_filename(artist_name if artist_name != "unknown_artist" else "artist")

                        st.download_button(
                            label="📥 Tải danh sách bài hát (.xlsx)",
                            data=buffer,
                            file_name=f"{sanitized_artist_name}_youtube_music_tracks.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    else:
                        st.warning("⚠️ Không tìm thấy bài hát nào từ kênh YouTube Music.")
                except Exception as e:
                    st.error(f"❌ Lỗi xảy ra: {e}")

            st.session_state["youtube_music_should_search"] = False

      
        df_youtube_music = st.session_state.get("df_youtube_music", None)
        if (
            df_youtube_music is not None
            and not df_youtube_music.empty
            and not st.session_state.get("youtube_music_should_search", False)
            and cur_input == prev_input
        ):
            artist_name = st.session_state.get("youtube_music_channel_name", "Unknown Artist")
            st.success(f"✅ Đã tìm thấy {len(df_youtube_music)} bài hát từ kênh {artist_name}.")
            st.dataframe(df_youtube_music, use_container_width=True)

            output_file = f"{sanitize_filename(artist_name)}_youtube_music_tracks.xlsx"
            with open(output_file, "wb") as f_out:
                df_youtube_music.to_excel(f_out, index=False)

            with open(output_file, "rb") as f:
                st.download_button(
                    "📥 Tải kết quả về (.xlsx)",
                    f,
                    output_file,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
if __name__ == "__main__":
    main()

