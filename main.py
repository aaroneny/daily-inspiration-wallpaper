import os
import requests
import datetime
import random
import time

# ================= 配置区域 =================
# 扩充后的关键词库，确保10张图风格各异
KEYWORDS = [
    "cinematic lighting",   # 电影光感
    "epic nature",          # 史诗自然
    "moody urban",          # 情绪城市
    "hope sunrise",         # 希望日出
    "mountain silhouette",  # 山脉剪影
    "cyberpunk city",       # 赛博朋克
    "solitary hiker",       # 孤独行者
    "starry night",         # 璀璨星空
    "futuristic architecture", # 未来建筑
    "misty forest",         # 迷雾森林
    "aerial view",          # 上帝视角
    "minimalist landscape", # 极简地貌
    "neon vibes"            # 霓虹氛围
]

# 每次运行生成的数量
BATCH_SIZE = 10 
SAVE_DIR = "wallpapers"
# ===========================================

UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY")
API_URL = "https://api.unsplash.com/photos/random"

def get_one_wallpaper():
    """随机抽取一个关键词，获取一张图"""
    headers = {
        "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
    }
    
    # 随机选一个主题
    query = random.choice(KEYWORDS)
    print(f"🔍 正在探索主题: {query} ...")

    params = {
        "query": query,
        "orientation": "landscape",
        "count": 1,
        "content_filter": "high"
    }

    try:
        response = requests.get(API_URL, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            # API返回的是列表，我们要取第一个
            return data[0] if isinstance(data, list) else data
        else:
            print(f"⚠️ API 请求失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        return None

def download_images():
    """执行多次下载任务"""
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    saved_files = []
    
    print(f"🚀 开始采集 {BATCH_SIZE} 张精选壁纸...")
    
    for i in range(BATCH_SIZE):
        img_data = get_one_wallpaper()
        
        if img_data:
            img_url = img_data['urls']['regular'] # 改用 regular 以免10张原图导致仓库爆炸
            img_id = img_data['id']
            author_name = img_data['user']['name']
            author_link = img_data['user']['links']['html']
            desc = img_data.get('alt_description') or img_data.get('description') or "Untitled"
            
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            # 文件名加上索引，防止一秒内下载多张重名
            filename = f"{SAVE_DIR}/{today}_{i}_{img_id}.jpg"
            
            print(f"   [{i+1}/{BATCH_SIZE}] ⬇️ 下载: {desc[:20]}...")
            
            try:
                with open(filename, 'wb') as f:
                    f.write(requests.get(img_url).content)
                
                saved_files.append({
                    "path": filename,
                    "author": author_name,
                    "author_link": author_link,
                    "desc": desc.title()
                })
            except Exception as e:
                print(f"   保存失败: {e}")
        
        # 稍微暂停一下，对 API 温柔一点
        time.sleep(0.5)
            
    return saved_files

def update_readme(new_images):
    """更新 README，使用 HTML 表格实现双列排版"""
    readme_path = "README.md"
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = "# 🌄 Daily Inspiration Gallery\n\n每天更新的视觉灵感库。\n\n---"

    # 构造 HTML 表格内容 (每行2张图)
    new_entry = f"\n### 📅 {today_str} Collection\n\n<table>\n"
    
    for i in range(0, len(new_images), 2):
        # 取出左边一张
        img1 = new_images[i]
        # 尝试取出右边一张（如果还有的话）
        img2 = new_images[i+1] if i+1 < len(new_images) else None
        
        new_entry += "  <tr>\n"
        
        # 左侧单元格
        new_entry += f"    <td width='50%' align='center'>\n"
        new_entry += f"      <img src='{img1['path']}' width='100%' style='border-radius:8px'><br>\n"
        new_entry += f"      <sub><b>{img1['desc']}</b><br>by <a href='{img1['author_link']}'>{img1['author']}</a></sub>\n"
        new_entry += "    </td>\n"
        
        # 右侧单元格
        if img2:
            new_entry += f"    <td width='50%' align='center'>\n"
            new_entry += f"      <img src='{img2['path']}' width='100%' style='border-radius:8px'><br>\n"
            new_entry += f"      <sub><b>{img2['desc']}</b><br>by <a href='{img2['author_link']}'>{img2['author']}</a></sub>\n"
            new_entry += "    </td>\n"
        else:
            new_entry += "    <td width='50%'></td>\n" # 占位
            
        new_entry += "  </tr>\n"

    new_entry += "</table>\n\n---\n"

    # 插入到顶部
    header_end_index = content.find("---") + 3
    final_content = content[:header_end_index] + new_entry + content[header_end_index:]

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(final_content)

if __name__ == "__main__":
    if not UNSPLASH_ACCESS_KEY:
        print("❌ 错误: 未找到 UNSPLASH_ACCESS_KEY")
        exit(1)

    images = download_images()
    if images:
        update_readme(images)
        print(f"✅ 今日 {len(images)} 张壁纸采集完成！")
    else:
        print("⚠️ 未能下载任何图片")
