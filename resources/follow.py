from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql.connector.errors import Error
import mysql.connector
from mysql_connection import get_connection


class FollowResource(Resource) :

    @jwt_required()
    def post(self) :
        data = request.get_json()

        follower_id = get_jwt_identity()

        try :
            connection = get_connection()

            # {
            #     "follower_id" : "1",
            #     "followee_id" : "2"
            # }

            # 팔로우하기 전에 사용자가가 존재 하는지 확인

            query = '''select * from user
                        where id in (%s, %s)'''
            
            record = (follower_id, data['followee_id'])
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)

            result_list = cursor.fetchall()

            user = result_list
            #print(user)

            if len(user) != 2 :
                
                cursor.close()
                connection.close()
                return {"error" : "없는 사용자를 팔로우할 수 없습니다."}

            # 이미 팔로우한 사람은 할 수 없도록 설정
            query = '''select * from follow
                        where follower_id = %s and followee_id = %s'''
            
            record = (follower_id, data['followee_id'])

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)

            result_list = cursor.fetchall()

            follow = result_list
            print(follow)

            if len(follow) == 1 :
                
                cursor.close()
                connection.close()
                return {"error" : "이미 팔로우를 했습니다."}


            query = '''insert into follow
                        (follower_id, followee_id)
                        values
                        (%s, %s);'''
            
            record = (follower_id, data['followee_id'])

            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()
            cursor.close()
            connection.close()
        
        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error" : str(e)}, 503

        return {"result" : "success"}

        
    @jwt_required()
    def get(self) :
        
        try : 
            connection = get_connection()

            follower_id = get_jwt_identity()

    
            query = '''select m.user_id, m.title, m.date, m.content
                        from memo m
                        join follow f
                            on m.user_id = f.followee_id
                            where f.follower_id=%s;'''
            record = (follower_id, )

            cursor = connection.cursor(dictionary = True)

            cursor.execute(query, record)

            # select 문은 아래 함수를 이용해서 데이터를 가져온다.
            result_list = cursor.fetchall()
            #print(result_list)

            # 중요! 디비에서 가져온 timestamp는
            # 파이썬의 datatime으로 자동 변경된다.
            # 문제는 ! 이제이터를 json으로 바로 보낼 수 없으므로 
            # 문자열로 바꿔서 다시 저장해서 보낸다.
             
            i=0
            for record in result_list :
                result_list[i]['date'] = record['date'].isoformat()
                i = i + 1   

            cursor.close()
            connection.close()
            print(result_list)
            
        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return { "error" : str(e) }, 503

        return {"result" : "success","result_list" : result_list}, 200