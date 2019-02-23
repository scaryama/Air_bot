# =========================
# crawling
# =========================
from selenium import webdriver
from selenium.webdriver.common.by import By

class CrawlingBot:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('headless')

        self.count = 0
        self.time_prev = ""
        self.domain = "https://earth.nullschool.net/#current/particulates/surface/level"
        self.loc = ""

        self.driver = webdriver.Chrome('chromedriver.exe', chrome_options=options)
        self.driver.get(self.domain)

        self.remove_element("/html/head")
        self.remove_element("/html/body/script")
        self.removes(["display", "tara-stats", "sponsor", "notice", "settings-wrap", "calendar-wrapper", "earth", "status"])
        print("Ready crawling")

    def get_url(self, overlay):
        return self.domain + "/overlay=" + overlay + "/loc=" + self.loc

    def remove_element(self, xpath):
        self.driver.execute_script("""
        var element = arguments[0];
        element.parentNode.removeChild(element);
        """, self.driver.find_element(By.XPATH, xpath))

    def removes(self, ar):
        for id in ar:
            self.remove_element("//*[@id=\"" + id + "\"]")

    def get_value(self):
        while True:
            element = self.driver.find_element(By.XPATH, "//*[@id=\"location-value\"]")
            value = element.text
            if len(value) > 0:
                self.driver.execute_script("arguments[0].innerHTML=''", element)
                break
        return value

    def run(self, loc):
        self.loc = loc
        self.ar_url = [self.get_url("pm1"), self.get_url("pm2.5"), self.get_url("pm10"), self.get_url("so2smass")]
        ar = []
        for url in self.ar_url:
            self.driver.get(url)
            ar.append(self.get_value())

        self.str = ""
        self.str += "[미세먼지 정보]\n"
        self.str += "이산화황 " + ar[3] + "\n"
        self.str += "극초미세 " + ar[0] + "\n"
        self.str += "초미세    " + ar[1] + "\n"
        self.str += "미세먼지 " + ar[2] + "\n"

        return self.str

# =========================
# telegram
# =========================
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import config


MSG_HOW_TO = '명령어 /air'
ar_admin = {688899662, 421152487}
dic_loc = {}
def proc_start(bot, update):
    id = update.message.chat.id
    #bot.send_message(id, MSG_HOW_TO)
    location_keyboard = telegram.KeyboardButton(text="시작", request_location=True)
    custom_keyboard = [[location_keyboard]]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)
    bot.send_message(chat_id=id, text = "[미세먼지 정보]\n위치정보를 봇에게 전송합니다", reply_markup = reply_markup)

def proc_location(bot, update):
    id = update.message.chat.id
    dic_loc[id] = "{},{}".format(update.message.location.longitude, update.message.location.latitude)
    location_keyboard = telegram.KeyboardButton(text="/air")
    custom_keyboard = [[location_keyboard]]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)
    str = crawling.run(dic_loc[id])
    bot.send_message(chat_id=id, text=str, reply_markup=reply_markup)
    bot.send_message(chat_id=id, text="다음에 또 불러주세요\n"+MSG_HOW_TO)

def check_init(bot, update):
    if len(dic_loc) == 0:
        proc_start(bot, update)
        return True
    else:
        return False

def proc_air(bot, update):
    if check_init(bot, update):
        return
    id = update.message.chat.id
    str = crawling.run(dic_loc[id])
    bot.send_message(id, str)

def proc_call(bot, update):
    if check_init(bot, update):
        return
    str = crawling.run(dic_loc[id])
    for id in ar_admin:
        bot.send_message(id, str)

def proc_message(bot, update):
    if check_init(bot, update):
        return
    update.message.reply_text(MSG_HOW_TO)

crawling = CrawlingBot()

#init
updater = Updater(config.BOT_ACCESS_TOKEN)

#add event
updater.dispatcher.add_handler(CommandHandler('start', proc_start))
updater.dispatcher.add_handler(CommandHandler('air', proc_air))
updater.dispatcher.add_handler(CommandHandler('call', proc_call))
updater.dispatcher.add_handler(MessageHandler(Filters.text, proc_message))
updater.dispatcher.add_handler(MessageHandler(Filters.location, proc_location))

#start
updater.start_polling()
updater.idle()
