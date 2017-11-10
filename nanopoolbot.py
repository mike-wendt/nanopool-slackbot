import os
import time
import re
import sys
import traceback
import requests
from datetime import datetime
from slackclient import SlackClient

"""
    Load environment variables
"""
WALLET_ID = os.environ.get('WALLET_ID')
OFFLINE_MIN = os.environ.get('OFFLINE_MIN')
BOT_ID = os.environ.get('BOT_ID')
BOT_TOKEN = os.environ.get('BOT_TOKEN')

"""
    CONSTANTS
"""
AT_BOT = "<@" + BOT_ID + ">"
NANOPOOL_URL = "https://api.nanopool.org/v1/eth/"
NANOPOOL_WORKER_URL = "https://eth.nanopool.org/account/"+WALLET_ID+"/"
ETHERSCAN_URL = "https://etherscan.io/address/"+WALLET_ID

"""
    Instantiate Slack client
"""
sc = SlackClient(BOT_TOKEN)

"""
    Slack command parser
"""
def handle_command(command, channel, user):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = ":question: Unknown/invalid command - Try `help` for a list of supported commands"
    commands = command.split()
    try:
        if commands:
            operator = commands[0].lower()
            s = " "
            msg = s.join(commands[1:])
            if operator == "on":
                response = list_online()
            elif operator == "off":
                response = list_offline()
            elif operator == "all":
                response = list_all()
            elif operator == "pool":
                response = show_pool()
            elif operator == "wallet":
                response = show_wallet()
            elif operator == "help":
                response = show_commands()
    except ValueError:
        respone = show_commands()
    except RuntimeError as e:
        response = e[0]
    message = "<@" + user + "> " + response
    sc.api_call("chat.postMessage", channel=channel, \
                          text=message, as_user=True)

def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                user = output['user']
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip(), \
                       output['channel'], user
    return None, None, None

"""
    Slack command handler functions
"""
def show_commands():
    """
        Return ist of commands that bot can handle
    """
    return ":hammer_and_wrench: *List of supported commands:*\n" \
            "`on` - list all online workers\n" \
            "`off` - list all offline workers\n" \
            "`all` - list all workers\n" \
            "`pool` - show link for nanopool stats page\n" \
            "`wallet` - show link for Etherscan wallet\n"

def list_workers(online):
    if online:
        header = ":white_check_mark: *Workers Online"
    else:
        header = ":x: *Workers Offline"

    count, workers = show_workers(np_get_workers(online))

    header += " ("+str(count)+")*\n"

    return header+workers

def list_online():
    return list_workers(True)

def list_offline():
    return list_workers(False)

def list_all():
    response = list_workers(True)
    response += list_workers(False)
    return response

def show_pool():
    return "<"+NANOPOOL_WORKER_URL+"|nanopool stats page>"

def show_wallet():
    return "<"+ETHERSCAN_URL+"|Etherscan wallet>"

"""
    Formatting functions
"""
def show_workers(workers):
    try:
        now = time.time()
        response = ""
        count = len(workers)
        for worker in workers:
            response += "> <"+NANOPOOL_WORKER_URL+worker['id']+"|"+worker['id']+">  _"+show_timediff(now,worker['lastShare'])+ \
                        "_  rating _"+str(worker['rating'])+"_  hash _"+str(worker['hashrate'])+" Mh/s_ \n"
        return count, response
    except:
        traceback.print_exc(file=sys.stderr)
        raise RuntimeError(":x: show_workers failed")

def show_timediff(now, then):
    diff = int(now) - int(then)

    if diff <= 60:
        return "less than a minute"
    elif int(diff / 60) == 1:
        return "1 minute ago"
    elif int(diff / 60) < 60 and int(diff / 60) > 1:
        return str(int(diff / 60))+" minutes ago"
    elif int(diff / 3600) == 1:
        return "1 hour ago"
    elif int(diff / 3600) < 24 and int(diff / 3600) > 1:
        return str(int(diff / 3600))+" hours ago"
    elif int(diff / 86400) == 1:
        return "1 day ago"
    elif int(diff / 86400) > 1:
        return str(int(diff / 86400))+" days ago"
    else:
        return "unknown"

"""
    Nanopool functions
"""
def np_get_workers(online):
    try:
        now = time.time()
        r = requests.get(NANOPOOL_URL+"workers/"+WALLET_ID)
        json = r.json()

        workers_on = []
        workers_off = []

        if json and json['status']:
            for w in json['data']:
                diff = int(now) - int(w['lastShare'])
                if diff > int(OFFLINE_MIN) * 60:
                    # worker offline
                    workers_off.append(w)
                else:
                    workers_on.append(w)

        if online:
            return workers_on
        else:
            return workers_off
    except:
        traceback.print_exc(file=sys.stderr)
        raise RuntimeError(":x: Failed in getting worker list from Nanopool")

"""
    Main
"""
if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if sc.rtm_connect():
        print("NanopoolBot connected and running!")
        while True:
            command, channel, user = parse_slack_output(sc.rtm_read())
            if command and channel and user != BOT_ID:
                handle_command(command, channel, user)
            elif channel and user != BOT_ID:
                handle_command("help", channel, user)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
