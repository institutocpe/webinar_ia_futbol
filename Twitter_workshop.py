import tweepy
import pandas as pd
from textblob import TextBlob
import re
from textblob import exceptions

class Twitter_workshop():
    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret ):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.data = ""

    def buscar_tweets(self, query):
        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)
        api = tweepy.API(auth, wait_on_rate_limit = True)

        tweets = tweepy.Cursor(api.search_tweets,
                    q=query,
                    lang="es").items(10)

        tweets_list = []
        for tweet in tweets:
            tweets_list.append(tweet)

        tweets_df = pd.DataFrame()

        for tweet in range(0,len(tweets_list)):
            tweets_df = tweets_df.append(pd.DataFrame({'user_name': tweets_list[tweet].user.name, 
                                                    'user_location': tweets_list[tweet].user.location,
                                                    'date': tweets_list[tweet].created_at,
                                                    'text': tweets_list[tweet].text,
                                                    'retweet' : tweets_list[tweet].retweet_count,
                                                    'likes' : tweets_list[tweet].favorite_count
                                                    }, index = [0]))
            tweets_df = tweets_df.reset_index(drop=True)
        self.data = tweets_df
        return self.data

    def first_step(self,doc):
            doc = re.sub("["u"\U0001F600-\U0001F64F""]",'',doc) 
            doc = re.sub("["u"\U0001F300-\U0001F5FF""]",'',doc) 
            doc = re.sub("["u"\U0001F680-\U0001F6FF""]",'',doc) 
            doc = re.sub("["u"\U0001F1E0-\U0001F1FF""]",'',doc) 
            doc = re.sub('@[A-Za-z0–9_]+','',doc) 
            doc = re.sub('RT[\s]+','',doc)        
            doc = re.sub('#','',doc)              
            doc = re.sub('https?:\/\/\S+','',doc) 
            doc = re.sub('&amp;','y',doc)       
            doc = re.sub(' +',' ',doc)            
            doc = re.sub("[\(\[].*?[\)\]]","",doc)  
            doc = re.sub("\n"," ", doc)             
            doc = re.sub("^[^A-Za-z0–9]+","",doc)    
            doc = doc.strip()                       
            doc = doc.lower()  
            return doc

    def limpiar_tweets(self):
        self.data["text"] = self.data["text"].apply(self.first_step)
        return self.data    

    def analisis_sentimiento(self):
        col_translated = []
        sentimientos = []
        l = 0
        for c in self.data.text:
            try:
                blob = TextBlob(c).translate(from_lang = "es", to="en")
                sentimientos.append(blob.sentiment.polarity)
            except exceptions.NotTranslated:
                col_translated.append("sin_traduccion")
                sentimientos.append("sin_traduccion")
        df_sentiment = pd.concat([self.data.date, self.data.text, self.data.likes, self.data.retweet, pd.Series(sentimientos, name = "polarity")], axis = 1)
        return df_sentiment