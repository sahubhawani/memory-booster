from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import psycopg2
import os
from datetime import date, timedelta, datetime, time


# Heroku cloud server parameter
TOKEN = os.environ.get('TOKEN')
PORT = os.environ.get('PORT', 5000)

# Heroku Database Parameters
heroku_host = os.environ.get('HOST')
heroku_database = os.environ.get('DATABASE')
heroku_user = os.environ.get('USER')
heroku_password = os.environ.get('PASSWORD')
heroku_port = int(os.environ.get('DATABASE_PORT'))


# Staring the Database
conn = psycopg2.connect(dbname=heroku_database, user=heroku_user, password=heroku_password, host=heroku_host,
                        port=heroku_port)  #

remind_period0 = timedelta(days=0)
remind_period3 = timedelta(days=3)
remind_period7 = timedelta(days=7)
remind_period21 = timedelta(days=21)


def delete_from_db(topic_date_str):
    topic_date = datetime.strptime(topic_date_str, "%Y/%m/%d")
    with conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM topiclist WHERE topicdate = %s ", (topic_date,))


def write_to_db(update, context: CallbackContext):  #
    chat_id = update.message.chat_id
    message = update.message.text  #
    try:
        first_str = message.split(",")[0]
        topic = message.split(",")[1].strip()
        if first_str == "del":
            topic_date_str = message.split(",")[1].strip()
            delete_from_db(topic_date_str)
            context.bot.send_message(chat_id=chat_id, text="Entries for the given date is deleted from the Database")
        else:
            topic_date = datetime.strptime(first_str, "%Y/%m/%d")
            topic = message.split(",")[1].strip()
    except:
        topic = message.strip()
        topic_date = date.today()
    with conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO topiclist (topicdate,topic) VALUES(%s,%s)", (topic_date, topic))
    context.bot.send_message(chat_id=chat_id, text="Thanks, this topic is added to the Database")


def remind(update, context: CallbackContext):
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id=chat_id, text="Revise the below topics tomorrow:")
    with conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM topiclist")
            data = cur.fetchall()

    for i in range(len(data)):
        topic_date = data[i][0]
        if date.today() - topic_date == remind_period0 or date.today() - topic_date == remind_period3 or date.today() - topic_date == remind_period7 or date.today() - topic_date == remind_period21:
            topic = "[" + str(topic_date) + "] " + data[i][1]
            context.bot.send_message(chat_id=chat_id, text=topic)


def auto_remind(context: CallbackContext):
    chat_id = "-1001248983748"
    context.bot.send_message(chat_id=chat_id, text="Revise the below topics tomorrow:")
    with conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM topiclist")
            data = cur.fetchall()

    for i in range(len(data)):
        topic_date = data[i][0]
        if date.today() - topic_date == remind_period0 or date.today() - topic_date == remind_period3 or date.today() - topic_date == remind_period7 or date.today() - topic_date == remind_period21:
            topic = "[" + str(topic_date) + "] " + data[i][1]
            context.bot.send_message(chat_id=chat_id, text=topic)


def show_all(update, context: CallbackContext):
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id=chat_id, text="Here is the list of all the topics in the Database:")
    with conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM topiclist")
            data = cur.fetchall()

    for i in range(len(data)):
        topic_date = data[i][0]
        topic = "[" + str(topic_date) + "] " + data[i][1]
        context.bot.send_message(chat_id=chat_id, text=topic)


def start(update, context: CallbackContext):
    chat_id = update.message.chat_id
    title = update.message.from_user["first_name"]
    context.bot.send_message(chat_id=chat_id,
                             text="Hi " + str(title) + ", i am glad to see you using this bot.")


def main():
    updater = Updater(TOKEN, use_context=True)
    job_queue = updater.job_queue
    dp = updater.dispatcher
    job_queue.run_daily(auto_remind, time(hour=9, minute=35, second=00))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, write_to_db))
    dp.add_handler(CommandHandler("remind", remind))
    dp.add_handler(CommandHandler("show_all", show_all))
    dp.add_handler(CommandHandler("start", start))
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    updater.bot.setWebhook('https://memory-booster.herokuapp.com/' + TOKEN)
    updater.idle()


if __name__ == '__main__':
    main()
conn.close()
