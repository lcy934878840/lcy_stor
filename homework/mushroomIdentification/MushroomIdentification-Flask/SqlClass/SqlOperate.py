from datetime import datetime

import pymysql


class SqlClass():
    def __init__(self):
        self.con = pymysql.connect(host='localhost', password='123456', port=3306, user='root', charset='utf8',
                                   db='user')
        self.cur = self.con.cursor()

    def Register(self, name, phone, password):
        global FLAG
        self.cur.execute(f'select phone from register where phone = "{phone}";')
        if self.cur.fetchall():
            FLAG = '请勿重复注册'
            return FLAG
        else:
            try:
                FLAG = '注册成功'
                registerSQL = f"insert into register values ('{name}',{phone},{password});"
                self.cur.execute(registerSQL)
                self.con.commit()
            except Exception:
                FLAG = '注册失败'
            finally:
                return FLAG

    def Login(self, phone, password):
        loginSQL = f"select phone,password from register where phone = {phone} and password = {password}"

        self.cur.execute(loginSQL)

        if (phone, password) in self.cur.fetchall():
            state = True
        else:
            state = False
        return state

    def AddPredictedData(self, dataId, type, base64Content, time, mushroom='none', confidence=0.0):
        global FLAG
        try:
            FLAG = True
            print(mushroom)
            insertSQL = f"insert into history values('{dataId}', '{type}','{base64Content}','{time}','{mushroom}','{confidence}')"

            self.cur.execute(insertSQL)

            self.con.commit()
        except Exception as e:
            print(e)
            FLAG = False

        finally:
            return FLAG

    def AddMushroomMsg(self, MsgList):
        try:
            # 先判断该菌是否存在
            ExistSql = f"select mushroomclass from mushroom where mushroomclass = '{MsgList['name']}';"
            self.cur.execute(ExistSql)
            if self.cur.fetchall():
                return False
            else:
                InsertSql = f"insert into mushroom(mushroomclass, edible, feature, description) values ('{MsgList['name']}','{MsgList['edible']}','{MsgList['feature']}','{MsgList['account']}') ;"
                self.cur.execute(InsertSql)
                self.con.commit()
        except pymysql.Error as e:
            print(e)
            self.con.rollback()
            return True

    def FetchPredictedData(self, phone):


        fetchImgSQL = f'select u.*,h.datatype,h.datacontent,h.datatime,h.confidence,m.* ' \
                      f'from userhistory u,history h,mushroom m ' \
                      f'where u.dataid = h.dataid ' \
                      f'and h.mushroomclass = m.mushroomclass ' \
                      f'and u.phone = "{phone}"' \
                      f'order by datatime;'

        self.cur.execute(fetchImgSQL)

        queryResult = self.cur.fetchall()
        if queryResult:
            resultTitle = tuple(t[0] for t in self.cur.description)

            resultList = [dict(zip(resultTitle, item)) for item in queryResult]

            for i in resultList:
                i['datacontent'] = i['datacontent'].decode()
                i['datatime'] = i['datatime'].strftime('%Y-%m-%d %H:%M:%S')

            return resultList
        else:
            return False

    def DeleteData(self, DeleteDataList):
        try:
            for dataid in DeleteDataList:
                deleteSQL = 'delete from userhistory where dataid = %s;'
                self.cur.execute(deleteSQL, dataid)
            self.con.commit()
            return '删除成功'
        except pymysql.Error as e:
            print(e)
            self.con.rollback()
            return '删除失败'


sq = SqlClass()

sq.DeleteData(['1888888888820230601110342'])