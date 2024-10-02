# BasicTwitchBotTemplate
A basic python twitch bot template. Will automatically gather the streamer's credentials and has an example command.

-Setup-
Make sure to use head to the twitch application dashboard (https://dev.twitch.tv/console) to create your application and get a client ID! Then set it to the CLIENT_ID variable.
Set the OAuth Redirect URL to "http://localhost:8080/callback". This is the URI of the local server run on the streamer's PC that the application connects to.

Once you've got that set up, you're ready to go to create your own custom commands!

-Using-
0) Install packages (see the import lines for what you need to import. It's not much)
1) Begin streaming
2) Install python (at least 3.6 or above)
3) Navigate to the script with the console
4) Run "python TwitchBot.py"
5) Follow instructions to authorize the bot.


-LICENSE-
This is so simple I don't have any real restrictions on it. Go nuts.
