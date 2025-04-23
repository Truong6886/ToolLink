from library import *
def scrape_youtube_music(channel_input: str, export_excel=False, excel_path=None):
    # Nếu chỉ là ID kênh, thì ghép thành URL
    if 'channel' not in channel_input:
        channel_id = channel_input
        channel_input = f"https://music.youtube.com/channel/{channel_id}"
    else:
        channel_id = channel_input.split('/channel/')[-1]

    # --- Lấy tên nghệ sĩ bằng ytmusicapi ---
    try:
        ytmusic = YTMusic()
        artist_info = ytmusic.get_artist(channel_id)
        artist_name = artist_info['name']
    except Exception as e:
        print("Không thể lấy tên nghệ sĩ từ ytmusicapi:", e)
        artist_name = "unknown_artist"

    print("Tên nghệ sĩ:", artist_name)

    # Làm sạch tên file
    def sanitize_filename(name):
        return re.sub(r'[\\/*?:"<>|]', "_", name)

    filename = f"{sanitize_filename(artist_name)}_YTMusic.xlsx"

    # Danh sách lưu dữ liệu bài hát
    data = []
    album_map = {}

    # --- Khởi tạo Selenium ---
    driver = webdriver.Chrome()
    driver.get(channel_input)

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    time.sleep(3)

    # --- PHẦN 1: Trang chính của kênh ---
    try:
        show_all_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[.//span[contains(text(), "Show all")]]'))
        )
        ActionChains(driver).move_to_element(show_all_button).click().perform()
        print("Đã click 'Show all'")
        time.sleep(3)
    except Exception as e:
        print("Không tìm thấy hoặc không thể click 'Show all':", e)

    song_links = driver.find_elements(By.XPATH, '//a[@class="yt-simple-endpoint style-scope yt-formatted-string"]')
    for song in song_links:
        song_url = song.get_attribute('href')
        song_title = song.text
        if song_url and 'watch?v=' in song_url:
            list_id = None
            if 'list=' in song_url:
                list_id = song_url.split('list=')[1].split('&')[0]
            album_name = song_title
            if list_id and list_id in album_map:
                album_name = album_map[list_id]
            data.append({
                "album": album_name,
                "tracklist": song_title,
                "video_url": song_url,
            })

    # --- PHẦN 2: Album (SINGLE & EPs) ---
    driver.get(channel_input)
    time.sleep(3)

    try:
        more_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='More']"))
        )
        more_button.click()
        time.sleep(3)
    except Exception as e:
        print("Không tìm thấy nút 'More':", e)

    album_elements = driver.find_elements(By.XPATH, "//a[@class='yt-simple-endpoint image-wrapper style-scope ytmusic-two-row-item-renderer']")
    album_titles = driver.find_elements(By.XPATH, "//yt-formatted-string[@class='title style-scope ytmusic-two-row-item-renderer']")

    album_links = [el.get_attribute("href") for el in album_elements]
    album_names = [el.text for el in album_titles]

    for idx, album_link in enumerate(album_links):
        album_name = album_names[idx] if idx < len(album_names) else "Unknown Album"
        driver.get(album_link)
        time.sleep(3)

        try:
            album_name_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h1[@class='style-scope ytmusic-responsive-header-renderer']/yt-formatted-string"))
            )
            album_name = album_name_element.text.strip()
        except Exception as e:
            print(f"Không lấy được tên album: {e}")

        try:
            tracks = driver.find_elements(By.XPATH, "//yt-formatted-string[@class='title style-scope ytmusic-responsive-list-item-renderer complex-string']//a")
            for track in tracks:
                track_title = track.text
                href = track.get_attribute("href")
                if href and 'watch?v=' in href:
                    list_id = None
                    if 'list=' in href:
                        list_id = href.split('list=')[1].split('&')[0]
                        album_map[list_id] = album_name
                    data.append({
                        "album": album_name,
                        "tracklist": track_title,
                        "video_url": href,
                    })
        except Exception as e:
            print(f"Lỗi lấy bài hát từ album: {e}")

    driver.quit()

    df = pd.DataFrame(data)

    if export_excel:
        if excel_path is None:
            excel_path = filename
        df.to_excel(excel_path, index=False)
        print(f"Đã lưu vào file: {excel_path}")

    return df,artist_name
