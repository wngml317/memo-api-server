from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql.connector.errors import Error
import mysql.connector
from mysql_connection import get_connection


class MemoListResource(Resource) :
    
    @jwt_required()
    def post(self) :
        # {
        #     "title" : "오전 미팅 주제",
        #     "date" : "2022-01-22",
        #     "content" : "클라우드"
        # }

        data = request.get_json()

        user_id = get_jwt_identity()

        try :
            connection = get_connection()

            query = '''insert into memo
                        (title, date, content, user_id)
                        values
                        (%s, %s, %s, %s);'''
            
            record = (data['title'], data['date'], data['content'], user_id)

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
                
        return {"result" : "success"}, 200

    def get(self) :

        offset = request.args.get('offset')
        limit = request.args.get('limit')

        try :
            connection = get_connection()

            query = '''select * from memo
                        limit {}, {}'''.format(offset, limit)

            # select 문은 dictionary=True 를 해준다.
            cursor = connection.cursor(dictionary = True)

            cursor.execute(query)

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
