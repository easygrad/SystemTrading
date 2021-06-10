# pip install python-telegram-bot 설치

# 채널 id 얻기
# import telegram

# telegram_token = "1890994921:AAHOQSZF20e48btUHp5MfWa8cpJJjckjSYg"
# bot = telegram.Bot(token = telegram_token)
# updates = bot.getUpdates()
# telegram_channel_id = bot.getUpdates()[-1].message.chat.id # 가장 최근에 온 메시지의 chat id를 가져옵니다.
# print(telegram_channel_id)

from telegram import update
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
import threading

class Telegrams():

    def __init__(self):

        self.sell_temp_gubun = None
        self.tr_temp = None

        updater = Updater("1890994921:AAHOQSZF20e48btUHp5MfWa8cpJJjckjSYg", use_context=True)
        message_handler = MessageHandler(Filters.text & (~Filters.command), self.get_message) # get_message 메시지 수신하는 곳
        updater.dispatcher.add_handler(message_handler)

        updater.bot.send_message(chat_id="393093230", text="텔레그램 활성화") # 단순 메시지 전송법 send_message

        threading.Thread(target=self.check_msg, args=(updater,)).start()

        help_handler = CommandHandler('help', self.help_command)
        updater.dispatcher.add_handler(help_handler)
        
        help_handler = CommandHandler('stocks_sell', self.sell_command) # 종목매도_sell 한글 안 돼서 변경
        updater.dispatcher.add_handler(help_handler)

        help_handler = CommandHandler('yes', self.yes_command)
        updater.dispatcher.add_handler(help_handler)
        help_handler = CommandHandler('no', self.no_command)
        updater.dispatcher.add_handler(help_handler)

        help_handler = CommandHandler('tr_request', self.tr_command) #tr요청 한글 안 돼서 변경
        updater.dispatcher.add_handler(help_handler)

    def get_message(self, update, context):
        print("메세지 수신: %s" % update.message.text)
        print(context)

    # 쓰레딩으로 동작시킨 함수
    def check_msg(self, up_data):
        # start_polling으로 새로운 메시지가 있는지 체크하고 주기적으로 데이터들을 비워준다.
        up_data.start_polling(timeout=3, poll_interval=2, clean=True)

    # 내가 만든 명령어를 텔레그램에서 작성하면 여기서 수신된다.
    def help_command(self, update, context):
        txt = "/help 도움말\n\n" \
              "/종목매도_sell\n\n" \
              "/tr요청\n\n"
        update.message.reply_text(txt)

    def sell_command(self, update, context):
        self.sell_temp_gubun = "종목매도"
        update.message.reply_text("한 번 실행하면 되돌릴 수 없습니다. 실행하시겠습니까?\n/yes          /no")

    def yes_command(self, update, context):
        if self.sell_temp_gubun is not None:
            print("종목을 매도하는 로직을 추가")
            update.message.reply_text("종목을 매도하는 로직을 추가")
        self.sell_temp_gubun = None

    def no_command(self, update, context):
        self.sell_temp_gubun = None

    def tr_command(self, update, context):
        if self.tr_temp in None:
            self.tr_temp = "tr이름"
            threading.Timer(5.1, self.tr_req_chk).start()
        elif self.tr_temp is not None:
            update.message.reply_text("이전 tr요청의 시간제한이 안 지났습니다.")

    def tr_req_chk(self, update):
        self.tr_temp = None

if __name__=="__main__":
    Telegrams()