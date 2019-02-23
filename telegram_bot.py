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
        self.ar_url = [self.get_url("pm1"), self.get_url("pm2.5"), self.get_url("pm10"), self.get_url("so2smass")]
        self.driver = webdriver.Chrome('chromedriver.exe', chrome_options=options)

        self.driver.get(self.ar_url[2])

        self.remove_element("/html/head")
        self.remove_element("/html/body/script")
        self.removes(["display", "tara-stats", "sponsor", "notice", "settings-wrap", "calendar-wrapper", "earth", "status"])

    def get_url(self, overlay):
        domain = "https://earth.nullschool.net/"
        orthographic = "126.92,37.38,3000"
        loc = "126.922,37.383"
        return domain + "#current/particulates/surface/level/overlay=" + overlay + "/orthographic=" + orthographic + "/loc=" + loc

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

    def run(self):
        ar = []

        for url in self.ar_url:
            self.driver.get(url)
            ar.append(self.get_value())

        self.str = ""
        self.str += "[미세먼지 정보]\n"
        self.str += "극초미세 " + ar[0] + "\n"
        self.str += "초미세    " + ar[1] + "\n"
        self.str += "미세먼지 " + ar[2] + "\n"
        self.str += "이산화황 " + ar[3] + "\n"

        return self.str


# =========================
# telegram
# =========================

import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

class TelegramBot:
    def __init__(self, token):
        self.core = telegram.Bot(token)
        self.updater = Updater(token)

    def start(self):
        self.updater.start_polling()
        self.updater.idle()

    def stop(self):
        self.updater.start_polling()
        self.updater.dispatcher.stop()
        self.updater.job_queue.stop()
        self.updater.stop()

    def send_message(self, id, text):
        return self.core.sendMessage(chat_id = id, text=text)

    def delete_message(self, chat_id, message_id):
        self.core.deleteMessage(chat_id, message_id)

    def add_handler(self, cmd, func):
        self.updater.dispatcher.add_handler(CommandHandler(cmd, func))

    def message_handler(self, func):
        self.updater.dispatcher.add_handler(MessageHandler(Filters.text, func))

#======================


MSG_HOW_TO = '사용방법\n/air'
ar_id = {688899662, 421152487}
def proc_start(bot, update):
    ar_id.add(update.message.chat.id)
    print(ar_id)
    bot.send_message(update.message.chat.id, MSG_HOW_TO)

def proc_message(bot, update):
    ar_id.add(update.message.chat.id)
    print(ar_id)
    update.message.reply_text(MSG_HOW_TO)

def proc_air(bot, update):
    ar_id.add(update.message.chat.id)
    print(ar_id)
    #result = bot.send_message(update.message.chat.id, '수집중...')
    str = crawling.run()
    bot.send_message(update.message.chat.id, str)
    #bot.delete_message(update.message.chat.id, result.message_id)


def proc_call(bot, update):
    #result = bot.send_message(update.message.chat.id, '수집중...')
    str = crawling.run()
    for id in ar_id:
        bot.send_message(id, str)
    #bot.delete_message(update.message.chat.id, result.message_id)

import config

crawling = CrawlingBot()
bot = TelegramBot(config.BOT_ACCESS_TOKEN)
bot.add_handler('start', proc_start)
bot.add_handler('air', proc_air)
bot.add_handler('call', proc_call)
bot.message_handler(proc_message)
bot.start()
