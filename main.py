import os
import requests
import datetime
import random
import time

# ================= 核心升级配置区域 =================

# 🌟 精英关键词库 🌟
# 这些是根据你的审美定制的组合词，每一个都能触发 Unsplash 的高质量反馈。
# 我们准备了超过10个词，用来确保每天都能轮换出不同的组合。
ELITE_KEYWORDS = [
    # 史诗自然类 (对标高山日出图)
    "epic mountain sunrise silhouette cinematic",
    "majestic forest light beams morning",
    "stunning landscape golden hour backlight",
    "awe inspiring nature vista foggy",
    "dramatic coastline cliff sunset",
    
    # 城市与希望类 (对标城市晨曦图)
    "cinematic city skyline sunrise hope",
    "urban architecture light rays hopeful",
    "cyberpunk city night cinematic neon",
    "futuristic city skyline dawn",
    
    # 人物与征途类 (积极向上、催人奋进)
    "solitary hiker mountain top success",
    "person standing on cliff edge looking at view",
    "man silhouette sunrise achievement",
    
    # 抽象与氛围类 (视觉震撼)
    "milky way starry night silhouette",
    "abstract nature texture cinematic lighting"
]

# 每次运行生成的数量
BATCH_SIZE = 10 
SAVE_DIR = "wallpapers"
# ===========================================

UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY")
API_URL = "https://api.unsplash.com/photos/random"

def get_one_wallpaper(specific_query):
    """使用指定的关键词，获取一张精选图"""
    headers = {
        "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
    }
    
    params = {
        "query": specific_query,   # 使用指定的精准长尾词
        "orientation": "landscape",
        "count": 1,
        "content_filter": "high",
        "featured": "true"         # 🌟 关键升级：只看 Unsplash 编辑精选的作品
    }

    try:
        # 设置 10 秒超时，防止网络卡住
        response = requests.get(API_URL, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data[0] if isinstance(data, list) else data
        else:
            print(f"⚠️ API 请求失败 [{response.status_code}]: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 网络或API错误: {e}")
        return None

def download_images():
    """执行批量下载任务"""
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    saved_files = []
    
    # ✅ 关键升级：从精英库中“不放回”地抽取 10 个不同的关键词
    # 确保这 10 张图的主题绝对不会重复
    todays_queries = random.sample(ELITE_KEYWORDS, BATCH_SIZE)
    
    print(f"🚀 开始采集 {BATCH_SIZE} 张精选壁纸，今日主题序列已生成。")
    
    for i, query in enumerate(todays_queries):
        print(f"   [{i+1}/{BATCH_SIZE}] 🔍 正在寻找: '{query}' ...")
        img_data = get_one_wallpaper(query)
        
        if img_data:
            # 使用 regular 尺寸平衡画质和文件大小
            img_url = img_data['urls']['regular'] 
            img_id = img_data['id']
            author_name = img_data['user']['name']
            author_link = img_data['user']['links']['html']
            # 优先使用简短描述，没有则用替代描述
            desc = img_data.get('description') or img_data.get('alt_description') or "Untitled Inspiration"
            # 清理描述中的换行符，保持整洁
            desc = desc.replace('\n', ' ').strip()
            if len(desc) > 50: desc = desc[:50] + "..."
            
            today_str = datetime.datetime.now().strftime("%Y-%m-%d")
            # 文件名加入索引确保唯一
            filename = f"{SAVE_DIR}/{today_str}_{i}_{img_id}.jpg"
            
            try:
                print(f"      ⬇️ 下载中...")
                img_content = requests.get(img_url, timeout=20).content
                with open(filename, 'wb') as f:
                    f.write(img_content)
                
                saved_files.append({
                    "path": filename,
                    "author": author_name,
                    "author_link": author_link,
                    "desc": desc.title()
                })
                print(f"      ✅ 保存成功")
            except Exception as e:
                print(f"      ❌ 下载保存失败: {e}")
        
        # 稍微暂停，礼貌调用 API
        time.sleep(1)
            
    return saved_files

def update_readme(new_images):
    """更新 README (保持之前的双列排版不变)"""
    if not new_images: return
    
    readme_path = "README.md"
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = "# 🌄 Daily Inspiration Gallery\n\n每天更新的视觉灵感库。精选积极向上、震撼人心的史诗级壁纸。\n\n---"

    # 构造 HTML 表格内容 (每行2张图)
    new_entry = f"\n### 📅 {today_str} 精选集\n\n<table>\n"
    
    for i in range(0, len(new_images), 2):
        img1 = new_images[i]
        img2 = new_images[i+1] if i+1 < len(new_images) else None
        
        new_entry += "  <tr>\n"
        # 左侧
        new_entry += f"    <td width='50%' align='center' style='border:none; padding:10px'>\n"
        new_entry += f"      <img src='{img1['path']}' width='100%' style='border-radius:8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1)'><br>\n"
        new_entry += f"      <sub style='color:#666'><b>{img1['desc']}</b><br>by <a href='{img1['author_link']}'>{img1['author']}</a></sub>\n"
        new_entry += "    </td>\n"
        # 右侧
        if img2:
            new_entry += f"    <td width='50%' align='center' style='border:none; padding:10px'>\n"
            new_entry += f"      <img src='{img2['path']}' width='100%' style='border-radius:8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1)'><br>\n"
            new_entry += f"      <sub style='color:#666'><b>{img2['desc']}</b><br>by <a href='{img2['author_link']}'>{img2['author']}</a></sub>\n"
            new_entry += "    </td>\n"
        else:
            new_entry += "    <td width='50%' style='border:none'></td>\n" 
        new_entry += "  </tr>\n"

    new_entry += "</table>\n\n---\n"

    # 插入到顶部
    marker = "---"
    if marker in content:
        header_end_index = content.find(marker) + len(marker)
        final_content = content[:header_end_index] + new_entry + content[header_end_index:]
    else:
        final_content = content + new_entry

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(final_content)

if __name__ == "__main__":
    if not UNSPLASH_ACCESS_KEY:
        print("❌ 错误: 未设置 UNSPLASH_ACCESS_KEY 密钥")
        exit(1)

    images = download_images()
    if images:
        update_readme(images)
        print(f"🎉 成功采集 {len(images)} 张高质量壁纸！README已更新。")
    else:
        print("⚠️ 本次运行未下载到任何图片，请检查日志。")
