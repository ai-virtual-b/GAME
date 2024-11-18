from game.environments.twitter_env import TwitterEnv


twitter_env = TwitterEnv(bearer_token="AAAAAAAAAAAAAAAAAAAAAETrtAEAAAAA9SD5ltAJweWDLKRyR%2FZFGnYtJQQ%3DZvgtnK8M6rnlNcczBZqrGbAZBgmudyF4FRWWtXcnttJCcHueyo")

# Get current state
state = twitter_env.get_state()
print(state)
# Get trending topics
trends = twitter_env.get_user_timeline(username="luna_virtuals", max_results=5)
print(trends)