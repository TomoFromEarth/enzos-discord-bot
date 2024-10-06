import asyncio
import configparser
import logging
from mcstatus import BedrockServer
from discord.ext import commands
import discord
import os

# Configure logging
logging.basicConfig(
    filename="bot.log", 
    level=logging.INFO, 
    format="%(asctime)s:%(levelname)s:%(message)s"
)

# Load configuration
config = configparser.ConfigParser()
config.read("config.ini")

# Get the Discord bot token from an environment variable
TOKEN = os.environ.get("DISCORD_TOKEN")

# Get Minecraft server details from config.ini or environment variables
MC_SERVER_IP = config.get("Minecraft", "server_ip", fallback=os.environ.get("MC_SERVER_IP"))
MC_SERVER_PORT = config.getint("Minecraft","server_port", fallback=os.environ.get("MC_SERVER_PORT"))

# Check if TOKEN is available
if not TOKEN:
    logging.error("Discord bot token not found.  Please set the DISCORD_TOKEN environment variable.")
    raise ValueError("Discord bot token not found. Please set the DISCORD_TOKEN environment variable.")

# Check if Minecraft server IP nad port are available
if not MC_SERVER_IP or not MC_SERVER_PORT:
    logging.error("Minecraft server IP or port not found.  Please set them in config.ini or as environment variables.")
    raise ValueError("Minecraft server IP or port not found.  Please set them in config.ini or as environment variables.")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Fetch Minecraft server status
async def fetch_mc_status():
    try:
        server = BedrockServer.lookup(f"{MC_SERVER_IP}:{MC_SERVER_PORT}")
        status = await server.async_status()

        response = (
            f"**Voici les moyens de connexion pour ce au serveur**\n\n"
            f"**IP**: `{MC_SERVER_IP}`\n"
            f"**Port**: `{MC_SERVER_PORT}`\n"
            f"**Joueurs en ligne**: `{status.players.online}/{status.players.max}`\n"
        )
        return response
    except Exception as e:
        logging.error(f"Erreur de récupération de l'état du serveur: {e}", exc_info=True)
        return f"A échoué à récupérer l'état du serveur:\n```{e}```"
    
@bot.command()
async def mcstatus(ctx):
    response, status = await fetch_mc_status()

    if status is not None:
        # Create an embed to dispolay the server status more attractively
        embed = discord.Embed(
            title="Voici les moyens de connexion pour ce serveur",
            color=discord.Color.green()
        )

        # Adding fields to the embed for better structure
        embed.add_field(name="IP", value=f"`{MC_SERVER_IP}`", inline=True)
        embed.add_field(name="Port", value=f"`{MC_SERVER_PORT}`", inline=True)
        embed.add_field(name="Joureurs en ligne", value=f"`{status.players.online}/{status.players.max}`", inline=True)

        # Set a footer with the name of the user who requested the status
        embed.set_footer(text=f"Demandé effectuée par {ctx.author.display_name}")

        await ctx.send(embed=embed)
    else:
        await ctx.send(response)

if __name__ == "__main__":
    try:
        logging.info("Le bot commence...")
        bot.run(TOKEN)
    except Exception as e:
        logging.error(f"A échoué à démarrer le bot: {e}", exc_info=True)