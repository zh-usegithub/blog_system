#小学春游 - 两组同学，每组1-3人，每组有一个队长;春游期间，由于景点人数较多，秩序混乱，班主任要求在指定地点，按组集合

#源数据
s = [{'name':'leader-1','belong_to':None},{'name':'jack','belong_to':'leader-2'},{'name':'lili','belong_to':'leader-1'},{'name':'leader-2','belong_to':None},{'name':'Tom', 'belong_to':'leader-1'}]
#目标数据
d = [
    {'name':'leader-1', 'team':[{'name':'lili'},{'name':'Tom'}]},
    {'name':'leader-2', 'team':[{'name':'jack'}]}
]

def find_team(data):

    leader_lst = []
    s_dict = {}   #{'leader-1':[{'name':'lili'}]}
    for d in data:
        if d['belong_to']:
            #队员
            s_dict.setdefault(d['belong_to'],[])#这是字典的新方法，如果字典中有这个d['belong_to']键，那么不执行这句，如果没有这个键，则插入键值对
            s_dict[d['belong_to']].append({'name':d['name']})
        else:
            #队长
            leader_lst.append({'name':d['name'], 'team':[]})

    for l in leader_lst:
        if l['name'] in s_dict:
            l['team'] = s_dict[l['name']]

    return leader_lst

print(find_team(s))
#[{'name': 'leader-1', 'team': [{'name': 'lili'}, {'name': 'Tom'}]}, {'name': 'leader-2', 'team': [{'name': 'jack'}]}]








