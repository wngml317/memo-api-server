from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql.connector.errors import Error
import mysql.connector
from mysql_connection import get_connection


class MemoResource(Resource) :
    def get(self, memo_id) :
        try :
            connection = get_connection()
            
            query = '''select *
                        from memo
                        where id=%s'''
            
            record = (memo_id, )

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)

            result_list = cursor.fetchall()
            print(result_list)

            i = 0 
            for record in result_list :
                result_list[i]['date'] = record['date'].isoformat()
                result_list[i]['created_at'] = record['created_at'].isoformat()
                result_list[i]['updated_at'] = record['updated_at'].isoformat()
                i = i + 1

            cursor.close()
            connection.close()
        
        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()

            return { "error" : str(e) }, 503

        return {'result' : 'success',
                'info' : result_list[0]}

    @jwt_required()
    def put(self, memo_id) :
        # {
        #     "title" : "운동",
        #     "date" : "2022-01-28",
        #     "content" : "한시간동안 운동하기"
        # }
        
        data = request.get_json()

        user_id = get_jwt_identity()

        # 디비 업데이트 실행코드
        try :
            # 데이터 insert
            # 1. DB에 연결
            connection = get_connection()

            ### memo_id에 들어있는 user_id가 
            ### 이 사람인지 먼저 확인한다.

            query = '''select user_id
                        from memo
                        where id = %s'''
                
            record = (memo_id, )

            cursor = connection.cursor(dictionary = True)

            cursor.execute(query, record)

            result_list = cursor.fetchall()

            recipe = result_list[0]

            if recipe['user_id'] != user_id :
                cursor.close()
                connection.close()
                return {"error" : "다른 사람의 메모를 수정할 수 없습니다."}

            query = '''update memo
                    set title = %s , date = %s, content = %s
                    where id = %s;'''
            
            record = (data['title'], data['date'], data['content'], memo_id)

            # 3. 커서를 가져온다.
            cursor = connection.cursor()

            # 4. 쿼리문을 커서를 이용해서 실행한다
            cursor.execute(query, record)

            # 5. 커넥션을 커밋해줘야 한다. => 디비에 영구적으로 반영하라는 뜻
            connection.commit()

            # 6. 자원 해제
            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error" : str(e)}, 503

        return {'result' : 'success'}, 200

    @jwt_required()
    def delete(self, memo_id) :

        user_id = get_jwt_identity()
        try :
            connection = get_connection()

            ### memo_id에 들어있는 user_id가 
            ### 이 사람인지 먼저 확인한다.

            query = '''select user_id
                        from memo
                        where id = %s'''
                
            record = (memo_id, )

            cursor = connection.cursor(dictionary = True)

            cursor.execute(query, record)

            result_list = cursor.fetchall()

            recipe = result_list[0]

            if recipe['user_id'] != user_id :
                cursor.close()
                connection.close()
                return {"error" : "다른 사람의 메모를 삭제할 수 없습니다."}

            query = '''delete from memo
                    where id=%s;'''
            record = (memo_id, )

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

        