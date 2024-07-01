from pyrogram import Client, filters
from samaweb.samaweb_scrape import SamaGradeChecker
import asyncio

chat_ids = ["176198851", "652429947"]

def run_grade_checker():
    checker = SamaGradeChecker()
    checker.run()
    messages = checker.go_to_all_messages_page()
    return messages

async def send_messages_to_bot(client):
    messages = run_grade_checker()
    for chat_id in chat_ids:
        for msg in messages:
            if 'message_body' in msg:
                text = f"{msg['message_date']}\n{msg['message_body']}"
                await client.send_message(
                    chat_id=chat_id,
                    text=text
                )

async def periodic_grade_checker(client):
    while True:
        await send_messages_to_bot(client)
        await asyncio.sleep(300)  # Wait for 5 minutes

@Client.on_message(filters.command("start"))
async def start(client, message):
    await client.send_message(message.chat.id, "Seeking for new grade notifications, be patient mr.mar...")
    await send_messages_to_bot(client)
    asyncio.create_task(periodic_grade_checker(client))  # Start the periodic task

