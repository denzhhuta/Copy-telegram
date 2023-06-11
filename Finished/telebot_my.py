from telethon import TelegramClient, events
import asyncio
import aiogram
import aiomysql

Id_bot = "@copycatpetrov_bot"
Id_Group2 = -1001461377874
Id_Group3 = -1001198589840
Id_Group4 = -1001279746025
Id_Group5 = -1001401696309
Id_Group6 = -1001210791591
Id_Group7 = -1001837710886
api_id = '24607193'
api_hash = '75e0b0af6c73a423bb12bc1ee0e9c14c'

chats_to_listen_to = [Id_Group2, Id_Group3, Id_Group4, Id_Group5, Id_Group6, Id_Group7]

client = TelegramClient('none2', api_id, api_hash)

@client.on(events.NewMessage(chats=chats_to_listen_to))
async def new_message_handler(event):
    if event.sender_id == Id_bot:
        return
    
    if event.grouped_id:
        return    # ignore messages that are gallery here
    
    await client.send_message(Id_bot, event.message)

@client.on(events.Album(chats=chats_to_listen_to))
async def album_handler(event):
    await event.forward_to(Id_bot, messages=event.messages)
    
client.start()
client.run_until_disconnected()

#6064195503:AAHL9SrKGWqdynJUqqIn04o9dJF8p4-nWVM