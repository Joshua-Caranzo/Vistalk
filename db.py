import mysql.connector
import cloudinary

def get_db_connection():
	return mysql.connector.connect(
		host="junction.proxy.rlwy.net",  # Proxy URL
        	port=52006,
		user="root",
		password="lTaYNRCJEpAYudgSYAGFkDXIXMDvFPmp",
		database="railway",
	)

HOST = '192.168.1.13'
PORT = 5000
DEBUG = True

SECRET_KEY='8807c2bfe813ec02b9178d3c5826118894f3cd01e5d1630555f03d64ee42e655'
CLOUDINARY_URL='cloudinary://232339977941922:Ngx09hHe4FAkKNHoBnwGGILYf4E@due4hbbar'
