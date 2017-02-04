import discord, time, asyncio, json, sys, os.path
from discord.ext import commands
from get_data import *

description = '''
    A bot for the redditors clan.
    Returns information from the google spreadsheet.
    '''

TOKEN = ''
UPDATE = 120 #Clan list update frequency in seconds
TOP_RANKS = ['general', 'admin', 'organiser', 'coordinator', 'overseer', 'deputy owner', 'owner'] #Big boys can't rank up
EMBED_COLOR = 0xff6666

client = discord.Client()   #Create the client object


#Update clannie list n seconds
async def update_clannies():
    await client.wait_until_ready()
    while client.is_logged_in:
        try:
            data = await get_data()
            if not data:
                print('Error getting data.')
            await asyncio.sleep(UPDATE)
        except Exception as e:
            print(e)
            return

async def set_rsn(author, name):
    if not os.path.isfile('links.json'):
        with open('links.json', 'w') as f:
            json.dump({author.id: name}, f)
            print('Created links.json')

    else:
        with open('links.json', 'r') as f:
            names = json.loads(f.read())
            names[author.id] = str(name)
        with open('links.json', 'w') as f:
            json.dump(names, f)

    return f'Okay, {author.display_name}! Your name {name} has been set.'


async def find_rsn(author):
    try:
        with open('links.json', 'r') as f:
            names = json.loads(f.read())
            if author.id in names:
                return await check_clannie(names[author.id])
            else:
                return f'Sorry, {author.display_name}! I couldn\'t find your name in my database.'

    except Exception as e:
        return 'Sorry! There was an error reading the database. It might be empty: try setting your username with !rsn *name*.'


async def check_clannie(name):
    name_clean = str(name).lower().replace(' ', '\xa0')     #Google's API returns spaces like this
    name_url = str(name).replace(' ', '_')          #To use in URLS (please no 400's)
    chathead = f'https://secure.runescape.com/m=avatar-rs/{name_url}/chat.png'

    msg = discord.Embed(color=EMBED_COLOR)          #Create the embed object
    msg.set_author(name=name, icon_url=chathead)    #Set the author
    msg.set_thumbnail(url=chathead)                 #Set the thumbnail
    msg.set_footer(text=f'It can take up to {UPDATE} seconds to update the database. Direct requests @ Otto')

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

                    cap_mark = '👎'
                    if clannie[3].lower() == 'yes':
                        cap_mark = '👍'

                    msg.add_field(name='Capped this week', value=cap_mark, inline=False)

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
    channel = discord.Object(id='223232913221746688')
    await client.send_message(channel, fmt.format(err))


@client.event
async def on_message(message):
    #Don't respond to self (!clannie !clannie)
    if message.author == client.user:
        return

    #Parse !clannie messages
    elif message.content.lower().startswith('!clannie'):
        name = message.content[9:]
        if len(name) > 0:
            msg = await check_clannie(name)
            await client.send_message(message.channel, embed = msg)
        else:
            msg = await find_rsn(message.author)
            if type(msg) == str:
                await client.send_message(message.channel, msg)
            else:
                await client.send_message(message.channel, embed = msg)

    elif message.content.lower().startswith('!rsn'):
        name = message.content[5:]
        if 0 < len(name) < 20:
            msg = await set_rsn(message.author, name)
            await client.send_message(message.channel, msg)
        else:
            await client.send_message(message.channel, 'Please enter a valid name to set!')

    elif message.content.startswith('!help'):
        await client.send_message(message.channel, '**Usage**: \n - !clannie *name*: *name* is optional, read on! \
\n - use !rsn *name* to bind your RSN to your Discord account. You can then use !clannie to get your info easily.')



if __name__ == '__main__':
    client.loop.create_task(update_clannies()) #Create BG task
    client.run(TOKEN) #Log in
