import telegram
import psycopg2
import os
from datetime import date, timedelta

# Heroku cloud server parameter
TOKEN = os.environ.get('TOKEN')
PORT = os.environ.get('PORT', 5000)

# Heroku Database Parameters
heroku_host = os.environ.get('HOST')
heroku_database = os.environ.get('DATABASE')
heroku_user = os.environ.get('USER')
heroku_password = os.environ.get('PASSWORD')
heroku_port = int(os.environ.get('DATABASE_PORT'))

# Starting the bot
bot = telegram.Bot(TOKEN)

# Staring the Database
conn = psycopg2.connect(dbname=heroku_database, user=heroku_user, password=heroku_password, host=heroku_host,
                        port=heroku_port)

remind_period0 = timedelta(days=0)
remind_period3 = timedelta(days=3)
remind_period7 = timedelta(days=7)
remind_period21 = timedelta(days=21)


def auto_remind(bot):
    chat_id = "-1001248983748"
    bot.send_message(chat_id=chat_id, text="Good Morning Guys")
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


auto_remind(bot)

