import asyncio
import discord
from dotenv import load_dotenv
load_dotenv()
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
SOURCE_FORUM_ID = 1400865136373403708  # Channel ID to copy FROM
TARGET_FORUM_ID = 1536781065107279932  # Your test forum channel ID (copy TO)
MAX_THREADS_TO_COPY = 20  # Limit to prevent rate limits

intents = discord.Intents.default()
intents.message_content = True  # Required to read starter message text
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

    source_forum = client.get_channel(SOURCE_FORUM_ID)
    target_forum = client.get_channel(TARGET_FORUM_ID)

    if not source_forum or not target_forum:
        print("Error: Could not find one or both forum channels.")
        await client.close()
        return

    print(f"Copying posts from #{source_forum.name} -> #{target_forum.name}\n")

    # 1. Collect threads (active threads)
    threads_to_copy = list(source_forum.threads)

    # 2. Also fetch archived threads if active list is small
    if len(threads_to_copy) < MAX_THREADS_TO_COPY:
        async for archived_thread in source_forum.archived_threads(
            limit=MAX_THREADS_TO_COPY - len(threads_to_copy)
        ):
            threads_to_copy.append(archived_thread)

    print(f"Found {len(threads_to_copy)} threads to clone.\n")

    # 3. Clone each thread into the target forum
    for i, thread in enumerate(threads_to_copy, start=1):
        try:
            # Fetch the original starter message
            starter_msg = await thread.fetch_message(thread.id)
            content = (
                starter_msg.content.strip()
                if starter_msg.content
                else "[Original post had no text body]"
            )

            # Discord API character limits check
            if len(content) > 2000:
                content = content[:1990] + "..."

            # Create the thread in your test forum
            await target_forum.create_thread(name=thread.name, content=content)
            print(f"[{i}/{len(threads_to_copy)}] Cloned: {thread.name}")

            # Sleep 2.5s between thread creations to avoid Discord API 429 Rate Limits
            await asyncio.sleep(2.5)

        except Exception as e:
            print(f"Skipped '{thread.name}': {e}")

    print("\n✅ Forum cloning complete!")
    await client.close()


client.run(BOT_TOKEN)