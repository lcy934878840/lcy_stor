import os
import ahocorasick

class QuestionClassifier:
    def __init__(self):
        self.mushroomClass_path = os.path.join('D:\\PyCharm 2021.3\\MushroomIdentification\\mushroomClass')
        self.symptom_path = os.path.join('D:\PyCharm 2021.3\MushroomIdentification\symptom')
        #加载特征词
        self.mushroomClass_words=[i.strip() for i in open(self.mushroomClass_path,encoding='utf-8') if i.strip()]
        self.symptom_words = [i.strip() for i in open(self.symptom_path, encoding='utf-8') if i.strip()]
        #整合
        self.region_words = set(self.mushroomClass_words + self.symptom_words )
        #构造树模型，加快匹配效率
        self.region_tree=self.build_actree(list(self.region_words))
        #构造词典
        self.wdtype_dict = self.wdtype_dict()

        #问句疑问词
        self.edible_qwds = ['可以吃吗','有没有毒','能不能食用','可不可以食用','可不可以吃','能吃吗','能食用吗','采摘','食用','中毒','能不能吃','有毒']
        self.symptom_qwds = ['症状','误食','后果','影响','表现','表征','病症','坏处','导致','引起']
        self.location_qwds = ['分布','生长','地方','地区','省市','位置']
        self.feature_qwds = ['特点','特征','外貌','长什么样','形状','样子','样貌','外形','外观']
        self.efficacy_qwds = ['功效','作用','好处','变化','疗效','营养']

    #构建词典，也就是问题词属于那种类型
    def wdtype_dict(self):
        wd_dict=dict()
        for wd in self.region_words:
            wd_dict[wd]=[]
            if wd in self.mushroomClass_words:
                wd_dict[wd].append('mushroomClass')
            if wd in self.symptom_words:
                wd_dict[wd].append('symptom')
        return wd_dict

    def build_actree(self,wordlist):
        actree=ahocorasick.Automaton()
        for index,word in enumerate(wordlist):
            actree.add_word(word,(index,word))
        actree.make_automaton()
        return actree

    #问句过滤和返回词语属于什么类型
    def check_medical(self,sentence):
        region_words=[]
        for i in self.region_tree.iter(sentence):
            wd = i[1][1]
            region_words.append(wd)
        stop_word=[]
        for wd1 in region_words:
            for wd2 in region_words:
                if wd1 in wd2 and wd1 != wd2:
                    stop_word.append(wd1)
        final_words = [i for i in region_words if i not in stop_word]
        final_dict={i:self.wdtype_dict.get(i) for i in final_words}
        return final_dict
    #基于特征词分类
    def check_words(self,wds,sent):
        for wd in wds:
            if wd in sent:
                return True
        return False

    #分类主函数
    def classify(self,sentence):
        data = {}
        medical_dict=self.check_medical(sentence)
        if not medical_dict:
            return {}
        #实体类型
        data['args']=medical_dict
        #疑问类型
        types=[]
        for type_ in medical_dict.values():
            types += type_

        print("types:{}".format(types))

        question_types = []

        #实体-->特征
        if self.check_words(self.feature_qwds,sentence) and 'mushroomClass' in types:
            question_type='mushroomClass_feature'
            question_types.append(question_type)
        #实体-->地点
        if self.check_words(self.location_qwds,sentence) and 'mushroomClass' in types:
            question_type='mushroomClass_location'
            question_types.append(question_type)
        # 实体-->症状
        if self.check_words(self.symptom_qwds,sentence) and 'mushroomClass' in types:
            question_type='mushroomClass_symptom'
            question_types.append(question_type)
        # 症状-->实体
        if self.check_words(self.symptom_qwds, sentence) and 'symptom' in types:
             question_type = 'symptom_mushroomClass'
             question_types.append(question_type)
        #实体 -- >功效
        if self.check_words(self.efficacy_qwds,sentence) and 'mushroomClass' in types:
            question_type = 'mushroomClass_efficacy'
            question_types.append(question_type)
        #实体 -->食用性
        if self.check_words(self.edible_qwds,sentence) and 'mushroomClass' in types:
            question_type='mushroomClass_edible'
            question_types.append(question_type)

        #如果匹配不上，则默认返回account
        if len(question_types) ==0 :question_types.append('mushroomClass_account')
        #把question_types的所有内容返回到data字典
        data['question_types']=question_types
        return data








