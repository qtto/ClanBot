import discord, time, asyncio, json, sys
from discord.ext import commands
from get_data import *

description = '''
    A bot for the redditors clan.
    Returns information from the google spreadsheet.
    '''

ERROR_CHANNEL: '' #Send errors to this channel
TOKEN = ''
UPDATE = 60 #Clan list update frequency in seconds
TOP_RANKS = ['general', 'admin', 'organiser', 'coordinator', 'overseer', 'deputy owner', 'owner'] #Big boys can't rank up
EMBED_COLOR = 0xff6666

client = discord.Client()   #Create the client object


#Update clannie list n seconds
async def update_clannies():
    await client.wait_until_ready()
    while client.is_logged_in:
        data = await get_data()
        if not data:
            print('Error getting data.')
        await asyncio.sleep(UPDATE)


async def check_clannie(name):
    name_clean = str(name).lower().replace(' ', '\xa0')     #Google's API returns spaces like this
    name_url = str(name).replace(' ', '_')          #To use in URLS (please no 400's)
    chathead = f'https://secure.runescape.com/m=avatar-rs/{name_url}/chat.png'

    msg = discord.Embed(color=EMBED_COLOR)          #Create the embed object
    msg.set_author(name=name, icon_url=chathead)    #Set the author
    msg.set_thumbnail(url=chathead)                 #Set the thumbnail

    found = False

    with open('spreadsheet.json', 'r') as f:
        data = json.loads(f.read()) #Creates more overhead than needed, but asyncio makes using global vars hard

        if len(data) > 0:
            for clannie in data:    #Could definitely be optimized better but doesn't really affect performance enough
                if str(clannie[0]).lower() == name_clean:
                    found = True

                    msg.add_field(name='Rank', value=str(clannie[1]))
                    msg.add_field(name='Clan Points', value=str(clannie[2]))

                    if clannie[1].lower() not in TOP_RANKS:     #Only add these if the person can rank up further
                        msg.add_field(name='Rank up (caps)', value=str(clannie[4]))
                        msg.add_field(name='Rank up (XP)', value=str(clannie[5]))

                    cap_message = ':negative_squared_cross_mark:'
                    if clannie[3]:
                        cap_message =  ':white_check_mark:'

                    msg.add_field(name='Capped this week', value=cap_message, inline=False)

            if not found:
                msg.add_field(name='Sorry!', value=f'{name} was not found in the database.')

        else:
            msg.add_field(name='Error!', value='Failed getting the data. Try again later.')

        return msg


@client.event
async def on_ready():
    print('Ready! Logged in as {}'.format(client.user.name))
    await client.change_presence(game=discord.Game(name='with Redditors'))


@client.event
async def on_error(event, *args, **kwargs):
    err = sys.exc_info()
    fmt = 'I ran into an error: {}'
    channel = discord.Object(id=ERROR_CHANNEL)
    await client.send_message(channel, fmt.format(err))


@client.event
async def on_message(message):
    #Don't respond to self (!clannie !clannie)
    if message.author == client.user:
        return

    #Parse !clannie messages
    elif message.content.lower().startswith('!clannie '):
        clannie = message.content[9:]
        if len(clannie) > 0:
            msg = await check_clannie(clannie)
            await client.send_message(message.channel, embed = msg)

    elif message.content.startswith('!help'):
        await client.send_message(message.channel, '**Usage**: !clannie *name*')



if __name__ == '__main__':
    client.loop.create_task(update_clannies()) #Create BG task
    client.run(TOKEN) #Log in
