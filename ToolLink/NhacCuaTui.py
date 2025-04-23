from library import *

def search_artist_nhaccuatui(driver, artist_name):
    """Tìm nghệ sĩ trên NhacCuaTui và lấy link trang nghệ sĩ."""
    driver.get("https://www.nhaccuatui.com/")
    time.sleep(3)

    try:
        search_box = driver.find_element(By.CSS_SELECTOR, "input#txtSearch")
        search_box.click()
        time.sleep(1)

        search_box.send_keys(artist_name)
        time.sleep(3)

        suggestions = driver.find_elements(By.CSS_SELECTOR, ".info-search .qsItem a")
        for suggestion in suggestions:
            if "nghe-si" in suggestion.get_attribute("href"):
                return suggestion.get_attribute("href")
    except Exception as e:
        print(f"Lỗi khi tìm nghệ sĩ {artist_name}: {e}")
    return None

def get_artist_songs(driver, artist_song_url):
    """Lấy danh sách bài hát của nghệ sĩ từ tất cả các trang."""
    driver.get(artist_song_url)
    time.sleep(3)
    song_list = []
    while True:
        song_blocks = driver.find_elements(By.CSS_SELECTOR, ".box-content-music-list .info_song")
        for song_block in song_blocks:
            try:
                song_name = song_block.find_element(By.CSS_SELECTOR, "h3 a").text
                song_link = song_block.find_element(By.CSS_SELECTOR, "h3 a").get_attribute("href")
                song_list.append(("N/A", song_name, song_link))
            except Exception as e:
                print(f"Lỗi khi lấy bài hát: {e}")
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "a.number[rel='next']")
            next_link = next_button.get_attribute("href")
            if next_link:
                driver.get(next_link)
                time.sleep(3)
            else:
                break
        except:
            break
    return song_list

def get_artist_albums(driver, artist_album_url):
    """Lấy danh sách Album của nghệ sĩ."""
    driver.get(artist_album_url)
    time.sleep(3)

    album_list = []
    while True:
        album_blocks = driver.find_elements(By.CSS_SELECTOR, ".box-left-album a.box_absolute")
        for album in album_blocks:
            try:
                album_link = album.get_attribute("href")
                album_list.append(album_link)
            except Exception as e:
                print(f"Lỗi khi lấy album: {e}")
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "a.number[rel='next']")
            next_link = next_button.get_attribute("href")
            if next_link:
                driver.get(next_link)
                time.sleep(3)
            else:
                break
        except:
            break
    return album_list

def get_album_songs(driver, album_url):
    """Lấy danh sách bài hát trong Album."""
    driver.get(album_url)
    time.sleep(3)
    try:
        album_name = driver.find_element(By.CSS_SELECTOR, ".name_title").text
        song_elements = driver.find_elements(By.CSS_SELECTOR, "li[id^='itemSong_']")
        album_songs = [(album_name,
                        s.find_element(By.CSS_SELECTOR, "meta[itemprop='name']").get_attribute("content"),
                        s.find_element(By.CSS_SELECTOR, "meta[itemprop='url']").get_attribute("content"))
                        for s in song_elements]
        return album_songs
    except Exception as e:
        print(f"Lỗi khi lấy bài hát từ album {album_url}: {e}")
    return []

def search_nhaccuatui(artist_name):
    driver = webdriver.Chrome()

    # Tìm kiếm bài hát
    search_url_songs = f"https://www.nhaccuatui.com/tim-kiem/bai-hat?q={artist_name}&b=keyword&l=tat-ca&s=default"
    # Tìm kiếm playlist
    search_url_playlists = f"https://www.nhaccuatui.com/tim-kiem/playlist?q={artist_name}&b=keyword&l=tat-ca&s=default"

    driver.get(search_url_songs)
    time.sleep(3)

    song_list = []

    while True:
        songs = driver.find_elements(By.CSS_SELECTOR, ".box_info h3.title_song a")
        artists = driver.find_elements(By.CSS_SELECTOR, ".box_info h4.singer_song")

        for song, artist in zip(songs, artists):
            artist_names = ", ".join([a.text for a in artist.find_elements(By.TAG_NAME, "a")])
            
            # Only add the song if the artist's name matches exactly
            if artist_name.lower() in artist_names.lower():  # You can adjust case sensitivity if needed
                song_list.append((song.text, song.get_attribute("href"), artist_names))

        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "a.number[rel='next']")
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(3)
        except:
            break

    # Chuyển qua tìm kiếm playlist
    driver.get(search_url_playlists)
    time.sleep(3)

    checked_playlists = set()
    playlist_links = []

    while True:
        try:
            playlists = driver.find_elements(By.CSS_SELECTOR, ".box_info h3.title_song a")
            for p in playlists:
                link = p.get_attribute("href")
                if link and link not in checked_playlists:
                    playlist_links.append(link)
                    checked_playlists.add(link)
        except Exception as e:
            print(f"Lỗi khi lấy danh sách playlist: {e}")

        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "a.number[rel='next']")
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(3)
        except:
            break

    playlist_list = []

    for link in playlist_links:
        retry = 3
        while retry > 0:
            try:
                driver.get(link)
                time.sleep(3)

                album_name = driver.find_element(By.CSS_SELECTOR, ".name_title").text

                song_elements = driver.find_elements(By.CSS_SELECTOR, "li[id^='itemSong_']")
                playlist_songs = [(s.find_element(By.CSS_SELECTOR, "meta[itemprop='name']").get_attribute("content"),
                                   s.find_element(By.CSS_SELECTOR, "meta[itemprop='url']").get_attribute("content"))
                                  for s in song_elements]

                playlist_list.append((album_name, playlist_songs, link))
                break
            except Exception as e:
                print(f"Lỗi khi lấy dữ liệu playlist {link}: {e}")
                driver.refresh()
                time.sleep(3)
                retry -= 1

    driver.quit()
    return song_list, playlist_list

