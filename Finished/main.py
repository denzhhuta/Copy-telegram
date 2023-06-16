import aiogram
import asyncio
from aiogram import types, Bot, Dispatcher, executor, filters
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.handler import CancelHandler
from aiogram.types import Update
from aiogram.types.chat_member import ChatMemberMember, ChatMemberOwner, ChatMemberAdministrator
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import CallbackQuery
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from typing import List, Union
from aiogram_media_group import media_group_handler
from aiogram.utils import deep_linking
from aiogram.utils.exceptions import (MessageToEditNotFound, MessageCantBeEdited, MessageCantBeDeleted, MessageToDeleteNotFound, CantRestrictChatOwner)
import logging
import contextlib
from contextlib import suppress
import re

class CheckSubscriptionUserMiddleware(BaseMiddleware):
    def __init__(self):
         self.prefix = 'key_prefix'
         super(CheckSubscriptionUserMiddleware, self).__init__()
         
    async def on_process_update(self, update: types.Update, data: dict):
        if "message" in update:
            this_user = update.message.from_user
            if update.message.text:
                if "start" in update.message.text:
                    return
    
        elif "callback_query" in update:
            this_user = update.callback_query.from_user
        
        else:
            this_user = None
        
        if this_user is not None:
            get_prefix = self.prefix
                     
            if not this_user.is_bot:                       
                user_id = this_user.id
                if this_user.username != "morkovka2005" or this_user.username != "andrey_pracja" or this_user.username != "auditoreold":
                    await bot.send_message(user_id, 
                               "<b>😔 You are not allowed to use this bot!</b>", 
                               parse_mode="HTML")
                    
                    raise CancelHandler()     
                

TOKEN_API = "6064195503:AAHdQeQ6LA4T2BPoDTBozkOucEIwCTcliQo"
CHANNEL_ID = -1001619748024
            
processed_messages = set()

loop = asyncio.get_event_loop()
storage = MemoryStorage()
bot = aiogram.Bot(TOKEN_API)
dp = aiogram.Dispatcher(bot, storage=storage)
#function to parse caption
async def format_text_with_entities(text, entities, as_html=True):
    if text is None:
        raise TypeError("Text is None.")

    parse_mode = "HTML" if as_html else "Markdown"
    formatted_text = text

    # Create a message object to access the parse_entities method
    message = types.Message(text=text, entities=entities)
    if as_html:
        formatted_text = message.parse_entities(as_html=True)

    return formatted_text
        
async def delete_message(message: types.Message, sleep_time: int = 0):
    await asyncio.sleep(sleep_time)
    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await message.delete()
        

@dp.message_handler(filters.MediaGroupFilter(is_media_group=True), content_types=types.ContentTypes.ANY)
@media_group_handler
async def album_handler(messages: List[types.Message]):
    for message in messages:
        buttons_row1 = [
        aiogram.types.InlineKeyboardButton("Edit", callback_data=f"edit:{message.message_id}"),
        aiogram.types.InlineKeyboardButton("Delete", callback_data=f"delete:{message.message_id}"),
        aiogram.types.InlineKeyboardButton("Forward", callback_data=f"forward:{message.message_id}")
        ]   

        buttons_row2 = [
        aiogram.types.InlineKeyboardButton("Change photo", callback_data=f"add_photo:{message.message_id}"),
        aiogram.types.InlineKeyboardButton("Remove Photo", callback_data=f"remove_photo:{message.message_id}")
        ]

        keyboard = aiogram.types.InlineKeyboardMarkup().row(*buttons_row1).row(*buttons_row2)
        
        if message.caption:
            formatted_caption = await format_text_with_entities(message.caption, message.caption_entities, as_html=True)
        else:
            caption = ''
        
        await bot.send_photo(
            chat_id=message.from_user.id,
            photo=message.photo[-1].file_id,
            caption=formatted_caption,
            caption_entities=message.caption_entities,
            reply_markup=keyboard,
            parse_mode="HTML"
        )

               
@dp.message_handler(filters.MediaGroupFilter(is_media_group=False), content_types=types.ContentTypes.ANY)
async def process_forwarded_message(message: types.Message, state: FSMContext):
    processed_messages.add(message.message_id)
    
    buttons_row1 = [
        aiogram.types.InlineKeyboardButton("Edit", callback_data=f"edit:{message.message_id}"),
        aiogram.types.InlineKeyboardButton("Delete", callback_data=f"delete:{message.message_id}"),
        aiogram.types.InlineKeyboardButton("Forward", callback_data=f"forward:{message.message_id}")
    ]

    buttons_row2 = [
        aiogram.types.InlineKeyboardButton("Change photo", callback_data=f"add_photo:{message.message_id}"),
        aiogram.types.InlineKeyboardButton("Remove Photo", callback_data=f"remove_photo:{message.message_id}")
    ]

    keyboard = aiogram.types.InlineKeyboardMarkup().row(*buttons_row1).row(*buttons_row2)

    
    #So that bot will not resend messaged, which are send by me into my group, etc.
    if message.chat.type != "private":
         return 
    
    if message.caption:
        formatted_caption = await format_text_with_entities(message.caption, message.caption_entities, as_html=True)
    else:
        caption = ''
    
    if message.photo:
        await bot.send_photo(chat_id=message.from_user.id,
                             photo=message.photo[-1].file_id,
                             caption=formatted_caption,
                             reply_markup=keyboard,
                             parse_mode="HTML")
        
    elif message.document:
        await bot.send_document(chat_id=message.from_user.id,
                                document=message.document.file_id,
                                caption=formatted_caption,
                                reply_markup=keyboard,
                                parse_mode="HTML")
    elif message.video:
        await bot.send_video(chat_id=message.from_user.id,
                             video=message.video.file_id,
                             caption=formatted_caption,
                             reply_markup=keyboard,
                             parse_mode="HTML")
    elif message.audio:
        await bot.send_audio(chat_id=message.from_user.id,
                             audio=message.audio.file_id,
                             caption=formatted_caption,
                             reply_markup=keyboard,
                             parse_mode="HTML")
    elif message.animation:
        await bot.send_animation(chat_id=message.from_user.id,
                                 animation=message.animation.file_id,
                                 caption=formatted_caption,
                                 reply_markup=keyboard,
                                 parse_mode="HTML")
    elif message.sticker:
        await bot.send_sticker(chat_id=message.from_user.id,
                               sticker=message.sticker.file_id,
                               reply_markup=keyboard,
                               parse_mode="HTML")
    elif message.voice:
        await bot.send_voice(chat_id=message.from_user.id,
                             voice=message.voice.file_id,
                             caption=formatted_caption,
                             reply_markup=keyboard,
                             parse_mode="HTML")
    elif message.video_note:
        await bot.send_video_note(chat_id=message.from_user.id,
                                  video_note=message.video_note.file_id,
                                  reply_markup=keyboard,
                                  parse_mode="HTML")
    else:
        await bot.send_message(chat_id=message.from_user.id,
                               text=message.html_text,
                               reply_markup=keyboard,
                               parse_mode="HTML")
                               
################################################################################################
################################################################################################
################################################################################################

@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('delete:'))
async def delete_callback_handler(callback: types.CallbackQuery, state: FSMContext):
    try:
        message_id = int(callback.data.split(':')[1])
        
        print(f"{message_id} - DELETE")

        # Delete the bot's message
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
        
        # Delete the user's message if it exists
        with contextlib.suppress(
            aiogram.utils.exceptions.MessageCantBeDeleted,
            aiogram.utils.exceptions.MessageToDeleteNotFound
        ):
            await bot.delete_message(chat_id=callback.message.chat.id, message_id=message_id)
        
    except Exception as ex:
        await bot.send_message(chat_id=callback.message.chat.id, text=f"Error while deleting the message: {ex}")

        
################################################################################################
################################################################################################
################################################################################################

@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('forward:'))
async def forward_callback_handler(callback: types.CallbackQuery):
    try:
        message_id = int(callback.data.split(':')[1])
        
        await bot.copy_message(chat_id=CHANNEL_ID, 
                                from_chat_id=callback.message.chat.id, 
                                message_id=callback.message.message_id)
        
    #    await bot.forward_message(chat_id=CHANNEL_ID, 
    #                               from_chat_id=callback.message.chat.id, 
    #                               message_id=callback.message.me ssage_id)
    
    except Exception as ex:
        await bot.send_message(chat_id=callback.message.chat.id, text=f"Error while forwarding the message. {ex}")

@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('edit:'))
async def edit_callback_handler(callback: types.CallbackQuery, state: FSMContext):
    try:
        message_id_forwarded = callback.message.message_id
        message_complete_forwarded = callback.message
        message_id = int(callback.data.split(':')[1])

        
        await state.update_data(message_id_forwarded=message_id_forwarded)
        await state.update_data(message_complete_forwarded=message_complete_forwarded)
        await state.update_data(message_id=message_id)
        
        await bot.send_message(chat_id=callback.message.chat.id,
                       text='Enter the new text for your post! (/cancel - to undo cancellation)')

        
        await state.set_state("edit_complete")
 
    except Exception as ex:
        await bot.send_message(chat_id=callback.message.chat.id, text=f"Error while editing the message. {ex}")
        
################################################################################################
################################################################################################
################################################################################################

@dp.message_handler(state='edit_complete')
async def edit_complete_handler(message: types.Message, state: FSMContext) -> types.Message:
        edit_message = message.text
        #cancel state
        if str(edit_message) == '/cancel':
            await bot.send_message(chat_id=message.from_user.id,
                                   text="<b>Operation has been cancelled!</b>",
                                   parse_mode="HTML")
            await state.reset_state()
            return

        async with state.proxy() as data:
            message_id_forwarded = data.get('message_id_forwarded')
            message_complete_forwarded = data.get('message_complete_forwarded')
            message_id = data.get('message_id')
            
        #type = message_id_forwarded.content_type
        print(f"{message_id} - EDITION")
        buttons_row1 = [
            types.InlineKeyboardButton("Edit", callback_data=f"edit:{message_id_forwarded}"),
            types.InlineKeyboardButton("Delete", callback_data=f"delete:{message_id}"),
            types.InlineKeyboardButton("Forward", callback_data=f"forward:{message_id_forwarded}")
        ]
        
        buttons_row2 = [
        aiogram.types.InlineKeyboardButton("Add Photo", callback_data=f"add_photo:{message_id_forwarded}"),
        aiogram.types.InlineKeyboardButton("Remove Photo", callback_data=f"remove_photo:{message_id_forwarded}")
        ]
        
        keyboard = aiogram.types.InlineKeyboardMarkup().row(*buttons_row1).row(*buttons_row2)

        if message_complete_forwarded.photo:
            if edit_message.strip():      
            
                await bot.edit_message_caption(chat_id=message.chat.id,
                                            message_id=message_id_forwarded,
                                            caption=edit_message,
                                            parse_mode="HTML",
                                            reply_markup=keyboard)

                await state.reset_state()
        
        elif message_complete_forwarded.document:
            if edit_message.strip():
                
                  await bot.edit_message_caption(chat_id=message.chat.id,
                                            message_id=message_id_forwarded,
                                            caption=edit_message,
                                            parse_mode="HTML",
                                            reply_markup=keyboard)
                  
                  await state.reset_state()


        elif message_complete_forwarded.video:
            if edit_message.strip():      
                
                 await bot.edit_message_caption(chat_id=message.chat.id,
                                            message_id=message_id_forwarded,
                                            caption=edit_message,
                                            parse_mode="HTML",
                                            reply_markup=keyboard)
                  
                 await state.reset_state()

        
        elif message_complete_forwarded.audio:
            if edit_message.strip():      
                
                 await bot.edit_message_caption(chat_id=message.chat.id,
                                            message_id=message_id_forwarded,
                                            caption=edit_message,
                                            parse_mode="HTML",
                                            reply_markup=keyboard)
                  
                 await state.reset_state()

        
        elif message.video_note:
             if edit_message.strip():      
                
                 await bot.edit_message_caption(chat_id=message.chat.id,
                                            message_id=message_id_forwarded,
                                            caption=edit_message,
                                            parse_mode="HTML",
                                            reply_markup=keyboard)
                  
                 await state.reset_state()
   
        else:
            if edit_message.strip():   
                await bot.edit_message_text(chat_id=message.chat.id, message_id=message_id_forwarded, text=edit_message,
                                    reply_markup=keyboard)
            
            await state.reset_state()


        await bot.send_message(chat_id=message.from_user.id,
                               text="<b>Message edited successfully!</b>",
                               parse_mode="HTML")

        await state.reset_state()


################################################################################################
################################################################################################
################################################################################################
      
@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('add_photo:'))
async def addPhoto_callback_handler(callback: types.CallbackQuery, state: FSMContext):
    try:
        message_id = int(callback.data.split(':')[1])
        message_id_forwarded = callback.message.message_id
        message_complete_forwarded = callback.message
        
        await state.update_data(message_id_forwarded=message_id_forwarded)
        await state.update_data(message_complete_forwarded=message_complete_forwarded)
        await state.update_data(message_id=message_id)
        
        await bot.send_message(chat_id=callback.message.chat.id,
                       text='Add your media! (/cancel - to undo cancellation)')

        
        await state.set_state("addMedia_complete")
 
    except Exception as ex:
        await bot.send_message(chat_id=callback.message.chat.id, text=f"Error while editing the message. {ex}")
    

@dp.message_handler(state='addMedia_complete', content_types=types.ContentTypes.ANY)
async def add_media_complete_handler(message: types.Message, state: FSMContext):
    try:
        
        async with state.proxy() as data:
            message_id_forwarded = data.get('message_id_forwarded')
            message_complete_forwarded = data.get('message_complete_forwarded')
            message_id = data.get('message_id')
            
        print(f"{message_id} - PHOTO ADD")


        buttons_row1 = [
            types.InlineKeyboardButton("Edit", callback_data=f"edit:{message_id_forwarded}"),
            types.InlineKeyboardButton("Delete", callback_data=f"delete:{message_id}"),
            types.InlineKeyboardButton("Forward", callback_data=f"forward:{message_id_forwarded}")
        ]

        buttons_row2 = [
            types.InlineKeyboardButton("Add Photo", callback_data=f"add_photo:{message_id_forwarded}"),
            types.InlineKeyboardButton("Remove Photo", callback_data=f"remove_photo:{message_id_forwarded}")
        ]

        keyboard = types.InlineKeyboardMarkup().row(*buttons_row1).row(*buttons_row2)
        
        if message.photo:
            is_media = message.photo[-1].file_id

            if is_media:
                caption_check = message_complete_forwarded.caption if message_complete_forwarded and message_complete_forwarded.caption else ''
                # Add the following lines to check if the message has a caption or just text
                if 'caption' in message_complete_forwarded and message_complete_forwarded.caption:
                    caption_check = message_complete_forwarded.caption
                elif 'text' in message_complete_forwarded and message_complete_forwarded.text:
                    caption_check = message_complete_forwarded.text

                if message_complete_forwarded and message_complete_forwarded.photo:       
                    await bot.edit_message_media(
                        chat_id=message.chat.id,
                        message_id=message_id_forwarded,
                        media=types.InputMediaPhoto(media=is_media),
                        reply_markup=keyboard
                    )
                    
                    await bot.edit_message_caption(
                        chat_id=message.chat.id,
                        message_id=message_id_forwarded,
                        caption=caption_check,
                        reply_markup=keyboard
                    )
                    
                    await state.reset_state()
                
                else:
                    await bot.send_photo(
                        chat_id=message.chat.id,
                        photo=is_media,
                        reply_markup=keyboard,
                        caption=caption_check
                    )
                    
                    await state.reset_state()


            
        elif message.video:
            is_media = message.video.file_id

            if is_media:
                if message_complete_forwarded:
                    if message_complete_forwarded.caption:
                        caption = message_complete_forwarded.caption
                    else:
                        caption = ''

                if message_complete_forwarded.video or message_complete_forwarded.photo:
                    await bot.edit_message_media(
                        chat_id=message.chat.id,
                        message_id=message_id_forwarded,
                        media=types.InputMediaVideo(media=is_media),
                        reply_markup=keyboard
                    )

                    await bot.edit_message_caption(
                        chat_id=message.chat.id,
                        message_id=message_id_forwarded,
                        caption=caption,
                        reply_markup=keyboard
                    )

                    await state.reset_state()
                else:
                    await bot.send_video(
                        chat_id=message.chat.id,
                        video=is_media,
                        caption=caption,
                        reply_markup=keyboard
                    )

                    await state.reset_state()
                             
        else:
            pass
            await state.reset_state()
            await bot.send_message(chat_id=message.chat.id,
                                   text="Should be photo or video!")

        
    except Exception as ex:
        
        await bot.send_message(chat_id=message.chat.id, text=f"Error while editing the message. {ex}")
        await state.reset_state()


@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('remove_photo:'))
async def delete_media_callback_handler(callback: types.CallbackQuery, state: FSMContext):
    try:
        message_id = int(callback.data.split(':')[1])
        
        # Delete the media content of the message
        await bot.send_message(chat_id=callback.message.chat.id,
                               text="сори низя")
        
        await state.reset_state()
        
    except Exception as ex:
        await bot.send_message(chat_id=callback.message.chat.id, text=f"Error while deleting the message media. {ex}")
        await state.reset_state()


    # if message.photo:
    #     # Get the existing photo
    #     existing_photo = types.InputMediaPhoto(media=message_complete_forwarded.photo[-1].file_id, caption='Existing Photo')

    #     # Get the new photo
    #     new_photo = types.InputMediaPhoto(media=message.photo[-1].file_id, caption='New Photo')

    #     # Create a media group with both photos
    #     media_group = types.MediaGroup()
    #     media_group.attach_photo(existing_photo)
    #     media_group.attach_photo(new_photo)

    #     await bot.send_media_group(
    #         chat_id=message.chat.id,
    #         media=media_group,
    #         reply_markup = keyboard
    #     )

    # elif message.video:
    #     # Handle video case separately if needed
    #     pass

    #await state.reset_state()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)