categories = '''
food: 1053
health: 1128
business: 1006
art: 1047
politics: 1014
sports: 1055
world: 10004
u.s.: 1003
movies: 1045
technology: 1019
science: 1007
economy: 1017
'''

def create():
    dic = {}
    cat = categories.split('\n')
    for c in cat:
        i = c.rfind(':')
        if i + 1 < len(c):
            topic = c[:i].strip()
            topic_id = c[i + 1:].strip()
            dic[topic] = topic_id
    return dic

def get_id(topic):
    # returns the mapping id of the topic
    dic = create()
    topic = topic.strip().lower()
    if dic[topic]:
        return dic[topic]