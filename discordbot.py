from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from discord.ext import commands
import discord, random, smtplib, datetime

BOT_TOKEN = ""
SERVER_ID = 00000000000000000
SERVER_ROLE = ""

EMAIL = ""
EMAIL_APP_SPECIFIC_PASSWORD = ""

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!',intents=intents)

verification = {}

#
# !register <sfsu_email>
#
@bot.command()
async def register(ctx, arg):
    # check if DM
    if not isinstance(ctx.channel, discord.channel.DMChannel):
        await ctx.message.delete()

    if checktxt(str(ctx.message.author.id)):
        await ctx.message.add_reaction('❌')
        await ctx.author.send("You are already verified!")
    else:
        await check_email(ctx, arg)

#
# !verify <verification code>
#
@bot.command()
async def verify(ctx, arg1):
    # check if DM
    if not isinstance(ctx.channel, discord.channel.DMChannel):
        await ctx.message.delete()

    if not ctx.message.author.id in verification:
        await ctx.author.send("You don't have an SFSU email waiting for verification!")
        await ctx.message.add_reaction('❌')
        return

    server = bot.get_guild(SERVER_ID)
    role = discord.utils.get(server.roles, name=SERVER_ROLE)
    member = server.get_member(ctx.message.author.id)
    try:
        if int(arg1) == verification[ctx.message.author.id][0]:
            #print("Verification code is VALID ...")
            await member.add_roles(role)
            embed = discord.Embed(title="✅ Email Verified",timestamp=datetime.datetime.utcnow(),description="You have been successfully verified :sparkles: \n\n:tickets: The " + SERVER_ROLE + " role has been added to your account!",color=0x62C979)
            embed.set_footer(text="SFSU Email Bot",icon_url="https://i.imgur.com/Drg5lcw.png")
            await ctx.author.send(embed=embed)
            await ctx.message.add_reaction("✅")
            #print("Writing email into emails.txt ...")
            write_email_to_txt(str(ctx.message.author.id) + " | " + verification[ctx.message.author.id][1])
            verification.pop(ctx.message.author.id)
        else:
            await ctx.author.send('You entered the wrong verification code!')
            await ctx.message.add_reaction('❌')
    except:
        await ctx.author.send('Something went wrong!')
        await ctx.message.add_reaction('❌')

@bot.event
async def on_ready():
        print("=> SFSU EMAIL VERIFICATION BOT ONLINE")
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="your emails"))

#
# sends verification email to email
#
async def send_email(ctx, code, receiver):
    sender_address = EMAIL
    sender_pass = EMAIL_APP_SPECIFIC_PASSWORD
    receiver_address = receiver
    body = str(code) + " is your verification code.\nReply to the bot !verify <code>"
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = 'SFSU MC BOT - ' + str(code) + ' is your verification code!'   # SUBJECT LINE
    session = smtplib.SMTP('smtp.gmail.com', 587)
    message.attach(MIMEText(body, 'plain'))
    session.starttls()
    session.login(sender_address, sender_pass)
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()
    print("Successfully sent verification code " + str(code) + " to " + receiver)
    embed = discord.Embed(title="📨 Email Sent!",timestamp=datetime.datetime.utcnow(),description='Verification email successfully sent to \n\n**' + receiver + "**\n\nType `!verify <code>` to get a role in the server!",color=0x62C979)
    embed.set_footer(text="SFSU Email Bot",icon_url="https://i.imgur.com/Drg5lcw.png")
    await ctx.message.add_reaction("📩")
    await ctx.author.send(embed=embed)

#
# CHECKS IF EMAIL HAS @sfsu.edu 
#
async def check_email(ctx, email):
    print("Checking email " + email)
    authorId = ctx.message.author.id
    print(authorId)
    if (checktxt(email)):
        #print("Email is already used!")
        await ctx.message.add_reaction('❌')
        await ctx.author.send('**' + email + '** is already being used! ')
    elif "@sfsu.edu" in email:
        code = random.randint(111111,999999) # generates a 6 digit number and uses that as the verification code
        verification[authorId] = [code,email]
        await send_email(ctx, code, email)
    else:
        await ctx.message.add_reaction('❌')
        await ctx.author.send('That is not a valid SFSU email! Did you forget the **@sfsu.edu**?')

#
# WRITES EMAIL INTO 'emails.txt' FILE
#
def write_email_to_txt(email):
    file1 = open("./sfsu email bot/emails.txt","a")
    file1.write(email + "\n")
    print("Successfully written " + email + " into emails.txt")
    file1.close

#
# CHECKS IF EMAIL IS IN 'emails.txt' FILE
#
def checktxt(email):
    file1 = open("./sfsu email bot/emails.txt", "r")
    flag = 0
    index = 0
    for line in file1:  
        index += 1 
        if email in line:
            flag = 1
            break 
    file1.close() 
    if flag == 0: 
        return False
    else: 
        return True

bot.run(BOT_TOKEN)

#
# SUMMARY:
# Checks email has "@sfsu.edu" and checks if it's in emails.txt file
# If it does, generate random 5 digit code, store in array
# Send email with 5 digit code 
# !verify <email> <code> checks if code is in array, if it is then add role to user and remove from array (so code can't be used multiple times)
# Stores email in .txt file
#
