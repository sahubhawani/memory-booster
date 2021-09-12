from telegram import Update
from telegram.ext import Updater, inlinequeryhandler, CommandHandler, MessageHandler, Filters
import psycopg2
import os
from datetime import date, timedelta, datetime

TOKEN = '1900223742:AAHSr57ONPwcqIFKSDvkBjLmmcJ1V9kZOz4'
PORT = int(os.environ.get('PORT', 5000))

# Database Parameters
heroku_host = "ec2-44-198-100-81.compute-1.amazonaws.com"
heroku_database = "dfo0b73e3hacft"
heroku_user = "uzjxpfwpahqcxd"
heroku_password = "6403155428aee5767a9d03d9a2aa2d4753e4b903f656a45cf7383f7bcf507c8b"
heroku_port = 5432
# Staring the Database
conn = psycopg2.connect(dbname=heroku_database, user=heroku_user, password=heroku_password, host=heroku_host,
                        port=heroku_port)

remind_period0 = timedelta(days=0)
remind_period3 = timedelta(days=3)
remind_period7 = timedelta(days=7)
remind_period21 = timedelta(days=21)


def delete_from_db():
    pass


def write_to_db(bot, update):  #
    message = update.message.text  #
    try:
        first_str = message.split(",")[0]
        topic = message.split(",")[1].strip()
        if first_str == "del":
            delete_from_db()
        else:
            topic_date = datetime.strptime(first_str, "%Y/%m/%d")
    except:
        topic = message.strip()
        topic_date = date.today()
    with conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO topiclist (topicdate,topic) VALUES(%s,%s)", (topic_date, topic))


def remind(bot, update):
    chat_id = update.message.chat_id
    bot.send_message(chat_id=chat_id, text="Revise the below topics today:")
    with conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM topiclist")
            data = cur.fetchall()

    for i in range(len(data)):
        topic_date = data[i][0]
        if date.today() - topic_date == remind_period0 or date.today() - topic_date == remind_period3 or date.today() - topic_date == remind_period7 or date.today() - topic_date == remind_period21:
            topic = "[" + str(topic_date) + "] " + data[i][1]
            bot.send_message(chat_id=chat_id, text=topic)


def start(bot, update):
    chat_id = update.message.chat_id
    title = update.message.from_user["first_name"]
    bot.send_message(chat_id=chat_id,
                     text="Hi " + str(title) + " welcome to this Bot. I am feeling great to see you here.")


def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, write_to_db))
    dp.add_handler(CommandHandler("remind", remind))
    dp.add_handler(CommandHandler("start", start))
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    updater.bot.setWebhook('https://memory-booster.herokuapp.com/' + TOKEN)
    updater.idle()


if __name__ == '__main__':
    main()
conn.close()
