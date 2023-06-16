from telethon import TelegramClient, events
import asyncio
import aiogram
import aiomysql

Id_bot = "@copycatpetrov_bot"
Id_Group2 = -1001566683552 #Робота Київ Вакансії
Id_Group3 = -1001523296762 #Работа Харьков | Вакансии Харьков | Подработка Харьков
Id_Group4 = -1001699952723 #Рекрутер: Вакансії
Id_Group5 = -1001958888111 #Работа 🇺🇦Харьков🇺🇦Украина
Id_Group6 = -1001877562692 #Вакансич
Id_Group7 = -1001911782118 #Харків Робота
Id_Group8 = -1001193192927 #Работа в Херсоне | Робота в Херсоні
Id_Group9 = -1001463094722 #Робота у Львові Львів
Id_Group10 = -1001289513843 #Работа в Харькове
Id_Group11 = -1001717717040 #Харків Робота
Id_Group12 = -1001431016100 #Херсон Робота
Id_Group13 = -1001493265625 #Робота Київ Вакансії
Id_Group14 = -1001453728910 #Робота | Вінниця (Работа Винница)

api_id = '24607193'
api_hash = '75e0b0af6c73a423bb12bc1ee0e9c14c'

chats_to_listen_to = [Id_Group2, Id_Group3, Id_Group4, Id_Group5, Id_Group6, Id_Group7, Id_Group8, Id_Group9, Id_Group10, Id_Group11, Id_Group12, Id_Group13, Id_Group14]

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