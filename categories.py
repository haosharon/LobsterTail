categories = '''
afghanistan: 1149
africa: 1126
analysis: 1059
animals: 1132
architecture: 1142
around the nation: 1091
art and design: 1047
arts and life: 1008
asia: 1125
author interviews: 1033
book reviews: 1034
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