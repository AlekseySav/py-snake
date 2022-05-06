import threading
import time
import telebot
import random

token = ?????????????????  # paste your own please

LEFT = '←'
RIGHT = '→'
UP = '↑'
DOWN = '↓'
SPACE = '░'
SNAKE = '█'
FOOD = 'Q'


class Snake:
    def __init__(self, msg, w, h):
        self.field = [[SPACE for _ in range(w)] for _ in range(h)]
        self.snake = [(w // 2, h // 2)]
        self.field[self.snake[0][1]][self.snake[0][0]] = SNAKE
        self.dx = 1
        self.dy = 0
        self.stop = False
        self.msg = msg
        self.gen_food()

    def width(self):
        return len(self.field[0])

    def height(self):
        return len(self.field)

    def __str__(self):
        return '┌' + '─' * self.width() + '┐\n' + \
            '\n'.join(['│' + ''.join(i) + '│' for i in self.field]) + \
            '\n' + '└' + '─' * self.width() + '┘'

    def render(self):
        bot.edit_message_text(
            f'```\n{self}\n```', chat_id=self.msg.chat.id, message_id=self.msg.message_id)

    def sched(self):
        self.snake.insert(0, ((self.snake[0][0] + self.dx + self.width()) %
                          self.width(), (self.snake[0][1] + self.dy + self.height()) % self.height()))
        if self.field[self.snake[0][1]][self.snake[0][0]] == SNAKE:
            bot.send_message(self.msg.chat.id, 'game end!')
            self.stop = True
            print('done')
            return
        if self.field[self.snake[0][1]][self.snake[0][0]] != FOOD:
            self.field[self.snake[-1][1]][self.snake[-1][0]] = SPACE
            self.snake.pop(len(self.snake) - 1)
        else:
            self.gen_food()
        self.field[self.snake[0][1]][self.snake[0][0]] = SNAKE
        self.render()

    def gen_food(self):
        self.field[random.randint(0, self.height() - 1)
                   ][random.randint(0, self.width() - 1)] = FOOD

    def update(self, key):
        self.dx, self.dy = 0, 0
        if key == LEFT:
            self.dx = -1
        if key == RIGHT:
            self.dx = 1
        if key == UP:
            self.dy = -1
        if key == DOWN:
            self.dy = 1


games = {}

bot = telebot.TeleBot(token)

bot.parse_mode = 'markdown'


@bot.message_handler(commands=['start'])
def start(msg):
    if msg.chat.id in games:
        games.pop(msg.chat.id)

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(telebot.types.KeyboardButton(LEFT), telebot.types.KeyboardButton(
        RIGHT), telebot.types.KeyboardButton(UP), telebot.types.KeyboardButton(DOWN))
    bot.send_message(
        msg.chat.id, f'game starts here\n/start -- start game\n/end -- stop game', reply_markup=markup)
    sent = bot.send_message(msg.chat.id, f'#')
    sent.chat.id = msg.chat.id
    games[msg.chat.id] = Snake(sent, 20, 10)
    games[msg.chat.id].render()


@bot.message_handler(commands=['end'])
def start(msg):
    del games[msg.chat.id]
    bot.send_message(msg.chat.id, f'game end!')


@bot.message_handler(content_types='text')
def message_reply(msg):
    bot.delete_message(msg.chat.id, msg.message_id)
    games[msg.chat.id].update(msg.text)


n_req = 0


def update_game():
    global n_req
    while True:
        for game in games.values():
            try:
                if not game.stop:
                    game.sched()
            except:
                print('error')
            print(f'request sent {n_req}')
            n_req += 1
        time.sleep(0.8)


threading.Thread(target=update_game).start()

bot.infinity_polling()
