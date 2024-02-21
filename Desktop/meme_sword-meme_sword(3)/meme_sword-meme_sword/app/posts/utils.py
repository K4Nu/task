from app.models import Vote_Like

def get_net_votes(comment_id):
    upvotes=Vote_Like.query.filter_by(comment_id=comment_id,type="up").count()
    downvotes=Vote_Like.query.filter_by(comment_id=comment_id,type="down").count()
    return upvotes-downvotes

def utility_processor():
    return dict(get_net_votes=get_net_votes)