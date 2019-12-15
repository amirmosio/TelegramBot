<p>Telegram Bot Using PyTelegramBotAPI and TelegramClient</p>


This code is an easy telegram chat bot that give message from students and send them to the related teacher then teachers can send their answers.
The code save the student chat id in a sqlite3 database to give the ability to send a message to all student.
All students memeber of <channel username> have access to teachers and every time they ask a question we should check if they are member or not.

<p>Dependecies:</p>
	<p>pytelegrambotapi</p>
	<p>telethon</p>
	<p>sqlite3</p>
	<p>asyncio--> this library is for python new versions</p><br>

I use two diffrent things that telegram gave us.
First part of this code used pytelegrambotapi to create a bot and used polling to get new updates.
In my experience it is better to use webhook to get message update.It is so much faster and in case you want to deploy your bot on free server like heroku you have to user webhook and you will get error using polling.So belive me, I tried so much, just listen and don't waste your time.

It is so cool to use only TelegramClient because it is not only a bot.You can use it as a client and then you are even able to controll your telegram account. Or in case you are interested in AI
you can use this to train and test your AI.
