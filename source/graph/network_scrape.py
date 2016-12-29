import time
from math import ceil as ceiling
from twython import Twython
from graph.data_model import Node, Tag
import graph.filter_node
import neomodel


class NetworkScrape(object):
    """Documentation for NetworkScrape

    """
    def __init__(self, app_key, app_secret, oauth_token, oauth_token_secret):
        self.twitter = Twython(app_key, app_secret,
                               oauth_token, oauth_token_secret)
    
    def get_user(self, screen_name):
        try:
            instance = Node.create_from_response(self.twitter.lookup_user(screen_name=screen_name)[0])
            return instance
        except neomodel.exception.UniqueProperty:
            # user already exists, retrieve
            return Node.nodes.get(screen_name=screen_name)
    
    def pull_follow_network(self, user_object, limit):
        scope_depth = 200
        scope_limit = ceiling(limit / scope_depth)
        
        self.pull_remote_graph(user_object, user_object.followers,
                               scope_limit, scope_depth, self.twitter.get_followers_list)
    
    def pull_friend_network(self, user_object, limit):
        scope_depth = 200
        scope_limit = ceiling(limit / scope_depth)
        
        self.pull_remote_graph(user_object, user_object.friends,
                               scope_limit, scope_depth, self.twitter.get_friends_list)
    
    def pull_remote_graph(self, user_object, relationship,
                          scope_limit, scope_depth, twitter_function):
        next_cursor = -1
        while(next_cursor and scope_limit):
            scope_limit -= 1
            search = twitter_function(screen_name=user_object.screen_name,
                                      count=scope_depth, cursor=next_cursor)
            for result in search['users']:
                tmp = None
                try:
                    tmp = Node.create_from_response(result)
                except neomodel.exception.UniqueProperty:
                    # user already exists, retrieve
                    tmp = Node.nodes.get(screen_name=result['screen_name'])
                relationship.connect(tmp)
            next_cursor = search["next_cursor"]
            time.sleep(60)
    
    def filter_0(self, root_user, time_zone, disparity_tolerance):
        """Create a Tag (StructuredNode) which we will connect with Nodes that
        meet the criteria of the first filter. The first filter
        describes any nodes that are interesting to us, which nodes we
        will draw a sample network from for analysis.
        
        :param root_user: The root_user of the network to be analyzed
        :param time_zone: The time_zone we will filter against
        :returns: None
        :rtype: None
        
        """
        try:
            tag = Tag(name=Tag.FILTER_0).save()
        except neomodel.exception.UniqueProperty:
            print('Tag filter_0 already exists in database')
            tag = Tag.nodes.get(name=Tag.FILTER_0)
        
        for follower in root_user.followers:
            if graph.filter_node.filter_0(follower, time_zone, disparity_tolerance):
                tag.users.connect(follower)
    
    # def pull_remote_status(self, screen_name, scope_depth=200):
    #     user_object = self.session.query(Node).filter_by(screen_name=screen_name).first()
    #     if (user_object is None and len(user_object.statuses) > 0):
    #         return
        
    #     try:
    #         # We have recorded 0 Statuses previously for this user, therefore we can reasonably assume
    #         # An object of the same credentials does not exist in the database, also it is within a try/catch
    #         statuses = self.twitter.get_user_timeline(screen_name=screen_name, count=scope_depth)
    #         for status in statuses:
    #             user_object.statuses.append(Status(status))
    #     except:
    #         pass
        
    #     self.session.commit()
    #     time.sleep(7)
    
    # def filter_1(self, root_user):
    #     root_user_object = self.get_user_from_data_store(root_user)
    #     for node in root_user_object.pointer_nodes():
    #         if (node.filter_0):
    #             node.filter_1 = filter_1(node)
    #     self.session.commit()
        
    # def filter_2(self):
    #     for node in self.session.query(Node).all():
    #         node.filter_2 = filter_2(node)
    #     self.session.commit()


