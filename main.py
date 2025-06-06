import aiohttp
import asyncio
import time
from datetime import datetime, timedelta, date
from threading import Lock
from bs4 import BeautifulSoup
import requests 
import tempfile
import subprocess, sys
import random
import json
import os
import sqlite3
import hashlib
import zipfile
from PIL import Image, ImageOps, ImageDraw, ImageFont
from io import BytesIO
from urllib.parse import urljoin, urlparse, urldefrag
from telebot import TeleBot, types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from keep_alive import keep_alive

THỜI_GIAN_CHỜ = timedelta(seconds=300)
FREE_GIỚI_HẠN_CHIA_SẺ = 400
VIP_GIỚI_HẠN_CHIA_SẺ = 1000
viptime = 100
ALLOWED_GROUP_ID = -1002892964030   # ID BOX
admin_diggory = "huymoddeptrai" # ví dụ : để user name admin là @diggory347 bỏ dấu @ đi là đc
name_bot = "Bot Spam Sms"
zalo = "0896874211"
web = "no"
facebook = "no"
allowed_group_id = -1002892964030 # ID BOX
users_keys = {}
key = ""
freeuser = []
auto_spam_active = False
last_sms_time = {}
allowed_users = []
processes = []
ADMIN_ID =  6871691882 # ID ADMIN
connection = sqlite3.connect('user_data.db')
cursor = connection.cursor()
last_command_time = {}


user_cooldowns = {}
share_count = {}
global_lock = Lock()
admin_mode = False
share_log = []
tool = 'Có C'
BOT_LINK = 'https://t.me/ToolBotSpamCallSms_Bot'
TOKEN = '7880421103:AAFv-xyZ2iA4bF4aJAuHEFK6YJ3PyuKrMmU'  
bot = TeleBot(TOKEN)

ADMIN_ID = 6871691882  # id admin
admins = {6871691882}
bot_admin_list = {}
cooldown_dict = {}
allowed_users = []
muted_users = {}

def get_time_vietnam():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
def check_command_cooldown(user_id, command, cooldown):
    current_time = time.time()
    
    if user_id in last_command_time and current_time - last_command_time[user_id].get(command, 0) < cooldown:
        remaining_time = int(cooldown - (current_time - last_command_time[user_id].get(command, 0)))
        return remaining_time
    else:
        last_command_time.setdefault(user_id, {})[command] = current_time
        return None

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        expiration_time TEXT
    )
''') 
connection.commit()

def TimeStamp():
  now = str(date.today())
  return now


def load_users_from_database():
  cursor.execute('SELECT user_id, expiration_time FROM users')
  rows = cursor.fetchall()
  for row in rows:
    user_id = row[0]
    expiration_time = datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
    if expiration_time > datetime.now():
      allowed_users.append(user_id)


def save_user_to_database(connection, user_id, expiration_time):
  cursor = connection.cursor()
  cursor.execute(
    '''
        INSERT OR REPLACE INTO users (user_id, expiration_time)
        VALUES (?, ?)
    ''', (user_id, expiration_time.strftime('%Y-%m-%d %H:%M:%S')))
  connection.commit()
###



###
####
start_time = time.time()

def load_allowed_users():
    try:
        with open('admin_vip.txt', 'r') as file:
            allowed_users = [int(line.strip()) for line in file]
        return set(allowed_users)
    except FileNotFoundError:
        return set()

vip_users = load_allowed_users()

async def share_post(session, token, post_id, share_number):
    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate',
        'connection': 'keep-alive',
        'content-length': '0',
        'host': 'graph.facebook.com'
    }
    try:
        url = f'https://graph.facebook.com/me/feed'
        params = {
            'link': f'https://m.facebook.com/{post_id}',
            'published': '0',
            'access_token': token
        }
        async with session.post(url, headers=headers, params=params) as response:
            res = await response.json()
            print(f"Chia sẻ bài viết thành công: {res}")
    except Exception as e:
        print(f"Lỗi khi chia sẻ bài viết: {e}")

async def get_facebook_post_id(session, post_url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, như Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

        async with session.get(post_url, headers=headers) as response:
            response.raise_for_status()
            text = await response.text()

        soup = BeautifulSoup(text, 'html.parser')
        meta_tag = soup.find('meta', attrs={'property': 'og:url'})

        if meta_tag and 'content' in meta_tag.attrs:
            linkpost = meta_tag['content'].split('/')[-1]
            async with session.post('https://scaninfo.vn/api/fb/getID.php?url=', data={"link": linkpost}) as get_id_response:
                get_id_post = await get_id_response.json()
                if 'success' in get_id_post:
                    post_id = get_id_post["id"]
                return post_id
        else:
            raise Exception("Không tìm thấy ID bài viết trong các thẻ meta")

    except Exception as e:
        return f"Lỗi: {e}"


@bot.message_handler(commands=['time'])
def handle_time(message):
    uptime_seconds = int(time.time() - start_time)
    
    uptime_minutes, uptime_seconds = divmod(uptime_seconds, 60)
    bot.reply_to(message, f'Bot đã hoạt động được: {uptime_minutes} phút, {uptime_seconds} giây')
#tiktok
def fetch_tiktok_data(url):
    api_url = f'https://scaninfo.vn/api/down/tiktok.php?url={url}'
    try:
        response = requests.get(api_url)
        response.raise_for_status()  
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching TikTok data: {e}")
        return None

@bot.message_handler(commands=['tiktok'])
def tiktok_command(message):
    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) == 2:
        url = command_parts[1].strip()
        data = fetch_tiktok_data(url)
        
        if data and 'code' in data and data['code'] == 0:
            video_title = data['data'].get('title', 'N/A')
            video_url = data['data'].get('play', 'N/A')
            music_title = data['data']['music_info'].get('title', 'N/A')
            music_url = data['data']['music_info'].get('play', 'N/A')
            
            reply_message = f"Tiêu đề Video: {video_title}\nĐường dẫn Video: {video_url}\n\nTiêu đề Nhạc: {music_title}\nĐường dẫn Nhạc: {music_url}"
            bot.reply_to(message, reply_message)
        else:
            bot.reply_to(message, "Không thể lấy dữ liệu từ TikTok.")
    else:
        bot.reply_to(message, "Hãy cung cấp một đường dẫn TikTok hợp lệ.")


@bot.message_handler(commands=['tool'])
def send_tool_links(message):
    markup = types.InlineKeyboardMarkup()
    
    tool_links = [
        ("https://ducthinhexe.github.io/huongdan", "Tool gộp vip"),
        ("https://ducthinhexe.github.io/huongdan", "Tool Golike Tiktok"),
        ("https://ducthinhexe.github.io/huongdan", "Tool Gộp - Source")
    ]
    
    for link, desc in tool_links:
        markup.add(types.InlineKeyboardButton(text=desc, url=link))
    
    bot.reply_to(message, "Chọn một tool từ bên dưới(2 cũng đc):", reply_markup=markup)
####
#####
video_url = 'https://v16m-default.akamaized.net/b7650db4ac7f717b7be6bd6a04777a0d/66a418a5/video/tos/useast2a/tos-useast2a-ve-0068-euttp/o4QTIgGIrNbkAPGKKLKteXyLedLE7IEgeSzeE2/?a=0&bti=OTg7QGo5QHM6OjZALTAzYCMvcCMxNDNg&ch=0&cr=0&dr=0&lr=all&cd=0%7C0%7C0%7C0&cv=1&br=2576&bt=1288&cs=0&ds=6&ft=XE5bCqT0majPD12cy-773wUOx5EcMeF~O5&mime_type=video_mp4&qs=0&rc=Mzk1OzY7PGdpZjxkOTQ3M0Bpajh1O2w5cmlzbzMzZjgzM0AuNWJgLi02NjMxLzBgXjUyYSNzNmptMmRjazFgLS1kL2Nzcw%3D%3D&vvpl=1&l=202407261543513F37EAD38E23B6263167&btag=e00088000'
@bot.message_handler(commands=['add', 'adduser'])
def add_user(message):
    admin_id = message.from_user.id
    if admin_id != ADMIN_ID:
        bot.reply_to(message, 'BẠN KHÔNG CÓ QUYỀN SỬ DỤNG LỆNH NÀY')
        return

    if len(message.text.split()) == 1:
        bot.reply_to(message, 'VUI LÒNG NHẬP ID NGƯỜI DÙNG')
        return

    user_id = int(message.text.split()[1])
    allowed_users.append(user_id)
    expiration_time = datetime.now() + timedelta(days=30)
    connection = sqlite3.connect('user_data.db')
    save_user_to_database(connection, user_id, expiration_time)
    connection.close()

    # Gửi video với tiêu đề
    caption_text = (f'NGƯỜI DÙNG CÓ ID {user_id}                                ĐÃ ĐƯỢC THÊM VÀO DANH SÁCH ĐƯỢC PHÉP SỬ DỤNG LỆNH /spamvip')
    bot.send_video(
        message.chat.id,
        video_url,
        caption=caption_text
    )

load_users_from_database()

def is_key_approved(chat_id, key):
    if chat_id in users_keys:
        user_key, timestamp = users_keys[chat_id]
        if user_key == key:
            current_time = datetime.datetime.now()
            if current_time - timestamp <= datetime.timedelta(hours=2):
                return True
            else:
                del users_keys[chat_id]
    return False

@bot.message_handler(commands=['share'])
def share(message):
    global bot_active, global_lock, admin_mode
    chat_id = message.chat.id
    user_id = message.from_user.id
    current_time = datetime.now()


    if not bot_active:
        msg = bot.reply_to(message, 'Bot hiện đang tắt.')
        time.sleep(10)
        try:
            bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        except telebot.apihelper.ApiTelegramException as e:
            print(f"Error deleting message: {e}")
        return

    if chat_id != ALLOWED_GROUP_ID:
        msg = bot.reply_to(message, 'Làm Trò Gì Khó Coi Vậy')
        time.sleep(10)
        try:
            bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        except telebot.apihelper.ApiTelegramException as e:
            print(f"Error deleting message: {e}")
        return
    
    if admin_mode and user_id not in admins:
        msg = bot.reply_to(message, 'Chế độ admin hiện đang bật, đợi tí đi.')
        time.sleep(10)
        try:
            bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        except telebot.apihelper.ApiTelegramException as e:
            print(f"Error deleting message: {e}")
        return
    
    try:
        global_lock.acquire()  
        
        args = message.text.split()
        if user_id not in allowed_users and user_id not in freeuser:
            bot.reply_to(message, 'bot chỉ hoạt động khi bạn mua key và get key bằng lệnh /laykey')
            return
        if len(args) != 3:
            msg = bot.reply_to(message, '''
╔══════════════════
║<|> /laykey trước khi sài hoặc mua
║<|> /key <key> để nhập key 
║<|> ví dụ /key ABCDXYZ
║<|> /share {link_buff} {số lần chia sẻ}
╚══════════════════''')
            time.sleep(10)
            try:
                bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
            except telebot.apihelper.ApiTelegramException as e:
                print(f"Error deleting message: {e}")
            return

        post_id, total_shares = args[1], int(args[2])

        # Kiểm tra người dùng VIP hoặc Free
        if user_id in allowed_users:
            handle_vip_user(message, user_id, post_id, total_shares, current_time)
        elif user_id in freeuser:
            handle_free_user(message, user_id, post_id, total_shares, current_time)
            
    except Exception as e:
        msg = bot.reply_to(message, f'Lỗi: {e}')
        time.sleep(10)
        try:
            bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        except telebot.apihelper.ApiTelegramException as e:
            print(f"Error deleting message: {e}")

    finally:
        if global_lock.locked():
            global_lock.release()  

def handle_vip_user(message, user_id, post_id, total_shares, current_time):
    if user_id in user_cooldowns:
        last_share_time = user_cooldowns[user_id]
        if current_time < last_share_time + timedelta(seconds=viptime):
            remaining_time = (last_share_time + timedelta(seconds=viptime) - current_time).seconds
            msg = bot.reply_to(message, f'Bạn cần đợi {remaining_time} giây trước khi chia sẻ lần tiếp theo.\nvip Delay')
            time.sleep(10)
            bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
            return
    if total_shares > VIP_GIỚI_HẠN_CHIA_SẺ:
        msg = bot.reply_to(message, f'Số lần chia sẻ vượt quá giới hạn {VIP_GIỚI_HẠN_CHIA_SẺ} lần.')
        time.sleep(10)
        bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        return
     #phân file token khác nhau
    file_path = 'token.txt'
    with open(file_path, 'r') as file:
        tokens = file.read().split('\n')

    total_live = len(tokens)

    sent_msg = bot.reply_to(message,
        f'Bot Chia Sẻ Bài Viết\n\n'
        f'║Số Lần Chia Sẻ: {total_shares}\n'
        f'║Free Max 400 Share\n'
        f'║{message.from_user.username} Đang Dùng Vip',
        parse_mode='HTML'
    )

    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
#check live token
    if total_live == 0:
        bot.edit_message_text(chat_id=message.chat.id, message_id=sent_msg.message_id, text='Không có token nào hoạt động.')
        return

    share_log.append({
        'username': message.from_user.username,
        'user_id': user_id,
        'time': current_time.strftime('%Y-%m-%d %H:%M:%S'),
        'post_id': post_id,
        'total_shares': total_shares
    })

    async def share_with_delay(session, token, post_id, count):
        await share_post(session, token, post_id, count)
        await asyncio.sleep(1)

    async def main():
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(total_shares):
                token = random.choice(tokens)
                share_number = share_count.get(user_id, 0) + 1
                share_count[user_id] = share_number
                tasks.append(share_with_delay(session, token, post_id, share_number))
            await asyncio.gather(*tasks)

    asyncio.run(main())

    bot.edit_message_text(chat_id=message.chat.id, message_id=sent_msg.message_id, text='Đơn của bạn đã hoàn thành')

def handle_free_user(message, user_id, post_id, total_shares, current_time):
    if user_id in user_cooldowns:
        last_share_time = user_cooldowns[user_id]
        if current_time < last_share_time + THỜI_GIAN_CHỜ:
            remaining_time = (last_share_time + THỜI_GIAN_CHỜ - current_time).seconds
            msg = bot.reply_to(message, f'Bạn cần đợi {remaining_time} giây trước khi chia sẻ lần tiếp theo.')
            time.sleep(10)
            bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
            return

    if total_shares > FREE_GIỚI_HẠN_CHIA_SẺ:
        msg = bot.reply_to(message, f'Số lần chia sẻ vượt quá giới hạn {FREE_GIỚI_HẠN_CHIA_SẺ} lần.')
        time.sleep(10)
        bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        return
    #token free
    file_path = 'token.txt'
    with open(file_path, 'r') as file:
        tokens = file.read().split('\n')

    total_live = len(tokens)

    sent_msg = bot.reply_to(message,
        f'Bot Chia Sẻ Bài Viết\n\n'
        f'║Số lần share: {total_shares}\n'
        f'║Vip Max 1000 Share\n'
        f'║{message.from_user.username} Đang Share Free',
        parse_mode='HTML'
    )

    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    if total_live == 0:
        bot.edit_message_text(chat_id=message.chat.id, message_id=sent_msg.message_id, text='Không có token nào hoạt động.')
        return

    share_log.append({
        'username': message.from_user.username,
        'user_id': user_id,
        'time': current_time.strftime('%Y-%m-%d %H:%M:%S'),
        'post_id': post_id,
        'total_shares': total_shares
    })

    async def share_with_delay(session, token, post_id, count):
        await share_post(session, token, post_id, count)
        await asyncio.sleep(1)

    async def main():
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(total_shares):
                token = random.choice(tokens)
                share_number = share_count.get(user_id, 0) + 1
                share_count[user_id] = share_number
                tasks.append(share_with_delay(session, token, post_id, share_number))
            await asyncio.gather(*tasks)

    asyncio.run(main())

    user_cooldowns[user_id] = current_time

    bot.edit_message_text(chat_id=message.chat.id, message_id=sent_msg.message_id, text='Đơn của bạn đã hoàn thành')
@bot.message_handler(commands=['vip'])
def handle_vip(message):
    chat_id = message.chat.id
    if message.from_user.id not in vip_users:
        bot.reply_to(message, "Bạn không phải là thành viên VIP.")
        return

   


@bot.message_handler(commands=['ls'])
def sharelog(message):
    if message.from_user.id in admins:
        if not share_log:
            bot.reply_to(message, 'chưa ai sử dụng hết')
            return
        
        log_text = "Danh sách người đã sử dụng lệnh share:\n"
        for log in share_log:
            log_text += f"<blockquote>Lịch_Sử\n- User: {log['username']} (ID: {log['user_id']})\n- vào lúc {log['time']}\n- Post LINK: <a href='{log['post_id']}'>link</a>\n- Số lần chia sẻ: {log['total_shares']}\n</blockquote>"
        
        bot.reply_to(message, log_text, parse_mode='HTML')
    else:
        bot.reply_to(message, 'admin mới xem đc á m')
@bot.message_handler(commands=['admod'])
def handle_on(message):
    global admin_mode
    if message.from_user.id in admins:
        admin_mode = True
        bot.reply_to(message, "Chế độ admin đã bật.")
    else:
        bot.reply_to(message, "Bạn không có quyền bật chế độ admin.")

@bot.message_handler(commands=['laykey'])
def laykey(message):
    bot.reply_to(message, text='VUI LÒNG ĐỢI TRONG GIÂY LÁT!')

    with open('key.txt', 'a') as f:
        f.close()

    user_id = message.from_user.id  
    string = f'GL-{user_id}+{TimeStamp()}'  
    hash_object = hashlib.md5(string.encode())
    key = str(hash_object.hexdigest())[:10]
    print(key)
    
    url_key = requests.get(f'https://yeumoney.com/QL_api.php?token=eee97ade0e7401a23d12ce61158be94906f9f098c9b7f9c2599e50bb6a7ef5c3&format=json&url=https://jirayshop.xyz/key.php?r={key}').json()['shortenedUrl']
    
    text = f'''
- KEY CỦA BẠN {get_time_vietnam()}
- DÙNG LỆNH /key {{key}} ĐỂ TIẾP TỤC -
 [Lưu ý: mỗi key chỉ có 1 người dùng]
    '''

    keyboard = InlineKeyboardMarkup()
    url_button = InlineKeyboardButton(text="Get Key", url=url_key)
    admin_button = InlineKeyboardButton(text="WED TẢI ALL TOOL", url="https://jirayshop.xyz/")
    keyboard.add(url_button, admin_button)
    
    bot.reply_to(message, text, reply_markup=keyboard)
    
    admin_message = f"Key Của {user_id}: {key}\n bạn có thể đưa key này cho id người nhận"
    bot.send_message(ADMIN_ID, admin_message)

@bot.message_handler(commands=['key'])
def key(message):
    if len(message.text.split()) == 1:
        bot.reply_to(message, 'CHƯA NHẬP KEY MÀ')
        return

    user_id = message.from_user.id
    
    key = message.text.split()[1]
    string = f'GL-{user_id}+{TimeStamp()}'  
    hash_object = hashlib.md5(string.encode())
    expected_key = str(hash_object.hexdigest())[:10]
    if key == expected_key:
        freeuser.append(user_id)
        bot.reply_to(message, 'KEY ĐÚNG BẠN CÓ THỂ TIẾP TỤC SỬ DỤNG LỆNH')
    else:
        bot.reply_to(message, 'KEY SAI R GET LẠI THỬ XEM HOẶC IB CHO ADMIN')


@bot.message_handler(commands=['unadmod'])
def handle_off(message):
    global admin_mode
    if message.from_user.id in admins:
        admin_mode = False
        bot.reply_to(message, "Chế độ admin đã tắt.")
    else:
        bot.reply_to(message, "Bạn không có quyền tắt chế độ admin.")
@bot.message_handler(commands=['off'])
def bot_off(message):
    global bot_active
    if message.from_user.id in admins:
        bot_active = False
        bot.reply_to(message, 'Bot đã được tắt.')
    else:
        bot.reply_to(message, 'Bạn không có quyền thực hiện thao tác này.')
@bot.message_handler(commands=['on'])
def bot_on(message):
    global bot_active
    if message.from_user.id in admins:
        bot_active = True
        bot.reply_to(message, 'Bot đã được bật.')
    else:
        bot.reply_to(message, 'Bạn không có quyền thực hiện thao tác này.')
@bot.message_handler(commands=['code'])
def handle_code_command(message):
    # Tách lệnh và URL từ tin nhắn
    command_args = message.text.split(maxsplit=1)

    # Kiểm tra xem URL có được cung cấp không
    if len(command_args) < 2:
        bot.reply_to(message, "Vui lòng cung cấp url sau lệnh /code. Ví dụ: /code https://xnxx.com")
        return

    url = command_args[1]
    domain = urlparse(url).netloc
    file_name = f"{domain}.txt"
    
    try:
        # Lấy nội dung HTML từ URL
        response = requests.get(url)
        response.raise_for_status()  # Xảy ra lỗi nếu có lỗi HTTP

        # Lưu nội dung HTML vào file
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(response.text)

        # Gửi file về người dùng
        with open(file_name, 'rb') as file:
            bot.send_document(message.chat.id, file, caption=f"HTML của trang web {url}")

        # Phản hồi tin nhắn gốc
        bot.reply_to(message, "Đã gửi mã nguồn HTML của trang web cho bạn.")

    except requests.RequestException as e:
        bot.reply_to(message, f"Đã xảy ra lỗi khi tải trang web: {e}")

    finally:
        # Đảm bảo xóa file sau khi gửi
        if os.path.exists(file_name):
            try:
                os.remove(file_name)
            except Exception as e:
                bot.reply_to(message, f"Đã xảy ra lỗi khi xóa file: {e}")
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
   
   
    username = message.from_user.username
    bot.reply_to(message, f'''
┌───⭓ {name_bot}
│» Xin chào @{username}
│» /help : Lệnh trợ giúp
│» /admin : Thông tin admin
│» /spam : Spam SMS FREE
│» /spamvip : Spam SMS VIP - Mua Vip 30k/Tháng
│» /share : Free 400 - Vip 1k share trên lần
│» /id : Lấy ID Tele Của Bản Thân
│» /voice : Đổi Văn Bản Thành Giọng Nói.
│» /tiktok : Check Thông Tin - Tải Video Tiktok.
│» /time : check thời gian hoạt động
│» /ad : có bao nhiêu admin
│» /code : Lấy Code html của web
│» /tv : Đổi Ngôn Ngữ Sang Tiếng Việt
│» Lệnh Cho ADMIN
│» /rs : Khởi Động Lại
│» /add : Thêm người dùng sử dụng /spamvip
└───────────⧕
    ''')
@bot.message_handler(commands=['admin'])
def diggory(message):
     
    username = message.from_user.username
    diggory_chat = f'''
┌───⭓ {name_bot}
│» Xin chào @{username}
│» Bot Spam : Vay Luon Ha
│» Zalo: {zalo}
│» Website: {web}
│» Telegram: @{admin_diggory}
└──────────────
    '''
    bot.send_message(message.chat.id, diggory_chat)


last_usage = {}

@bot.message_handler(commands=['spam'])
def spam(message):
    user_id = message.from_user.id
    current_time = time.time()
    if not bot_active:
        msg = bot.reply_to(message, 'Bot hiện đang tắt.')
        time.sleep(10)
        try:
            bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        except telebot.apihelper.ApiTelegramException as e:
            print(f"Error deleting message: {e}")
        return
    if admin_mode and user_id not in admins:
        msg = bot.reply_to(message, 'có lẽ admin đang fix gì đó hãy đợi xíu')
    if user_id in last_usage and current_time - last_usage[user_id] < 100:
        bot.reply_to(message, f"Vui lòng đợi {100 - (current_time - last_usage[user_id]):.1f} giây trước khi sử dụng lệnh lại.")
        return

    last_usage[user_id] = current_time

    # Phân tích cú pháp lệnh
    params = message.text.split()[1:]
    if len(params) != 2:
        bot.reply_to(message, "/spam sdt số_lần như này cơ mà - vì lý do server treo bot hơi cùi nên đợi 100giây nữa dùng lại nhé")
        return

    sdt, count = params

    if not count.isdigit():
        bot.reply_to(message, "Số lần spam không hợp lệ. Vui lòng chỉ nhập số.")
        return

    count = int(count)

    if count > 5:
        bot.reply_to(message, "/spam sdt số_lần tối đa là 5 - đợi 100giây sử dụng lại.")
        return

    if sdt in blacklist:
        bot.reply_to(message, f"Số điện thoại {sdt} đã bị cấm spam.")
        return

    diggory_chat3 = f'''
┌──────⭓ {name_bot}
│ Spam: Thành Công 
│ Số Lần Spam Free: {count}
│ Đang Tấn Công : {sdt}
│ Spam 5 Lần Tầm 1-2p mới xong 
│ Hạn Chế Spam Nhé !  
└─────────────
    '''

    script_filename = "dec.py"  # Tên file Python trong cùng thư mục
    try:
        # Kiểm tra xem file có tồn tại không
        if not os.path.isfile(script_filename):
            bot.reply_to(message, "Không tìm thấy file script. Vui lòng kiểm tra lại.")
            return

        # Đọc nội dung file với mã hóa utf-8
        with open(script_filename, 'r', encoding='utf-8') as file:
            script_content = file.read()

        # Tạo file tạm thời
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
            temp_file.write(script_content.encode('utf-8'))
            temp_file_path = temp_file.name

        # Chạy file tạm thời
        process = subprocess.Popen(["python", temp_file_path, sdt, str(count)])
        bot.send_message(message.chat.id, diggory_chat3)
    except FileNotFoundError:
        bot.reply_to(message, "Không tìm thấy file.")
    except Exception as e:
        bot.reply_to(message, f"Lỗi xảy ra: {str(e)}")



blacklist = ["112", "113", "114", "115", "116", "117", "118", "119", "0", "0896874211", "2", "3", "4"]


# Xử lý lệnh /spamvip
@bot.message_handler(commands=['spamvip'])
def supersms(message):
    user_id = message.from_user.id
    if user_id not in allowed_users:
        bot.reply_to(message, 'Hãy Mua Vip Để Sử Dụng.')
        return
    
    current_time = time.time()
    if user_id in last_usage and current_time - last_usage[user_id] < 1:
        bot.reply_to(message, f"Vui lòng đợi {250 - (current_time - last_usage[user_id]):.1f} giây trước khi sử dụng lệnh lại.")
        return
    
    last_usage[user_id] = current_time

    params = message.text.split()[1:]

    if len(params) != 2:
        bot.reply_to(message, "/spamvip sdt số_lần như này cơ mà ")
        return

    sdt, count = params

    if not count.isdigit():
        bot.reply_to(message, "Số lần spam không hợp lệ. Vui lòng nhập một số nguyên dương.")
        return
    
    count = int(count)
    
    if count > 30:
        bot.reply_to(message, "/spamvip sdt 30 thôi nhé - đợi 250giây sử dụng lại.")
        return

    if sdt in blacklist:
        bot.reply_to(message, f"Số điện thoại {sdt} đã bị cấm spam.")
        return

    diggory_chat3 = f'''
┌──────⭓ {name_bot}
│ Spam: Thành Công 
│ Số Lần Spam Vip: {count}
│ Đang Tấn Công : {sdt}
│ Spam 30 Lần Tầm 5-10p mới xong 
│ Hạn Chế Spam Nhé !  
└─────────────
    '''

    script_filename = "dec.py"  # Tên file Python trong cùng thư mục
    try:
        if os.path.isfile(script_filename):
            with open(script_filename, 'r', encoding='utf-8') as file:
                script_content = file.read()

            with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
                temp_file.write(script_content.encode('utf-8'))
                temp_file_path = temp_file.name

            process = subprocess.Popen(["python", temp_file_path, sdt, str(count)])
            bot.send_message(message.chat.id, diggory_chat3)
        else:
            bot.reply_to(message, "Tập tin không tìm thấy.")
    except Exception as e:
        bot.reply_to(message, f"Lỗi xảy ra: {str(e)}")

# Xử lý lệnh /voice
API_URL = "https://scaninfo.vn/api/gg/voice.php?text={}"

@bot.message_handler(commands=['voice'])
def handle_voice_command(message):
    text = message.text.split('/voice ', 1)[1].strip()
    api_request_url = API_URL
    response = requests.post(api_request_url, data={'text': text})
    if response.status_code == 200:
        audio_data = response.content
        if audio_data:
            bot.send_voice(message.chat.id, audio_data, caption=f"Nội dung: {text}", reply_to_message_id=message.message_id)
        else:
            bot.reply_to(message, f"@{message.from_user.username} Không thể tạo giọng nói từ văn bản này.")
    else:
        bot.reply_to(message, f"@{message.from_user.username} Đã xảy ra lỗi khi chuyển đổi văn bản thành giọng nói.")

ADMIN_NAME = "DucThinhEXE"

@bot.message_handler(commands=['ad'])
def send_admin_info(message):
    bot.send_message(
        message.chat.id, 
        f"Only One => Is : {ADMIN_NAME}\nID: `{ADMIN_ID}`", 
        parse_mode='Markdown'
    )

@bot.message_handler(func=lambda message: message.text.isdigit())
def copy_user_id(message):
    bot.send_message(message.chat.id, f"ID của bạn đã được sao chép: `{message.text}`", parse_mode='Markdown')
ADMIN_NAME = "DucThinhEXE"
@bot.message_handler(commands=['id'])
def get_user_id(message):
    if len(message.text.split()) == 1:  
        user_id = message.from_user.id
        bot.reply_to(message, f"ID của bạn là: `{user_id}`", parse_mode='Markdown')
    else:  
        username = message.text.split('@')[-1].strip()
        try:
            user = bot.get_chat(username)  # Lấy thông tin người dùng từ username
            bot.reply_to(message, f"ID của {user.first_name} là: `{user.id}`", parse_mode='Markdown')
        except Exception as e:
            bot.reply_to(message, "Không tìm thấy người dùng có username này.")
@bot.message_handler(commands=['ID'])
def handle_id_command(message):
    chat_id = message.chat.id
    bot.reply_to(message, f"ID của nhóm này là: {chat_id}")
####################
import time

def restart_program():
    """Khởi động lại script chính và môi trường chạy."""
    python = sys.executable
    script = sys.argv[0]
    # Khởi động lại script chính từ đầu
    try:
        subprocess.Popen([python, script])
    except Exception as e:
        print(f"Khởi động lại không thành công: {e}")
    finally:
        time.sleep(10)  # Đợi một chút để đảm bảo instance cũ đã ngừng hoàn toàn
        sys.exit()

@bot.message_handler(commands=['rs'])
def handle_reset(message):
    if message.from_user.id == ADMIN_ID:
        bot.reply_to(message, "Bot đang khởi động lại...")
        restart_program()
    else:
        bot.reply_to(message, "Bạn không có quyền truy cập vào lệnh này!")
####
@bot.message_handler(commands=['tv'])
def tieng_viet(message):
    chat_id = message.chat.id
    message_id = message.message_id
    
    keyboard = types.InlineKeyboardMarkup()
    url_button = types.InlineKeyboardButton("Tiếng Việt 🇻🇳", url='https://t.me/setlanguage/abcxyz')
    keyboard.add(url_button)
    
    bot.send_message(chat_id, 'Click Vào Nút "<b>Tiếng Việt</b>" để đổi thành tv VN in đờ bét.', reply_markup=keyboard, parse_mode='HTML')
    
    # Delete user's command message
    try:
        bot.delete_message(chat_id, message_id)
    except Exception as e:
        bot.send_message(chat_id, f"Không thể xóa tin nhắn: {e}", parse_mode='HTML')

############
if __name__ == "__main__":
    bot_active = True
    keep_alive()
    bot.infinity_polling()