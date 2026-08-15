from discord.ext import commands
import discord
from database.sql import set_the_forum_channel_to_db, guild_verification, get_forum_channel
from cogs.ai_chat import get_summerization
from vector_database.vector_db import add_text_to_chromadb
import asyncio

class CommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="set_up_forum", description="Set your existing thread wherer the LLM will read threads")
    @commands.has_permissions(administrator=True)
    async def set_up_thread(self, ctx, forum_channel: discord.ForumChannel):
        # Store the thread channel ID in the bot's state or database
        set_the_forum_channel_to_db(ctx.guild.id, forum_channel.id)
        await ctx.respond(f"Forum channel set to: {forum_channel.name}")

    @discord.slash_command(name="scan_forum",description="It scans the forum for resolved answers and save them in database")
    @commands.has_permissions(administrator=True)
    async def scan_forum(self, ctx: discord.ApplicationContext):
        print("Scan command is called")
        # 1. Defer interaction to give the bot time to process
        await ctx.defer()
        guild_id = ctx.guild_id

        # 2. Check Verification
        if not guild_verification(guild_id=guild_id) == True:
            return await ctx.followup.send(
                "❌ This server does not have an active AI connected forum channel.",
                ephemeral=True,
            )

        print("The server has AI connected forum channel.")

        # 3. Get Forum Channel ID
        forum_channel_id = get_forum_channel(guild_id=guild_id)
        if not forum_channel_id:
            return await ctx.followup.send(
                "❌ No forum channel found in the database for this server.",
                ephemeral=True,
            )

        # 4. Fetch Channel via API safely (Fixes get_channel error)
        try:
            forum = await self.bot.fetch_channel(forum_channel_id)
        except (discord.NotFound, discord.Forbidden):
            return await ctx.followup.send(
                "❌ Unable to access the configured forum channel.",
                ephemeral=True,
            )

        if not isinstance(forum, discord.ForumChannel):
            return await ctx.followup.send(
                "❌ Configured channel is not a Forum Channel.", ephemeral=True
            )

        print(f"Forum channel '{forum.name}' has been found.")

        # 5. Collect Active and Archived Threads
        all_threads = list(forum.threads)

        async for thread in forum.archived_threads(limit=None):
            print(f"Getting archived thread: {thread.name}")
            all_threads.append(thread)

        print(f"Total threads found: {len(all_threads)}")

        # 6. Process Messages
        for i, thread in enumerate(all_threads, start=1):
            messages = []
            async for message in thread.history(limit=None, oldest_first=True):
                if message.content:  # Skip empty system/attachment messages
                    messages.append(message.content)

            if not messages:
                continue

            print(
                f"[{i}/{len(all_threads)}] Thread '{thread.name}': Collected {len(messages)} messages"
            )

            # Join messages into a single text block for the LLM
            full_text = "\n".join(messages)
            print(f"The post's message block is:\n{full_text}")
            summarization = await get_summerization(full_text)

            print(f"Adding thread {thread.id} to ChromaDB")
            add_text_to_chromadb(str(thread.id), summarization)

            # Small delay to respect Discord API rate limits
            await asyncio.sleep(0.3)

        # 7. Final Completion Message
        await ctx.followup.send("✅ Forum scanning complete!", ephemeral=True)
                



            

        
def setup(bot):
    bot.add_cog(CommandsCog(bot))