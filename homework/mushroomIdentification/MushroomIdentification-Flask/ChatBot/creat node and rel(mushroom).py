import json
import os
from py2neo import Graph, Node

g = Graph("http://localhost:7474/", auth=("neo4j", "NEO4J"))

file = os.path.join('a')
files = open(file, encoding='utf-8')
json_data = json.loads(files.read())

# 定义节点
mushroomClass = []  # 蘑菇种类
location = []  # 分布地方
symptom = []  # 误食症状
efficacy = []  # 功效
edible = []  # 是否可食用

# 定义关系
mushroomClass_rel_location = []  # 蘑菇分布地
mushroomClass_rel_symptoms = []  # 蘑菇误食症状
mushroomClass_rel_edible = []  # 蘑菇是否可以食用
mushroomClass_rel_efficacy = []  # 蘑菇功效
# 设置存放所有节点属性信息的list
mushroomClassInfo = []

for data in json_data:
    name = data['name']
    mushroomClass.append(name)
    mushroomDict = {'name': name, 'EnglishName': '', 'feature': '', 'account': ''}
    # 添加关系节点
    if 'edible' in data:
        edible += data['edible']
        for e in data['edible']:
            mushroomClass_rel_edible.append([name, e])

    if 'location' in data:
        location += data['location']
        for loc in data['location']:
            mushroomClass_rel_location.append([name, loc])

    if 'symptom' in data:
        symptom += data['symptom']
        for sym in data['symptom']:
            mushroomClass_rel_symptoms.append([name, sym])

    if 'efficacy' in data:
        efficacy += data['efficacy']
        for efi in data['efficacy']:
            mushroomClass_rel_efficacy.append([name, efi])
    # 添加节点属性
    if 'EnglishName' in data:
        mushroomDict['EnglishName'] = data['EnglishName']

    if 'feature' in data:
        mushroomDict['feature'] = data['feature']

    if 'account' in data:
        mushroomDict['account'] = data['account']

    # 信息存入
    mushroomClassInfo.append(mushroomDict)
print(mushroomClass_rel_symptoms)
# 创建蘑菇实体节点
for mushroomdic in mushroomClassInfo:
    node = Node("mushroomClass", name=mushroomdic['name'], EnglishName=mushroomdic['EnglishName'],
                feature=mushroomdic['feature'], account=mushroomdic['account'])
    g.create(node)


# 创建其他节点
def creat_node(label, nodes):
    for node_name in set(nodes):
        node_ = Node(label, name=node_name)
        g.create(node_)


creat_node('Edible', edible)
creat_node('Location', location)
creat_node('Symptom', symptom)
creat_node('Efficacy', efficacy)


# 创建边
def creat_relationship(star_node, end_node, edges, rel_type, rel_name):
    #去重处理
    set_edges = []
    for edge in edges:
        set_edges.append('###'.join(edge))
    for edge in set(set_edges):
        edge = edge.split('###')
        Cypher = "match(E:%s),(R:%s) where E.name='%s' and R.name='%s' create (E)-[rel:%s{name:'%s'}]->(R)" % (
            star_node, end_node, edge[0], edge[1], rel_type, rel_name
        )
        try:
            g.run(Cypher)
        except:
            print('Error')
            
creat_relationship('mushroomClass','Edible',mushroomClass_rel_edible,'edible','是否可食用')
creat_relationship('mushroomClass','Location',mushroomClass_rel_location,'location','分布')
creat_relationship('mushroomClass','Symptom',mushroomClass_rel_symptoms,'symptom','误食症状')
creat_relationship('mushroomClass','Efficacy',mushroomClass_rel_efficacy,'efficacy','功效')
