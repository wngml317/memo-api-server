from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql.connector.errors import Error
import mysql.connector
from mysql_connection import get_connection


class FollowListResource(Resource) :
        
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

class FollowResource(Resource) :
    
    @jwt_required()
    def post(self, follow_id) :

        # 1. 클라이언트로부터 데이터를 받아온다.
        user_id = get_jwt_identity()

        # 2. 데이터베이스에 친구정보 인서트한다.
        try :
            # 1) 디비에 연결
            connection = get_connection()

            # 팔로우하기 전에 사용자가가 존재 하는지 확인

            query = '''select * from user
                        where id in (%s, %s)'''
            
            record = (user_id, follow_id)
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
            
            record = (user_id, follow_id)

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)

            result_list = cursor.fetchall()

            follow = result_list
            print(follow)

            if len(follow) == 1 :
                
                cursor.close()
                connection.close()
                return {"error" : "이미 팔로우를 했습니다."}

            # 2) 쿼리문 만들기
            query = '''insert into follow
                        (follower_id, followee_id)
                        values
                        (%s, %s);'''
            
            record = (user_id, follow_id)

            # 3) 커서를 가져온다.
            cursor = connection.cursor()

            # 4) 쿼리문을 커서를 이용하여 실행
            cursor.execute(query, record)

            # 5) 커넥션을 커밋해준다. -> 디비에 영구적으로 반영
            connection.commit()

            # 6) 자원 해제
            cursor.close()
        
        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error" : str(e)}, 503

        return {"result" : "success"}


    @jwt_required()
    def delete(self, follow_id) :
        
        user_id = get_jwt_identity()
        try :
            connection = get_connection()    

            query = '''delete from follow
                        where follower_id = %s and followee_id=%s;'''
            record = (user_id, follow_id)

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
        return {'result' : 'success'}, 200
