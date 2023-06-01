from py2neo import Graph

class AnswerSearcher():
    def __init__(self):
        self.g=Graph("http://localhost:7474/",auth=("neo4j", "NEO4J"))
        self.num_limit=20

    #按照CQL查询返回结果
    def seacher_main(self,cqls):
        final_answers=[]
        if cqls:
            for cql in cqls:
                question_type=cql['question_types']
                queries=cql['cql']
                print(queries)
                answer=[]
                for query in queries:
                    ress=self.g.run(query).data()
                    answer += ress
                    print(answer)
                    final_answer=self.answer_prettify(question_type,answer)
                    if final_answer:
                        final_answers.append(final_answer)
        else:return None
        return final_answers
    #查询英文名对应的中文名和描述
    def EnglishNameParseCql(self,cypher):
        ress = self.g.run(cypher).data()
        return ress[0]
    #对结果进行处理
    def answer_prettify(self,question_type,answer):
        answer_list=[]
        if question_type=='mushroomClass_symptom':
            temp_answer = f"{answer[1]['m.name']}的{answer[1]['r.name']}为："
            for i in answer:
                temp_answer = temp_answer + i['s.name']+','
            answer_list.append(temp_answer)
        elif question_type=='mushroomClass_location':
            temp_answer = f"{answer[0]['m.name']}常{answer[0]['r.name']}在"
            for i in answer:
                temp_answer = temp_answer + i['l.name'] + ' '
            answer_list.append(temp_answer)
        elif question_type=='mushroomClass_edible':
            temp_answer = f"{answer[0]['m.name']}{answer[0]['e.name']}"
            answer_list.append(temp_answer)
        elif question_type=='mushroomClass_feature':
            temp_answer = f"{answer[0]['m.name']}{answer[0]['m.feature']}"
            answer_list.append(temp_answer)
        elif question_type=='mushroomClass_efficacy':
            temp_answer = f"{answer[0]['m.name']}的{answer[0]['r.name']}为："
            for i in answer:
                temp_answer = temp_answer + i['e.name'] + ','
            answer_list.append(temp_answer)
        elif question_type=='mushroomClass_account':
            temp_answer = f"{answer[0]['m.account']}"
            answer_list.append(temp_answer)
        elif question_type=='symptom_mushroomClass':
            temp_answer = f"出现{answer[0]['s.name']}的现象可能是误食了"
            for i in answer:
                temp_answer = temp_answer + i['m.name'] + ','
            answer_list.append(temp_answer)
        return answer_list



