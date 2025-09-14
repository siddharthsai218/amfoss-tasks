import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import aiohttp
import asyncio

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")


# Intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents,help_command=None)


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"{bot.user} is online!")


def chunk_text(text, chunk_size=1024):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]


@bot.tree.command(name="greet", description="Sends greeting to the user")
async def greet(interaction: discord.Interaction):
    username = interaction.user.mention
    await interaction.response.send_message(f"Hello , {username}")

@bot.command()
async def lyrics(ctx, *, query: str):
    if '-' not in query:
        await ctx.reply("Please use correct format: `<song name> - <artist>`")
        return

    song, artist = query.split('-', 1)
    song = song.strip()
    artist = artist.strip()

    await ctx.typing()

    url = f"https://lrclib.net/api/search?q={song} {artist}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()

    if not data:
        await ctx.reply(f"Lyrics are not found for '{song}' by '{artist}'")
        return

    lyrics_text = data[0].get("plainLyrics", "Lyrics not available")
    chunks = chunk_text(lyrics_text)

    for i, chunk in enumerate(chunks, 1):
        embed = discord.Embed(
            title=f"Lyrics of '{song}' by {artist}" if i == 1 else None,
            description=chunk,
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Part {i} of {len(chunks)}")
        await ctx.send(embed=embed)
        await asyncio.sleep(0.25)


@bot.command()
async def track(ctx, *, query: str):
    """Fetch track info from MusicBrainz API"""
    await ctx.typing()

    search_url = "https://musicbrainz.org/ws/2/recording/"
    params = {'query': query, 'fmt': 'json', 'limit': 1}

    async with aiohttp.ClientSession() as session:
        async with session.get(search_url, params=params) as resp:
            data = await resp.json()

    if not data.get('recordings'):
        await ctx.send("No track found!")
        return

    track = data['recordings'][0]
    title = track.get('title', 'Unknown')
    artist = track['artist-credit'][0]['name'] if track.get('artist-credit') else 'Unknown'
    release_list = track.get('releases')
    album = release_list[0]['title'] if release_list else 'Unknown'
    release_date = release_list[0].get('date', 'Unknown') if release_list else 'Unknown'
    length_ms = track.get('length', 0)
    duration = f"{length_ms//60000}:{(length_ms//1000)%60:02d}" if length_ms else 'Unknown'

    embed = discord.Embed(
        title=title,
        description=f"Artist: {artist}",
        color=discord.Color.blue()
    )
    embed.add_field(name="Album", value=album, inline=False)
    embed.add_field(name="Duration", value=duration, inline=False)
    embed.add_field(name="Release Date", value=release_date, inline=False)

    await ctx.send(embed=embed)




user_playlists = {}


if os.path.exists("playlist.txt"):
    with open("playlist.txt", "r") as f:
        for line in f:
            line = line.strip()
            if line:
                user_id, songs = line.split(":", 1)
                user_playlists[int(user_id)] = songs.split(",") 


def save_playlists():
    with open("playlist.txt", "w") as f:
        for user_id, songs in user_playlists.items():
            f.write(f"{user_id}:{','.join(songs)}\n")


@bot.command()
async def playlist(ctx, action: str, *, song: str = None):
    user_id = ctx.author.id

    if user_id not in user_playlists:
        user_playlists[user_id] = []

    action = action.lower()

    if action == "add":
        if not song:
            await ctx.send("Please specify a song to add.")
            return
        user_playlists[user_id].append(song)
        save_playlists()
        await ctx.send(f" Added **{song}** to your playlist!")

    elif action == "remove":
        if not song:
            await ctx.send("Which song to remove.")
            return
        if song in user_playlists[user_id]:
            user_playlists[user_id].remove(song)
            save_playlists()
            await ctx.send(f" Removed **{song}** from your playlist.")
        else:
            await ctx.send(f"  **{song}** is not there in your playlist.")

    elif action == "view":
        if not user_playlists[user_id]:
            await ctx.send("Your playlist is empty!")
            return
        playlist_text = "\n".join([f"{i+1}. {s}" for i, s in enumerate(user_playlists[user_id])])
        await ctx.send(f" **Your Playlist:**\n{playlist_text}")

    elif action == "clear":
        user_playlists[user_id] = []
        save_playlists()
        await ctx.send(" CLEARED.")

    else:
        await ctx.send("Invalid Use: add/remove/view/clear.")

@bot.command()
async def trending(ctx):
    """Shows top 10 trending tracks from Deezer"""
    await ctx.typing()

    url = "https://api.deezer.com/chart/0/tracks?limit=10"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                await ctx.send("Failed to fetch trending tracks.")
                return
            data = await resp.json()

    tracks = data.get("data", [])
    if not tracks:
        await ctx.send("No trending tracks found.")
        return

    embed = discord.Embed(
        title=" Top 10 Trending Tracks",
        color=discord.Color.orange()
    )

    for i, track in enumerate(tracks, 1):
        title = track.get("title")
        artist = track.get("artist", {}).get("name")
        link = track.get("link")  
        embed.add_field(
            name=f"{i}. {title} — {artist}",
            inline=False
        )

    await ctx.send(embed=embed)

@bot.command()
async def recommend(ctx, *, genre: str):
    await ctx.typing()
    
    url = "http://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "tag.gettoptracks",
        "tag": genre.lower(),
        "api_key": LASTFM_API_KEY,
        "format": "json",
        "limit": 10
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            if resp.status != 200:
                await ctx.send("Failed to fetch recommendations. Try again later.")
                return
            data = await resp.json()

    tracks = data.get("tracks", {}).get("track", [])
    if not tracks:
        await ctx.send(f"No recommendations found for genre: {genre}")
        return

    embed = discord.Embed(
        title=f" Top 10 Tracks for '{genre}'",
        color=discord.Color.green()
    )

    for i, track in enumerate(tracks, 1):
        name = track.get("name")
        artist = track.get("artist", {}).get("name")
        link = track.get("url") 
        embed.add_field(
            name=f"{i}. {name} — {artist}",
            value=f"Music",
            inline=False
        )

    await ctx.send(embed=embed)

@bot.command()
async def help(ctx):
    
    await ctx.typing()
    
    embed = discord.Embed(
        title=" Welcome to Music Bot!",
        description="Lists all commands",
        color=discord.Color.blue()
    )
    

    embed.add_field(
        name="/lyrics <song> - <artist>",
        value="Gives lyrics for song.",
        inline=False
    )
    embed.add_field(
        name="/track <song>",
        value="Gives info on the song.",
        inline=False
    )
    embed.add_field(
        name="/playlist [add/remove/view/clear] [song]",
        value="Edit playlist.",
        inline=False
    )
    embed.add_field(
        name="/trending",
        value="Shows top 10 trending tracks.",
        inline=False
    )
    embed.add_field(
        name="/recommend <genre>",
        value="Recommends music ",
        inline=False
    )

    embed.set_footer(text="Enjoy the music! 🎵")
    
    await ctx.send(embed=embed)








bot.run(TOKEN)
