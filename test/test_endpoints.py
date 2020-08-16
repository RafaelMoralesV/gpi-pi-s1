import unittest
from io import StringIO, FileIO
from requests_toolbelt import sessions
from requests import Response


class EndpointTest(unittest.TestCase):

    base_url = "http://127.0.0.1:5000" 

    client = sessions.BaseUrlSession(base_url="http://127.0.0.1:5000")

    endpoints = {
        "reddit" : {
            "user" : "reddit/user",
            "subreddit": "reddit/subreddit"
        },
        "twitter":{
            "user": "twitter/user",
            "hashtags": "twitter/hashtags"
        }
    }

class QuickTest(EndpointTest):

    def test_get_reddit_default_users(self):
        response = self.client.get(self.endpoints["reddit"]["user"]) 
        obj = response.json()
        self.assertNotEqual(obj["n_entries"], 0) 

    def test_get_reddit_multiple_users(self):
        users = ["joeyisgoingto"]
        for user in users:
            res: Response = self.client.get(self.endpoints["reddit"]["user"] + f"/{user}")
            self.assertEqual(res.status_code, 200, f"Consulta por {user} fallida")
            obj = res.json()
            self.assertNotEqual(obj["n_entries"], 0, f"Consulta por {user} sin entradas")

    def test_tweets_id_type(self):
        response = self.client.get(self.endpoints["twitter"]["user"])
        obj = response.json()
        for user in obj["users"]:
            [self.check_tweet_id_type(tw) for tw in user["tweets"]] 

        response = self.client.get(self.endpoints["twitter"]["hashtags"])
        obj = response.json()
        for hashtag in obj["hashtags"]:
            [self.check_tweet_id_type(tw) for tw in hashtag["tweets"]] 

    def check_tweet_id_type(self, tweet: dict):
        self.assertTrue(type(tweet["id"]) == str)


class PostTest(EndpointTest):
  
    input_file: FileIO

    def setUp(self):
        self.input_file = open("./data/small.xlsx", "rb")

    def test_post_reddit_users_file(self):
        files = {"plantilla" : self.input_file}
        res : Response = self.client.post(self.endpoints["reddit"]["user"], files=files)
        self.assertEqual(res.status_code, 200)
        obj = res.json()
        self.assertNotEqual(obj["n_entries"], 0, "Sin entradas")
    
    def test_post_reddit_subreddits_file(self):
        files = {"plantilla" : self.input_file}
        res : Response = self.client.post(self.endpoints["reddit"]["subreddit"], files=files)
        self.assertEqual(res.status_code, 200)
        obj = res.json()
        self.assertNotEqual(obj["n_entries"], 0, "Sin entradas")

    def test_post_twitter_users_file(self):
        files = {"plantilla" : self.input_file}
        res : Response = self.client.post(self.endpoints["twitter"]["user"], files=files)
        self.assertEqual(res.status_code, 200)
        obj = res.json()
        self.assertNotEqual(obj["n_entries"], 0, "Sin entradas")

    def test_post_twitter_hashtags_file(self):
        files = {"plantilla" : self.input_file}
        res : Response = self.client.post(self.endpoints["twitter"]["hashtags"], files=files)
        self.assertEqual(res.status_code, 200)
        obj = res.json()
        self.assertNotEqual(obj["n_entries"], 0, "Sin entradas")

if __name__ == "__main__":
    unittest.main(verbosity=3)
