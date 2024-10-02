
TWITCH_CLIENT_ID = '' #get this from the developer application page. This should change per application! This lets twitch know which app is asking for perms
oauth_token = None
channel_name = 'ERROR: NO CHANNEL NAME PROVIDED' #this needs to match the streamer's name.

redirect_uri = "http://localhost:8080/callback" #this is the Oauth redirect URI in the developer page

TWITCH_AUTH_LINK = f'https://id.twitch.tv/oauth2/authorize?response_type=token&client_id={TWITCH_CLIENT_ID}&redirect_uri={redirect_uri}&scope=chat:read+chat:edit+channel:read:redemptions+channel:manage:redemptions+channel:manage:polls+channel:manage:predictions+channel:read:polls+channel:read:predictions&state=frontend|cG00TExydnVqNERmZGpvRnR4S3ljUT09&force_verify=true'
# empty URL: https://id.twitch.tv/oauth2/authorize?response_type=token&client_id={TWITCH_CLIENT_ID}&redirect_uri={redirect_uri}&scope= [SCOPE STUFF HERE] &state=frontend|cG00TExydnVqNERmZGpvRnR4S3ljUT09&force_verify=true

TWITCH_USERS_LINK = f'https://api.twitch.tv/helix/users' #link to get username information

from twitchio.ext import commands
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse as urlparse
import requests

#A simple HTTP server to handle the redirect and capture the authorization token
class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
# Serve a page with JavaScript that will extract the full URL including the fragment
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        # HTML with JavaScript to extract the fragment (OAuth token) and send it to the this script
        html_content = """
        <html>
        <body>
            <script type="text/javascript">
                // Extract the full URL from the browser, including the fragment
                const fullURL = window.location.href;

                // Send the full URL back to the server using a POST request
                fetch("http://localhost:8080/full_url", {
                    method: "POST",
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: "full_url=" + encodeURIComponent(fullURL)
                }).then(response => {
                    document.body.innerHTML = "URL captured! You can close this window.";
                }).catch(error => {
                    document.body.innerHTML = "Error capturing the URL.";
                });
            </script>
            <p>Processing OAuth token...</p>
        </body>
        </html>
        """
        self.wfile.write(html_content.encode('utf-8'))

    def do_POST(self):
        global oauth_token  # Reference the global variable
        # Handle the POST request when the full URL is sent from JavaScript
        if self.path == "/full_url":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            # Extract the full URL from the POST body
            full_url = post_data.split("full_url=")[1]
            full_url = full_url.replace('%3A', ':').replace('%2F', '/').replace('%23', '#')  # Decode URL-encoded characters
            #print(f"Full URL captured: {full_url}")
        
            # Step 1: Find the position of the '#' and '&'
            start_pos = full_url.find('#') + 1  # Add 1 to move past the '#'
            end_pos = full_url.find('&', start_pos)  # Find the first '&' after '#'

            # Step 2: Extract the substring between '#' and '&'
            token_fragment = full_url[start_pos:end_pos]
            #print(f"Extracted fragment: {token_fragment}\n")

            # Step 3: Split the fragment to get the token
            oauth_token = token_fragment.split('%')[1]
            oauth_token = oauth_token[2:] #idk why the extractor has these two extra chars, but I'm just gonn remove them

            self.send_response(200)
            self.end_headers() #close connection
            self.wfile.write(b"Token received on server.")

#Commands for the bot itself. If you want to add custom commands, this is where you do so!
class Bot(commands.Bot):

    def __init__(self):
        # Initialize the bot with the necessary OAuth token, prefix, and initial channels
        super().__init__(token=oauth_token, prefix='!', initial_channels=[channel_name])

    async def event_ready(self):
        # Called once when the bot is connected
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')
        channel = self.get_channel(channel_name)
        await channel.send(f'Connected from balatro!')

    async def event_reward_redeem(self, reward_id, user, message):
        # Triggered when a channel point reward is redeemed
        print(f'{user.name} redeemed a reward: {reward_id} with message: {message}')
        # Example: send a message when a reward is redeemed
        await self.get_channel('your_channel').send(f'Thank you {user.name} for redeeming points!')

#An example command. Run !hello and it wil lsay hello back!
    @commands.command(name='hello')
    async def hello_command(self, ctx):
        # Sends a hello message when the !hello command is used
        await ctx.send(f'Hello! Nice to meet you!')

# Basic function to run a server locally to receive authorization token from twitch
def run_server():
    server_address = ('localhost', 8080)
    httpd = HTTPServer(server_address, OAuthHandler)
    
    # Wait until the token is captured and stored in the server object
    print("Waiting for OAuth token...")
    httpd.handle_request()  # Handle the first GET request (serve the page)
    httpd.handle_request()  # Handle the POST request with the full URL




#----------- ACTUAL START OF SCRIPT -----------------------



#Tell user what's up
print("Welcome to the Ottercontrol 1.0!")
input("First, let's get your OAuth ID. \nNote if it doesn't open, or opens in the wrong web browser, you should be able to just copy the URL in the right one.\nMake sure you are ALREADY STREAMING!\nAnd it should be the account that is streaming.\nPress enter to begin authorization.")
# Step 1: Open the authorization URL in the user's web browser
webbrowser.open(TWITCH_AUTH_LINK)

# Call the function to start the server and capture the token
run_server()

#user performs authorization in browser

# Make the request to get user info
response = requests.get(TWITCH_USERS_LINK, headers={
    'Authorization': f"Bearer {oauth_token}",
    'Client-Id': TWITCH_CLIENT_ID
})

# Get the streamer's username to connect to the chat
if response.status_code == 200:
    user_data = response.json()
    if user_data['data']:
        # Get the channel name
        channel_name = user_data['data'][0]['display_name']

        print(f"Channel Name: {channel_name}")
    else:
        print("No user data found.")
else:
    print(f"Error: {response.status_code} - {response.text}")

# Now run the bot and check for commands!
bot = Bot()
bot.run()
