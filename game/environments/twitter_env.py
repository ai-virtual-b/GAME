from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio
from game.core.environment import Environment
import tweepy

class TwitterEnv(Environment):
    """Twitter environment for LLM agent interaction with Twitter API"""
    
    def __init__(self, 
                 bearer_token: str,
                 api_key: str = None,
                 api_key_secret: str = None,
                 cache_duration: int = 60):  # Cache duration in seconds
        """
        Initialize Twitter environment
        
        Args:
            bearer_token: Twitter API Bearer Token
            cache_duration: How long to cache state data in seconds
        """
        self.client = tweepy.Client(
            bearer_token=bearer_token, 
            consumer_key=api_key,
            consumer_secret=api_key_secret,
            wait_on_rate_limit=True)
        
        # Cache management
        self._cache = {}
        self._cache_timestamp = None
        self.cache_duration = cache_duration
        
        # Initialize state descriptions for LLM
        state_descriptions = {
            "follower_count": {
                "description": "Number of followers the account has",
                "type": "integer",
                "example": 1234
            },
            "following_count": {
                "description": "Number of accounts being followed",
                "type": "integer",
                "example": 567
            },
            "tweet_count": {
                "description": "Total number of tweets posted by the account",
                "type": "integer",
                "example": 789
            },
            "recent_mentions": {
                "description": "List of 5 most recent mentions/interactions",
                "type": "array",
                "example": [{"username": "user1", "text": "Hello!"}]
            },
            "account_age_days": {
                "description": "Age of the Twitter account in days",
                "type": "integer",
                "example": 365
            },
            "engagement_rate": {
                "description": "Average engagement rate on recent tweets (likes + retweets / followers) as percentage",
                "type": "number",
                "example": 2.5
            },
            "recent_hashtags": {
                "description": "Most used hashtags in recent tweets",
                "type": "array",
                "example": ["#AI", "#Tech"]
            }
        }
        
        world_description = """
        Twitter social media environment for monitoring and interacting with Twitter.
        The agent can:
        - Track followers, following, and tweet counts
        - Monitor recent mentions and interactions
        - Track engagement rates and hashtag usage
        - Post tweets and monitor account performance
        
        Note: Actions follow Twitter's rate limits and terms of service.
        """
        
        super().__init__(state_descriptions, world_description)
        self.state_descriptions = state_descriptions
        self.world_description = world_description

    def get_state(self) -> Dict[str, Any]:
        """Get current state of the Twitter environment"""
        current_time = datetime.now()
        
        # Return cached state if valid
        if (self._cache_timestamp and 
            current_time - self._cache_timestamp < timedelta(seconds=self.cache_duration) and 
            self._cache):
            return self._cache
        
        try:
            # Get user information (assuming we know the user ID)
            print("here")
            user = self.client.get_me()
            print(user)
            # Get recent tweets
            tweets = self.client.get_users_tweets(
                user.data.id,
                max_results=20,
                tweet_fields=['public_metrics', 'created_at']
            )
            
            # Calculate engagement rate
            if tweets.data and user.data.public_metrics['followers_count'] > 0:
                total_engagement = sum(
                    tweet.public_metrics['like_count'] + tweet.public_metrics['retweet_count']
                    for tweet in tweets.data
                )
                avg_engagement = total_engagement / len(tweets.data)
                engagement_rate = (avg_engagement / user.data.public_metrics['followers_count']) * 100
            else:
                engagement_rate = 0.0
                
            # Get recent mentions
            mentions = self.client.get_users_mentions(
                user.data.id,
                max_results=5,
                tweet_fields=['created_at']
            )
            mentions_data = []
            if mentions.data:
                mentions_data = [
                    {
                        'username': mention.author_id,  # You might want to get user details separately
                        'text': mention.text,
                        'created_at': mention.created_at.isoformat()
                    }
                    for mention in mentions.data
                ]
            
            # Extract hashtags from recent tweets
            hashtags = []
            if tweets.data:
                for tweet in tweets.data:
                    if 'entities' in tweet and 'hashtags' in tweet.entities:
                        hashtags.extend([h['tag'] for h in tweet.entities['hashtags']])
            top_hashtags = sorted(set(hashtags), key=hashtags.count, reverse=True)[:5]
            
            # Calculate account age
            account_age = (datetime.now() - user.data.created_at).days
            
            state = {
                "follower_count": user.data.public_metrics['followers_count'],
                "following_count": user.data.public_metrics['following_count'],
                "tweet_count": user.data.public_metrics['tweet_count'],
                "recent_mentions": mentions_data,
                "account_age_days": account_age,
                "engagement_rate": round(engagement_rate, 2),
                "recent_hashtags": top_hashtags
            }
            
            self._cache = state
            self._cache_timestamp = current_time
            
            return state
            
        except Exception as e:
            print(f"Error fetching Twitter state: {str(e)}")
            return self._cache if self._cache else {
                "error": "Failed to fetch Twitter state",
                "error_message": str(e)
            }

    def get_state_descriptions(self) -> Dict[str, Dict[str, Any]]:
        """Return descriptions of all state variables for prompts"""
        return self.state_descriptions

    def get_world_description(self) -> str:
        """Get world description for prompts"""
        return self.world_description

    def get_user_timeline(self, 
                        username: str, 
                        max_results: int = 10) -> List[Dict[str, Any]]:
        """Get timeline for specified user"""
        try:
            # First get user ID from username
            user = self.client.get_user(username=username)
            if not user.data:
                return []
                
            tweets = self.client.get_users_tweets(
                user.data.id,
                max_results=max_results,
                tweet_fields=['public_metrics', 'created_at']
            )
            
            if not tweets.data:
                return []
                
            return [{
                'id': tweet.id,
                'text': tweet.text,
                'likes': tweet.public_metrics['like_count'],
                'retweets': tweet.public_metrics['retweet_count']
            } for tweet in tweets.data]
        except Exception as e:
            print(f"Error fetching user timeline: {str(e)}")
            return []