import json
from twitter import Twitter, OAuth, TwitterHTTPError, TwitterStream
from SoteraWatchmanTest_authorization import ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET

oauth = OAuth(ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET)
twitter_stream = TwitterStream(auth=oauth)
iterator = twitter_stream.statuses.sample()

tweet_count = 1000
print("[")
for tweet in iterator:
    spacer = ""
    tweet_count -= 1
    # Twitter Python Tool wraps the data returned by Twitter 
    # as a TwitterDictResponse object.
    # We convert it back to the JSON format to print/score
    if "quoted_status" in tweet:
        if "entities" in tweet["quoted_status"]:
            if "media" in tweet["quoted_status"]["entities"]:
                spacer = ","
                print(json.dumps(tweet, indent=4))
    
    if tweet_count <= 0:
        break 
    else:
        if len(spacer) > 0:
            print(spacer)

print("]")
