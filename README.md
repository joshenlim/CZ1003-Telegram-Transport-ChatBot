# Dora - Telegram Bot
Dora is a one-stop bot to quickly retrieve taxi fare estimations and make comparisons all on one convenient single platform. You no longer have to open multiple applications on your mobile phone before coming to a decision! Taxi companies currently in the list of comparisons include Uber, Grab and ComfortDelGro.

## APIs Integrated
  * Google Places Distance Matrix
  * Google Places Autocomplete
  * Google Places
  * TaxiFareFinder Fare Estimate
  * Uber Fare Estimate

## Commands
  * /taxi - Compare prices across taxi companies by inputting your pick up and drop off location
  * /cancel - Cancel the current action
  * /help - Show a list of available commands

## Quick Start (Locally)
  1. Navigate into the directory via the terminal using <code>cd PATH/TO/FOLDER</code>
  2. Create a <code>config.py</code> using <code>sampleconfig.py</code> as a template. Be sure to have created your own bot via The Botfather and input your own bot API key.
  3. Run <code>python3 telegramBot.py</code> to initiate server
  4. Start conversing with your own bot

## Test Cases
Below are example inputs to achieve the corresponding test cases, where you'll see how Dora responds accordingly.
### 1. Successful Flow
  * Pick Up location: 'ntu tanjong hall'
  * Drop Off location: 'jurong point'
  * Result: Fare estimates retrieved and comparisons displayed

### 2. Location not found
  * Typo cases: 'ntu tanjong hal', 'pungol centrl'
  * Result: Bot will prompt user to re-input location


### 3. Same location input
  * Pick Up location: '192 Punggol Central'
  * Drop Off location: '192 Punggol Central'
  * Result: Bot will alert user of an invalid pick up and drop off location set, and suggest user to try the entire flow again.

### 4. Undefined land route
  * Pick Up location: 'Pulau Tekong'
  * Drop Off location: 'Pulau Ubin'
  * Result: Bot will alert user of an invalid pick up and drop off location set, and suggest user to try the entire flow again.

## Example Input Flow
  * User: '/taxi'
  * Dora: 'Gotcha! Where would you like to be picked up from?'
  * User: 'NTU Tanjong Hall of Residence'
  * Dora: 'Sweet! I found these locations! Which would you like your <b>pick up</b> point to be?' (Select location from up to 5 options)
  * Dora: 'Now where would you like to be dropped off at?'
  * User: 'Jurong Point'
  * Dora: 'Gotcha! I found these locations! Which would you like your <b>drop off</b> point to be?' (Select location from up to 5 options)
  * Dora: 'Gotcha! Retrieving prices...'
  * Dora: 'Here are the estimated prices to travel from NTU Tanjong Hall of Residence to Jurong Point from the various taxi companies!'
  * Dora: 'Feel free to type '/taxi' again to retrieve more fare comparisons! :)'

  PLEASE WRITE DOWN FOR FAIL CASES TOO HOrh
