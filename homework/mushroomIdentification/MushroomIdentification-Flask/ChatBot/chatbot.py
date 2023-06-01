from question_classifier import *
from answer_search import *
from question_parser import *


class ChatBotGraph:
    def __init__(self):
        self.classifier = QuestionClassifier()
        self.parser = QuestionParser()
        self.searcher = AnswerSearcher()

    def chat_main(self, sentence):
        answer = '对不起，我听不懂您的问题，请换一种说法！'
        res_classify = self.classifier.classify(sentence)
        if not res_classify:
            return answer
        print(res_classify)
        res_cql = self.parser.parser_main(res_classify)
        print(res_cql)
        return_answer = self.searcher.seacher_main(res_cql)
        if not return_answer:
            return answer
        else:
            final_answer = ''
            for sen in return_answer:
                final_answer += ''.join(sen) + '\n'
            return final_answer

    def EnglishNameSearchAccount(self, EnglishName):
        cypher =f"match (m:mushroomClass) - [r:edible]->(e:Edible) where m.EnglishName ='{EnglishName}' return m.name, " \
        f"m.feature, e.name, m.account "
        ress = self.searcher.EnglishNameParseCql(cypher)
        return {'name': ress['m.name'],
                'edible': ress['e.name'],
                'feature': ress['m.feature'],
                'account': ress['m.account']}



chatbot = ChatBotGraph()


def Chat(sentence):
    return chatbot.chat_main(sentence)


def EnglishNameSearchFor(EnglishName):
    return chatbot.EnglishNameSearchAccount(EnglishName)





