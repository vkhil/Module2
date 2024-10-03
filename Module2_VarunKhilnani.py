import tweepy
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import time

# Set up Twitter API credentials
api_key = 'your_api_key'
api_secret = 'your_api_secret'
access_token = 'your_access_token'
access_token_secret = 'your_access_token_secret'

# Authenticate to Twitter API
auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

# Function to get retweet network for a specific tweet with data cleaning
def get_retweet_network(tweet_id):
    G = nx.DiGraph()  # Create a directed graph
    try:
        retweets = api.retweets(tweet_id, count=100)
        for retweet in retweets:
            user = retweet.user.screen_name
            retweeted_user = retweet.retweeted_status.user.screen_name
            
            # Avoid self-loops (users retweeting themselves, which is rare but possible)
            if user != retweeted_user:
                G.add_edge(user, retweeted_user)  # Directed edge from retweeter to original poster
        
        # Remove duplicate edges (NetworkX takes care of this, but double-checking for clarity)
        G = nx.DiGraph(G)
        
    except tweepy.TweepError as e:
        print(f"Error fetching retweets: {e}")
    
    return G

# Example tweet ID (replace with your tweet ID)
tweet_id = 'your_target_tweet_id'

# Create the retweet network
G = get_retweet_network(tweet_id)

# Ensure the graph is not empty
if G.number_of_nodes() == 0:
    print("No data collected, the graph is empty. Check the tweet ID or data source.")
else:
    # Calculate centrality measures
    degree_centrality = nx.degree_centrality(G)
    betweenness_centrality = nx.betweenness_centrality(G)
    pagerank = nx.pagerank(G)

    # Handle missing data: Removing nodes that have missing centrality measures
    users_with_complete_data = set(degree_centrality.keys()) & set(betweenness_centrality.keys()) & set(pagerank.keys())
    
    degree_centrality = {user: degree_centrality[user] for user in users_with_complete_data}
    betweenness_centrality = {user: betweenness_centrality[user] for user in users_with_complete_data}
    pagerank = {user: pagerank[user] for user in users_with_complete_data}

    # Get top 3 users for each centrality measure for labeling purposes
    top_users = list(degree_centrality.keys())[:3]

    # Prepare actual data for graphing based on real results
    degree_centrality_values = [degree_centrality[user] for user in top_users]
    betweenness_centrality_values = [betweenness_centrality[user] for user in top_users]
    pagerank_values = [pagerank[user] for user in top_users]

    # Create a bar chart for centrality measures
    def plot_centrality_distribution():
        x = np.arange(len(top_users))  # the label locations
        width = 0.25  # the width of the bars

        # Create the figure and the axes
        fig, ax = plt.subplots()

        # Create the bars for each centrality measure
        rects1 = ax.bar(x - width, degree_centrality_values, width, label='Degree Centrality')
        rects2 = ax.bar(x, betweenness_centrality_values, width, label='Betweenness Centrality')
        rects3 = ax.bar(x + width, pagerank_values, width, label='PageRank')

        # Add labels, title, and custom x-axis tick labels
        ax.set_xlabel('User')
        ax.set_ylabel('Centrality Measure')
        ax.set_title('Centrality Measures for Top Influencers')
        ax.set_xticks(x)
        ax.set_xticklabels(top_users)
        ax.legend()

        # Display the figure
        plt.tight_layout()
        plt.show()

    plot_centrality_distribution()

    # Create the graph for the other two statistics (Betweenness and PageRank)
    def plot_betweenness_pagerank():
        fig, ax = plt.subplots()

        # Create the bars for Betweenness Centrality and PageRank
        rects1 = ax.bar(x - width / 2, betweenness_centrality_values, width, label='Betweenness Centrality')
        rects2 = ax.bar(x + width / 2, pagerank_values, width, label='PageRank')

        # Add labels, title, and custom x-axis tick labels
        ax.set_xlabel('User')
        ax.set_ylabel('Centrality Measure')
        ax.set_title('Betweenness Centrality and PageRank for Top Influencers')
        ax.set_xticks(x)
        ax.set_xticklabels(top_users)
        ax.legend()

        # Display the figure
        plt.tight_layout()
        plt.show()

    plot_betweenness_pagerank()

