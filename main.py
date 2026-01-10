import os
import requests
import datetime
import random

# ================= 配置区域 =================
# 这里的关键词是根据你上传的图片风格定制的
KEYWORDS = [
    "cinematic lighting",   # 电影级布光
    "epic nature",          # 史诗自然
    "moody urban",          # 情绪化城市
    "hope sunrise",         # 希望与日出
    "mountain silhouette",  # 山峰剪影
    "cyberpunk city",       # 赛博朋克 (类似图1的城市感)
    "solitary hiker"        # 孤独的徒步者 (类似图2)
]

# 每次运行下载几张？建议 1 张，保持精品
DOWNLOAD_COUNT = 1
SAVE_DIR = "wallpapers"
# ===========================================

UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY")
API_URL = "https://api.unsplash.com/photos/random"

def get_wallpaper():
    """从 Unsplash 获取符合审美的高清图"""
    headers = {
        "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
    }
    
    # 随机选一个关键词组合，保持新鲜感
    query = random.choice(KEYWORDS)
    print(f"🔍 今天的探索主题: {query}")

    params = {
        "query": query,
        "orientation": "landscape", # 只要横图
        "count": DOWNLOAD_COUNT,
        "content_filter": "high"    # 过滤低俗内容
    }

    try:
        response = requests.get(API_URL, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"API 请求失败: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"发生错误: {e}")
        return []

def download_image(img_data):
    """下载图片并保存"""
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    saved_files = []
    
    for img in img_data:
        img_url = img['urls']['full'] # 获取最高清原图
        img_id = img['id']
        author_name = img['user']['name']
        author_link = img['user']['links']['html']
        
        # 为了不占太多空间，我们也可以选择 'regular' 尺寸，这里选 'full' 追求极致画质
        # 如果仓库太大，可以改用 img['urls']['regular']
        
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        filename = f"{SAVE_DIR}/{today}_{img_id}.jpg"
        
        print(f"⬇️ 正在下载: {filename} ...")
        
        with open(filename, 'wb') as f:
            f.write(requests.get(img_url).content)
            
        saved_files.append({
            "path": filename,
            "url": img_url,
            "author": author_name,
            "author_link": author_link,
            "description": img.get('alt_description') or "Untitled",
            "date": today
        })
        
    return saved_files

def update_readme(new_images):
    """更新 README 展示画廊"""
    readme_path = "README.md"
    
    # 读取旧内容
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = "# 🌄 Daily Inspiration Wallpapers\n\n每天一张视觉震撼的壁纸，保持饥渴，保持愚蠢。\n\n---"

    # 构造新图片的 Markdown
    new_entry = ""
    for img in new_images:
        # 使用 HTML 标签可以控制图片宽度，避免太占版面
        new_entry += f"\n### 📅 {img['date']} | {img['description'].title()}\n"
        new_entry += f"<img src='{img['path']}' width='100%' style='border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);'>\n\n"
        new_entry += f"> 📸 Photo by [{img['author']}]({img['author_link']}) on Unsplash\n\n---\n"

    # 将新内容插入到标题之后（即置顶最新图片）
    header_end_index = content.find("---") + 3
    final_content = content[:header_end_index] + new_entry + content[header_end_index:]

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(final_content)

if __name__ == "__main__":
    if not UNSPLASH_ACCESS_KEY:
        print("❌ 错误: 未找到 UNSPLASH_ACCESS_KEY")
        exit(1)

    images = get_wallpaper()
    if images:
        saved_list = download_image(images)
        update_readme(saved_list)
        print("✅ 任务完成！")
    else:
        print("⚠️ 未找到图片")
