import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests
import random
from discord.ext import commands
import discord

bot_token = ""
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!',intents=intents)

verificationcodes = []

#
# !register <sfsu_email>
#
@bot.command()
async def register(ctx, arg):
     await ctx.author.send('Checking your email!')
     await check_email(ctx, arg)

#
# !verify <sfsu_email> <verif code>
#
@bot.command()
async def verify(ctx, arg1, arg2):
    server = bot.get_guild(883246479702114335) # <-- SERVER ID GOES HERE
    role = discord.utils.get(server.roles, name="verified") # <-- ROLE NAME GOES HERE
    member = server.get_member(ctx.message.author.id)
    #print(member)
    if int(arg2) in verificationcodes:
        print("Verification code is VALID ...")
        await member.add_roles(role)
        await ctx.author.send('Success! The verified role has been added to your account! :white_check_mark: ')
        print("Writing email into emails.txt ...")
        write_email_to_txt(arg1)
        verificationcodes.remove(int(arg2)) # REMOVES VERIFICATION CODE FROM ARRAY SO IT CAN'T BE USED MULTIPLE TIMES
    else:
        print("Verification code is NOT VALID!")

@bot.event
async def on_ready():
        print("BOT IS ONLINE AND READY TO VERIFY SFSU EMAILS")
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="your emails"))

#
# sends verification email to email
#
async def send_email(ctx, code, receiver):
    sender_address = '@gmail.com'
    sender_pass = '' # APP SPECIFIC PASSWORD 
    receiver_address = receiver
    body = str(code) + " is your verification code.\nReply to the bot !verify <email> <code>"
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = 'shdwverify - ' + str(code) + ' is your verification code!'   # SUBJECT LINE
    session = smtplib.SMTP('smtp.gmail.com', 587)
    message.attach(MIMEText(body, 'plain'))
    session.starttls() # enables security
    session.login(sender_address, sender_pass) # LOGS IN WITH EMAIL AND PASSWORD 
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()
    print("Successfully sent verification code " + str(code) + " to " + receiver)
    await ctx.author.send('Verification email successfully sent to ' + receiver)
    await ctx.author.send('Type `!verify <email> <code>` to get a role in the server!')

#
# CHECKS IF EMAIL HAS @sfsu.edu 
#
async def check_email(ctx, email):
    print("Checking email " + email )
    if (checktxt(email)):
        print("Email is already used!")
        await ctx.author.send('Email is already being used! :x:')
    elif "@sfsu.edu" in email:
        code = random.randint(11111,99999) # generates a 5 digit number and uses that as the verification code
        verificationcodes.append(code) # stores verification code into array
        await send_email(ctx, code, email)
    else:
        print("Email not a valid SFSU email!")
        await ctx.author.send('That is not a valid SFSU email! :x:')

#
# WRITES EMAIL INTO 'emails.txt' FILE
#
def write_email_to_txt(email):
    file1 = open("emails.txt","a")
    file1.write(email + "\n")
    print("Successfully written " + email + " into emails.txt")
    file1.close

#
# CHECKS IF EMAIL IS IN 'emails.txt' FILE
#
def checktxt(email):
    file1 = open("emails.txt", "r")
    flag = 0
    index = 0
    for line in file1:  
        index += 1 
        if email in line:
            flag = 1
            break 
    file1.close() 
    if flag == 0: 
        #print('EMAIL IS NOT FOUND') 
        return False
    else: 
        #print('EMAIL IS FOUND')
        return True

bot.run(bot_token)

#
# SUMMARY:
# Checks email has "@sfsu.edu" and checks if it's in emails.txt file
# If it does, generate random 5 digit code, store in array
# Send email with 5 digit code 
# !verify <email> <code> checks if code is in array, if it is then add role to user and remove from array (so code can't be used multiple times)
# Stores email in .txt file
#
