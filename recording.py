from flask import request, jsonify
from db import get_db_connection
import random
from setup import upload_media

def save_content():
    content_id = int(request.form.get('contentId', 0))
    content_name = request.form.get('contentName', 'default_name').replace(' ', '_')
    
    audio_file = request.files.get('audioFile')
    if audio_file:
        result = upload_media(audio_file)
        path = result
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            INSERT INTO fileData (contentId, filePath, isAccepted, fileName) VALUES (%s, %s, %s, %s)
        """
        values = [content_id, path, 0, path]
        cursor.execute(query, values)
        conn.commit()
        return jsonify({'isSuccess': True, "message": "Content saved successfully"}), 200
    else:
        return jsonify({'isSuccess': False, "message": "No audio file provided"}), 400


def get_contents():
    searchString = request.args.get('searchString')
    pageNo = int(request.args.get('pageNo', 1))
    languageId = request.args.get('languageId')
    pageSize = 15
    offset = (pageNo - 1) * pageSize
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT fd.*, c.contentText
        FROM fileData fd inner join content c on c.contentID = fd.contentID where fd.isAccepted = 0 and fd.isRejected = 0
        AND c.languageID = %s
    """
    values = [languageId,]

    if searchString:
        query += " AND (c.contentText LIKE %s)"
        likePattern = f"%{searchString}%"
        values.extend([likePattern])
    print(query)
    query += """
        ORDER BY fd.Id DESC
        LIMIT %s OFFSET %s
    """
    values.extend([pageSize, offset])
  
    cursor.execute(query, tuple(values))
    contents = cursor.fetchall()
    
    return jsonify({
        'isSuccess': True,
        'message': 'Successfully retrieved reports',
        'data': contents,
        'totalCount': None
    }), 200
    
def acceptRecording():
    fileId = int(request.args.get('fileId')) 
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    update_query = "UPDATE fileData SET isAccepted = 1 WHERE id = %s"
    cursor.execute(update_query, (fileId,))
    conn.commit()
        
    return jsonify({'isSuccess': True, 'message': 'Report updated successfully'}), 200

def rejectRecording():
    fileId = int(request.args.get('fileId')) 
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    
    update_query = "UPDATE fileData SET isRejected = 1 WHERE id = %s"
    cursor.execute(update_query, (fileId,))
    conn.commit()
        

    return jsonify({'isSuccess': True, 'message': 'Report updated successfully'}), 200
