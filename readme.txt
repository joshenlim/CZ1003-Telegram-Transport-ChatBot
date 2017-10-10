DORA FARE ESTIMATION TELEGRAM BOT
------------------------------------------

We are live as well on: https://github.com/joshenlim/cz1003-telegram-transport

For a more wholesome overview of this repository, do check out our README.md

Main Files for the Telegram Bot:
------------------------------------------
1. `telegramBot.py` - Main Bot file
2. `config.py` - Stores the IDs, keys and tokens for APIs
3. `comfort.py` - Returns the fare estimate of ComfortDelGro via an API
4. `grab.py` - Returns the fare estimate of Grab via an arithmetic algorithm according to Grab's fare structure
5. `uber.py` - Returns the fare estimate of Uber via an API
6. `distance.py` - Returns the road distance estimate between two selected locations via Google's Distance Matrix API
7. `requirements.txt` - Lists the required python libraries for this project


Other files within the folder:
------------------------------------------
1. .gitignore - Dictates what files to ignore when pushing up to the Git Repository (config.py, for security purposes)
2. sampleconfig.py - A sample config file for anyone to fill their own credentials, to be renamed as config.py
3. README.md - README file for the Git Repository
