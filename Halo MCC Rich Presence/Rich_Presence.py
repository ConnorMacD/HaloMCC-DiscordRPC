from xbox.webapi.authentication.manager import AuthenticationManager
from xbox.webapi.common.exceptions import AuthenticationException
from xbox.webapi.api.client import XboxLiveClient
from pypresence.presence import Presence
import sys, time, os

def main():
    #update this variable with a valid Client ID. You can get one from creating an application at https://discordapp.com/developers.
    discord_client_id = int(input("Enter valid Client ID (Must be a Number): "))
    largeI = str(input("Enter Large Image (Must be a Name):"))
    smallI = str(input("Enter Small Image (Must be a Name):"))

    xbox_status_last_change = None
    discord_online_status = False

    if discord_client_id == None:
        print("The discord_client_id variable is None. Update the script with a valid Discord client ID.\nGo to https://discordapp.com/developers to create an application for a Client ID.")
        time.sleep(5)
        sys.exit(0)
    if discord_client_id <= 0:
        print("That is not a valid id")
        time.sleep(5)
        sys.exit(0)

    ## Handle XBL API authentication
    try:
        xbox_token = os.getenv('LOCALAPPDATA') + "\\OpenXbox\\xbox\\tokens.json"
        auth_mgr = AuthenticationManager.from_file(xbox_token)
    except FileNotFoundError as e:
        print(
        'Failed to load tokens from \'{}\'.\n'
        'ERROR: {}'.format(e.filename, e.strerror)
        )
        time.sleep(5)
        sys.exit(-1)
    try:
        auth_mgr.authenticate(do_refresh=True)
    except AuthenticationException as e:
        print('Authentication failed! Err: %s' % e)
        time.sleep(5)
        sys.exit(-1)
    ## Make the connection to XBL
    xbl_client = XboxLiveClient(auth_mgr.userinfo.userhash, auth_mgr.xsts_token.jwt, auth_mgr.userinfo.xuid)

    ## discord RPC init 
    discordRPC = Presence(discord_client_id)

    ## Discord RPC update loop

    while True:
        try:
            ##get current presence
            XboxPresence = xbl_client.presence.get_presence_own().json()
            ##If we're online, do all this
            if (XboxPresence['state'] == 'Online'):
                OnlineDevices = XboxPresence['devices']
                for ActiveTitles in OnlineDevices:
                    ##check if we're actually playing MCC
                    if ActiveTitles['titles'][0]['name'] == "Halo: The Master Chief Collection" and ActiveTitles['type'] == "Win32":
                        print("We're playing Halo!")
                        ##start Discord RPC
                        if discord_online_status == False:
                            print("Discord RPC not running. Starting!")
                            discordRPC.connect()
                            discord_online_status = True
                            print("Discord RPC Started")
                        ##set the current status
                        try:
                            DiscordStatus = ActiveTitles['titles'][0]['activity']['richPresence'].split(" - ")
                            discordRPC.update(large_image=largeI, large_text='Halo: MCC', small_image=smallI, small_text="Playing on PC", state=DiscordStatus[0], details=DiscordStatus[1])
                        except Exception as e:
                            print(e)
                        break
                else:
                    print("Guess we're not playing Halo.")
                    if discord_online_status == True:
                        print("Closing Discord RPC Connection!")
                        discordRPC.close()
                        discord_online_status = False
            else:
                print("You're not online on XBL at the moment.")
                if discord_online_status == True:
                        print("Closing Discord RPC Connection!")
                        discordRPC.close()
                        discord_online_status = False
            time.sleep(15)
        except Exception as e:
            print(e)
            print("Crashed or received KeyboardInterrupt! Closing Discord RPC and shutting down script...")
            if discord_online_status == True:
                        print("Closing Discord RPC Connection!")
                        discordRPC.close()
                        discord_online_status == False
            time.sleep(5)
            sys.exit(0)
