from library import *
# Load biến môi trường
load_dotenv()
api_key = os.getenv("AIzaSyAPws3yhPzjMysV8yR9F-5ndj-At9q8i18") or "AIzaSyAPws3yhPzjMysV8yR9F-5ndj-At9q8i18"

def extract_channel_id(input_str):
    """
    Chuyển URL/username/@handle thành channel ID (UCxxxxxxx).
    """
    youtube = build("youtube", "v3", developerKey=api_key)

    if "youtube.com" in input_str:
        match_channel = re.search(r"/channel/(UC[\w-]+)", input_str)
        if match_channel:
            return match_channel.group(1)

        match_handle = re.search(r"@([a-zA-Z0-9._-]+)", input_str)
        if match_handle:
            username = match_handle.group(1)
        else:
            return input_str
    elif input_str.startswith("@"):
        username = input_str[1:]
    elif input_str.startswith("UC"):
        return input_str
    else:
        username = input_str

    try:
        request = youtube.search().list(
            part="snippet",
            q=username,
            type="channel",
            maxResults=1
        )
        response = request.execute()
        if response["items"]:
            return response["items"][0]["snippet"]["channelId"]
    except Exception as e:
        print(f"Lỗi khi tìm channel ID từ username: {e}")

    return input_str

def get_channel_videos(input_str):
    """
    Lấy toàn bộ danh sách video từ Channel ID hoặc URL/username.
    """
    try:
        channel_id = extract_channel_id(input_str)
        youtube = build("youtube", "v3", developerKey=api_key)

        videos = []
        next_page_token = None

        while True:
            request = youtube.search().list(
                part="snippet",
                channelId=channel_id,
                maxResults=50,
                order="date",
                type="video",
                pageToken=next_page_token
            )
            response = request.execute()

            for item in response.get("items", []):
                snippet = item["snippet"]
                video_id = item["id"]["videoId"]
                videos.append({
                    "Tiêu đề": snippet["title"],
                    "Ngày đăng": snippet["publishedAt"],
                    "Video ID": video_id,
                    "Link YouTube": f"https://www.youtube.com/watch?v={video_id}"
                })

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

        return pd.DataFrame(videos)

    except Exception as e:
        print(f"Lỗi khi lấy video từ kênh: {e}")
        return pd.DataFrame()
