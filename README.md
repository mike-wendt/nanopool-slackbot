# nanopool-slackbot
Slackbot for Nanopool to watch workers and report mining info

## Overview

`nanopool-slackbot` is designed to monitor workers on a Nanopool wallet address,
sending alerts when workers are reported to be 'offline' and when new workers
come online

## Install

```
pip install virtualenv
virtualenv env
source env/bin/activate
pip install slackclient
```

## Configure

### Slack

1. Create [a bot named `@redminebot`](https://my.slack.com/services/new/bot) and save the API token
 
 `export BOT_TOKEN="<slack api token>"`
 
2. Run the following Python script to get the bot's user ID for `BOT_ID`
 
 `python print_bot_id.py`

### Slackbot

1. Copy `run.sh.example` to `run.sh` 

 `cp run.sh.example run.sh`

2. Edit `run.sh` and fill in the following variables
```
export WALLET_ID="0xADDRESS"
export BOT_ID="<from print_bot_id.py>"
export BOT_TOKEN="<slack api token>"
```

## Running

```
bash run.sh
```
Recommended to use `supervisor` if you want a long running service that is fault tolerant

### Supervisord example conf

```
[program:nanopoolbot]
command=/opt/nanopoolbot/run.sh   ; the program (relative uses PATH, can take args)
numprocs=1                        ; number of processes copies to start (def 1)
directory=/opt/nanopoolbot        ; directory to cwd to before exec (def no cwd)
autostart=true                    ; start at supervisord start (default: true)
autorestart=true                  ; restart on exit
stopasgroup=true                  ; send stop signal to the UNIX process group (default false)
user=nanopoolbot                  ; setuid to this UNIX account to run the program
stderr_logfile=/var/log/nanopoolbot.err.log
stdout_logfile=/var/log/nanopoolbot.out.log
```

## Source

Thanks to https://www.fullstackpython.com/blog/build-first-slack-bot-python.html for the great starting point/guide
