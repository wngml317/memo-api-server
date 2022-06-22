from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql.connector.errors import Error
import mysql.connector
from mysql_connection import get_connection


class MemoListResource(Resource) :
    
    @jwt_required()
    def post(self) :
        # 1. 클라이언트로 부터 데이터를 받아온다.
        # {
        #     "title" : "오전 미팅 주제",
        #     "date" : "2022-01-22",
        #     "content" : "클라우드"
        # }

        data = request.get_json()

        user_id = get_jwt_identity()

        try :
            # 2. 메모를 데이터베이스에 저장
            # 1) DB에 연결
            connection = get_connection()

            # 2) 쿼리문 만들기
            query = '''insert into memo
                        (title, date, content, user_id)
                        values
                        (%s, %s, %s, %s);'''
            
            record = (data['title'], data['date'], data['content'], user_id)

            # 3) 커서를 가져온다.
            cursor = connection.cursor()

            # 4) 쿼리문을 커서를 이용하여 실행
            cursor.execute(query, record)

            # 5) 커넥션을 커밋해준다. -> 디비에 영구적으로 반영
            connection.commit()

            # 5-1) 디비에 저장된 아이디값 가져오기
            user_id = cursor.lastrowid

            # 6) 자원 해제
            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error" : str(e)}, 503
                
        return {"result" : "success"}, 200

    @jwt_required()
    def get(self) :

        # 1. 클라이언트로부터 데이터를 받아온다.
        # request.args는 딕셔너리이다.
        offset = request.args.get('offset')
        limit = request.args.get('limit')

        user_id = get_jwt_identity()

        # 2. 디비로부터 내 메모를 가져온다.
        try :
            connection = get_connection()

            query = '''select * from memo
                        where user_id = %s
                        limit {}, {}'''.format(offset, limit)

            record = (user_id, )

            # select 문은 dictionary=True 를 해준다.
            cursor = connection.cursor(dictionary = True)

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

        return { "result" : "success", 
                "count" : len(result_list) ,
                "result_list" : result_list }, 200


class MemoInfoResource(Resource) :

    @jwt_required()
    def put(self, memo_id) :
        # 1. 클라이언트로부터 데이터를 받아온다.
        # {
        #     "title" : "운동",
        #     "date" : "2022-01-28",
        #     "content" : "한시간동안 운동하기"
        # }
        
        data = request.get_json()

        user_id = get_jwt_identity()

        # 2. 디비 업데이트 실행코드
        try :
            # 1. DB에 연결
            connection = get_connection()

            # 2. 쿼리문 만들기
            query = '''select user_id
                        from memo
                        where id = %s'''
                
            record = (memo_id, )

            cursor = connection.cursor(dictionary = True)

            cursor.execute(query, record)

            result_list = cursor.fetchall()

            memo = result_list[0]
            print(memo)

            if memo['user_id'] != user_id :
                cursor.close()
                connection.close()
                return {"error" : "다른 사람의 메모를 수정할 수 없습니다."}

            query = '''update memo
                    set title = %s , date = %s, content = %s
                    where id = %s and user_id = %s;'''
            
            record = (data['title'], data['date'], data['content'], memo_id, user_id)

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

            memo = result_list[0]

            if memo['user_id'] != user_id :
                cursor.close()
                connection.close()
                return {"error" : "다른 사람의 메모를 삭제할 수 없습니다."}

            query = '''delete from memo
                    where id=%s and user_id = %s;'''
            record = (memo_id, user_id)

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

        
