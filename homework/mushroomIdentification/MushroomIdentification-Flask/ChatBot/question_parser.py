class QuestionParser:
#提取实体
    def build_entity_dict(self,args):
        entity_dict={'entity':[i for i in args]}
        return entity_dict

    def parser_main(self,res_classify):
        args = res_classify['args']
        entity_dict = self.build_entity_dict(args)
        question_types = res_classify['question_types']
        cyphers=[]
        for question_type in question_types:
            cypher_={}
            cypher_['question_types']=question_type
            cypher = self.cql_transfer(question_type, entity_dict.get('entity'))
            if cypher:
                cypher_['cql']=cypher
                cyphers.append(cypher_)
        return cyphers

    def cql_transfer(self,question_type,entities):
        if not entities:
            return []
        cql=[]
        if question_type =='mushroomClass_feature':
            cql = ["match (m:mushroomClass) where m.name='{0}' return m.name,m.feature".format(i) for i in entities]
        elif question_type =='mushroomClass_account':
            cql = ["match (m:mushroomClass) where m.name='{0}' return m.name,m.account".format(i) for i in entities]

        elif question_type =='mushroomClass_edible':
            cql = ["match (m:mushroomClass)-[r:edible]->(e:Edible) where m.name='{0}' return m.name,e.name".format(i) for i in entities]
        elif question_type =='mushroomClass_efficacy':
            cql = ["match (m:mushroomClass)-[r:efficacy]->(e:Efficacy) where m.name='{0}' return m.name,r.name,e.name".format(i) for i in entities]
        elif question_type =='mushroomClass_symptom':
            cql = ["match (m:mushroomClass)-[r:symptom]->(s:Symptom) where m.name='{0}' return m.name,r.name,s.name".format(i) for i in entities]
        elif question_type =='mushroomClass_location':
            cql = ["match (m:mushroomClass)-[r:location]->(l:Location) where m.name='{0}' return m.name,r.name,l.name".format(i) for i in entities]
        elif question_type =='symptom_mushroomClass':
            cql = ["match (m:mushroomClass)-[r:symptom]->(s:Symptom) where s.name='{0}' return m.name,s.name".format(i) for i in entities]
        return cql
