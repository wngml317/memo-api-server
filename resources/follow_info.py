from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql.connector.errors import Error
import mysql.connector
from mysql_connection import get_connection


class FolloweeResource(Resource) :
    

    @jwt_required()
    def delete(self, followee_id) :
        
        follower_id = get_jwt_identity()
        try :
            connection = get_connection()    

            query = '''delete from follow
                        where follower_id = %s and followee_id=%s;'''
            record = (follower_id, followee_id)

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
