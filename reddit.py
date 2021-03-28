import requests
import json
import logging
from random import randint

logger = logging.getLogger(__name__)


class Post:
    def __init__(self, title: str, url: str, image_url: str, text: str):
        self.title = title
        self.url = url
        self.is_photo = image_url != None
        self.image_url = image_url
        self.text = text


class Subreddit:
    def __init__(self, name: str):
        self.name = name
        self.posts = []

    def parse(self) -> None:
        req = requests.get(f"https://reddit.com/r/{self.name}.json", headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.105 Safari/537.36'})
        data = req.json()

        if 'data' not in data.keys():
            msg = data['message'] if 'message' in data.keys() else f'Couldn\'t parse {self.name} for an unknown error. Status code {req.status_code}' 
            raise Exception(msg)

        for c in data['data']['children']:
            # Skip pinned posts
            c = c['data']

            if c['stickied'] or c['is_video']:
                continue

            post = Post(
                title=c['title'],
                url=c['url'],
                text=c['selftext'],
                image_url=c.get('url_overridden_by_dest')
            )

            self.posts.append(post)


class Reddit:
    def __init__(self) -> None:
        self.posts = {}
        self.config = json.load(open('config.json', 'r'))
        self.parse_posts()        

    def parse_posts(self) -> None:
        logger.info(f'Parsing {len(self.config["subreddits"])} subreddits')

        for s in self.config['subreddits']:
            self.parse_subreddit(
                Subreddit(s)
            )
    
    def update_config(self, subreddit: Subreddit, add: bool):
        if add:
            self.config['subreddits'].append(subreddit.name)
        else:
            self.config['subreddits'].remove(subreddit.name)

        with open('config.json', 'w') as w:
            json.dump(self.config, w, indent=4)

    def add_subreddit(self, subreddit: Subreddit) -> bool:
        self.parse_subreddit(subreddit)

        # Adds a subreddit if it is not in the config, but the parse was succesful
        if subreddit.name not in self.config['subreddits'] and self.posts.get(subreddit.name):
            self.update_config(subreddit, True)
            
            return True

    def remove_subreddit(self, subreddit: Subreddit) -> bool:
        if subreddit.name in self.config['subreddits']:
            self.update_config(subreddit, False)

            return True

    def parse_subreddit(self, subreddit: Subreddit) -> None:
        try:
            subreddit.parse()
            emoji = '✔️' if subreddit.posts else '❌'
            logger.info(f'{subreddit.name} {emoji}')

            self.posts[subreddit.name] = subreddit.posts
        except Exception as err:
            logger.error(err)

    def get_post(self, subreddit: Subreddit) -> Post:
        # Parse a subreddit if it's empty and the key exists
        if subreddit.name in self.posts.keys() and not self.posts[subreddit.name]: 
            self.parse_subreddit(subreddit)
        elif subreddit.name not in self.posts.keys():
            return logger.error(f'There is no such subreddit saved as {subreddit.name}')

        # Take one post out of the list
        return self.posts[subreddit.name].pop()