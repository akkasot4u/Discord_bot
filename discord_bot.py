secret_token= "NzEwMDMyMzQ5MDgwODQ2NDE3.Xr1aCw._MmHOJUIFxL3MWqYFf2WHpmXBBs"

import discord
from googlesearch import search
import psycopg2

user = "postgres"
password = "test@123"
host = "127.0.0.1"
port = "5432"
database = "discord"

connection = None
try:
    connection = psycopg2.connect(user = user,
                                password = password,
                                host = host,
                                port = port,
                                database = database)
    cursor = connection.cursor()
except:
    print("database named discord does not exist, wait its Creating")
    connection = psycopg2.connect(user = user,
                                password = password,
                                host = host,
                                port = port,
                                database = "postgres")
    connection.autocommit = True
    cursor = connection.cursor()
    qry = '''CREATE database discord'''
    cursor.execute(qry)
    print("database with name discord created")


#Creating table as per requirement
cursor.execute('''CREATE TABLE IF NOT EXISTS user_history
    (user_name CHAR(200) NOT NULL, history CHAR(200))''')

# saving the search history of author inside database
def insert_data(user_name, search_string):
    insert_query = """INSERT INTO user_history (user_name, history) VALUES (%s,%s)"""
    record_to_insert = (user_name, search_string)
    cursor.execute(insert_query, record_to_insert)

# a function which will fetch the top 3 history data using the keyword
def fetch_history_data(user_name, search_string):
    QUERY = "select history from user_history where user_name =%s"
    cursor.execute(QUERY, (user_name,))
    records = cursor.fetchall()
    his = []
    for rec in records:
        if search_string in rec[0]:
            his.append(rec[0])
            if len(his) == 3:
                break
    return his

# a function which will get the top 5 links from google using the key word
def google_search(search_string):
    top_links = []
    result = search(query=search_string,tld='co.in',lang='en',num=5,stop=5,pause=2)
    for res in result:
        top_links.append(res)
    return top_links

client = discord.Client()

@client.event
async def on_ready():
    print("the bot," , client.user, " is ready to answer")  #bot is ready to give answers of author auery

@client.event
async def on_message(message):
    user_name = str(message.author)
    if message.author == client.user: 
        return  #stopping when the bot itself sending message

    if message.content == "Hi":
        await message.channel.send("Hey") #responding Hey of hi

    if "!google " in message.content:
        search_string = " ".join(message.content.split()[1:]) 
        links = google_search(search_string) #top 5 links which got from google
        for i, link in enumerate(links):
            await message.channel.send("%d: %s" % (i+1, link)) #returning top 5 links with respect to this keyword
        insert_data(user_name, search_string) #storing this search with respect to the user in database
        connection.commit()

    if "!recent " in message.content:
        search_string = " ".join(message.content.split()[1:])
        history_records = fetch_history_data(user_name, search_string)
        if not history_records:
            await message.channel.send("no recent searches found from you with this key word") #if no history found from this user then return this
        for i, his in enumerate(history_records):
            await message.channel.send("%d: %s" % (i+1, his)) #returning history searches of the user

client.run(secret_token)