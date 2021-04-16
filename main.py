import requests
import config
from twilio.rest import Client

STOCK_NAME = "GME"
COMPANY_NAME = "GameStop Corp."

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

# Access API keys without disclosing keys
STOCK_API_KEY = config.STOCK_API_KEY
NEWS_API_KEY = config.NEWS_API_KEY
TWILIO_SID = config.TWILIO_SID
TWILIO_TOKEN = config.TWILIO_TOKEN


# Set required parameters for the API call using a dictionary
stock_params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK_NAME,
    "apikey": STOCK_API_KEY,
}

# Send HTTP request to API endpoint and capture in a new variable called response
# Return exception using the method from requests
response = requests.get(url=STOCK_ENDPOINT, params=stock_params)
response.raise_for_status()
data = response.json()["Time Series (Daily)"]
# List comprehension allows us to traverse the JSON to get yesterday's closing stock price
data_list = [value for (key, value) in data.items()]
yesterday_data = data_list[0]
yesterday_price = yesterday_data["4. close"]

# Get the day before yesterday's closing stock price
day_before_data = data_list[1]
day_before_price = day_before_data["4. close"]

# Get the absolute value between yesterday's closing price and the day before yesterday's
# Calculate percent difference
pos_diff = abs(float(yesterday_price) - float(day_before_price))
percent_incr = pos_diff / float(yesterday_price) * 100

# Add emojis to message depending on increase or decrease in change
if float(yesterday_price) - float(day_before_price) > 0:
    direction_change = "👍😊"
else:
    direction_change = "👎😪"


# List first 3 articles using list comprehension
# If percent difference is larger than 0.5% send a message
news_params = {
    "apiKey": NEWS_API_KEY,
    "qInTitle": COMPANY_NAME,
}

if percent_incr > 0.5:
    response = requests.get(url=NEWS_ENDPOINT, params=news_params)
    response.raise_for_status()
    related_news = response.json()["articles"]
    # Using a Python slice operator, we can grab the first 3 news articles from the list
    # https://stackoverflow.com/questions/509211/understanding-slice-notation
    top_three_news = related_news[0:3]
    news_list = [f"{STOCK_NAME}: {direction_change}{round(percent_incr)}% \nTitle: {article['title']}. \nDescription: {article['description']}" for article in top_three_news]

# Send 3 articles as a separate message through Twilio
account_sid = TWILIO_SID
auth_token = TWILIO_TOKEN

client = Client(account_sid, auth_token)

for article in news_list:
    message = client.messages.create(
        to=config.YOUR_PRIVATE_NUM,
        from_=config.YOUR_TWILIO_NUM,
        body=article
    )


## Notes
# Originally captured yesterday's date using datetime and use f strings to convert to string format
# today = date.today()
# yesterday = f"{today - timedelta(days=1)}"
# day_before = f"{today - timedelta(days=2)}"
# This does not work every day of the week because stocks are only traded on a weekday, so Saturday/Sunday
# get left out. A better way is to use list comprehension to create a list from the JSON dictionary and then traverse
# that list
