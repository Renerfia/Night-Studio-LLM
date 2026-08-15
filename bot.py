import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from database.sql import init_db,guild_verification
from cogs.ai_chat import get_response,generate_search_query
from vector_database.vector_db import add_text_to_chromadb, retrieve_memory


load_dotenv()
init_db()

BOT_TOKEN = os.getenv("BOT_TOKEN")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)
bot.load_extension("cogs.commands")
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')

@bot.event
async def on_thread_create(thread):
    if thread.parent.type == discord.ChannelType.forum:
        print(f"New forum post has been found: {thread.name}")

        guild_id = thread.guild.id

        verfication = guild_verification(guild_id=guild_id)

        if verfication == True:
            print("The channel is verified")
        else:
            print("The channel isn't verified")

        try:
            print("Getting the starter message")
            starter_message = await thread.fetch_message(thread.id)
            content = starter_message.content.strip() if starter_message.content else "[No text content provided]"

            print("Making the full query")
            full_query = f"Title: {thread.name}\nContent: {content}"

            print("Vector searching")
            vector_search_query = await generate_search_query(full_query) 

            memories = retrieve_memory(vector_search_query)

            if memories:
                print("Found relevent memories")

            print("Getting response")
            response = await get_response(query=full_query,memories=memories)

            await thread.send(response)
        except Exception as e:
            print(f"An error occured:{e}")

@bot.event
async def on_application_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.respond("You don't have permission to do that.", ephemeral=True)
    elif isinstance(error, discord.Forbidden):
        await ctx.respond("I don't have permission to do that.", ephemeral=True)
    else:
        await ctx.respond("Something went wrong.", ephemeral=True)
        print(f"Unhandled error: {error}")
    

bot.run(BOT_TOKEN)