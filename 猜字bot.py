import discord
import random

# 設定機器人前綴及權限
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# 定義全局變量
word_list = []
current_word = ""
current_display = ""
guessed_letters = set()

# 載入單字庫
def load_word_list():
    global word_list
    try:
        with open('words.txt', 'r', encoding='utf-8') as f:
            word_list = f.read().splitlines()
    except FileNotFoundError:
        word_list = ["example", "discord", "python", "robot"]  # 默認單字庫

# 隨機選擇一個單字
def get_random_word():
    return random.choice(word_list)

# 初始化遊戲狀態
def start_new_game():
    global current_word, current_display, guessed_letters
    current_word = get_random_word()
    current_display = ''.join(['-' if c.isalpha() else c for c in current_word])  # 顯示未猜出的字母
    guessed_letters = set()

# 更新顯示的字母
def update_display(guess):
    global current_display
    new_display = list(current_display)
    for i, c in enumerate(current_word):
        if c.lower() == guess.lower():  # 比較時不區分大小寫
            new_display[i] = c  # 保留原始字母大小寫
    current_display = ''.join(new_display)

# 處理猜測
def process_guess(user_id, guess):
    global current_display, guessed_letters

    if guess in guessed_letters:
        return f"你已經猜過字母 '{guess}' 了！"
    
    guessed_letters.add(guess)

    if guess.lower() in current_word.lower():  # 比較時不區分大小寫
        update_display(guess)
        if current_display == current_word:
            result = f"恭喜！你猜中了整個單字 '{current_word}'！"
            start_new_game()  # 開始新一局
            return result
        return f"字母 '{guess}' 正確！目前狀態: {current_display}"
    else:
        return f"字母 '{guess}' 不在單字中！"

# 顯示正確的答案
def reveal_answer():
    return f"正確答案是: {current_word}"

# 開始新的遊戲
@client.event
async def on_ready():
    print(f'已登入為 {client.user}')
    load_word_list()
    start_new_game()

# 處理訊息
@client.event
async def on_message(message):
    if message.author == client.user:  # 忽略機器人的消息
        return

    # 玩家猜測字母或單字
    if message.content.startswith('!guess'):
        guess = message.content[len('!guess '):].strip().lower()

        # 檢查玩家是否猜測了一個單個字母
        if len(guess) == 1:  # 單個字母
            result = process_guess(message.author.id, guess)
            await message.channel.send(result)

        # 檢查玩家是否猜測了整個單字
        elif guess == current_word.lower():  # 整個單字猜測，忽略大小寫
            result = f"恭喜！你猜中了整個單字 '{current_word}'！"
            start_new_game()  # 開始新一局
            await message.channel.send(result)

        else:
            await message.channel.send(f"你猜的單字 '{guess}' 不正確！")

    # 結束遊戲並顯示答案
    elif message.content == '!endgame':  # 結束遊戲並公布解答
        await message.channel.send(reveal_answer())
        start_new_game()  # 遊戲結束後自動開始新一局
        await message.channel.send(f"遊戲已重新開始！猜測單字: {current_display}")

    # 開始新遊戲
    elif message.content == '!newgame':  # 開始新遊戲
        start_new_game()
        await message.channel.send(f"遊戲已重新開始！猜測單字: {current_display}")

# 啟動機器人
client.run('token')
