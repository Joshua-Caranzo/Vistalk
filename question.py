# user.py
from db import get_db_connection
from flask import request, jsonify
import uuid
from setup import upload_media

def get_QuestionTypes():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM questiontype order by typeName"
    cursor.execute(query)
    questionTypes = cursor.fetchall()
    if not questionTypes:
        return jsonify({
            'isSuccess': True,
            'message': 'No types found',
            'data': [],
            'data2': None,
            'totalCount': 0
        }), 200
    return jsonify({
                'isSuccess': True,
                'message': 'Successfully Retrieved',
                'data': questionTypes,
                'data2': None,
                'totalCount': None 
            }), 200

def get_choices():
    langID = request.args.get('languageID')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT * FROM content where languageID = %s and isActive = 1
    """
    values = [langID,]

    cursor.execute(query, tuple(values))
    contents = cursor.fetchall()
    count_query = "SELECT COUNT(*) as total FROM content WHERE languageID = %s"
    countvalues = [langID]
    cursor.execute(count_query, tuple(countvalues))
    total_count = cursor.fetchone()['total']

    if not contents:
        return jsonify({
            'isSuccess': True,
            'message': 'No contents found',
            'data': [],
            'data2': None,
            'totalCount': 0
        }), 200
    return jsonify({
                'isSuccess': True,
                'message': 'Successfully Retrieved',
                'data': contents,
                'data2': None,
                'totalCount': total_count
            }), 200

def get_Questions():
    unitId = request.args.get('unitId')
    searchString = request.args.get('searchString')
    pageNo = int(request.args.get('pageNo', 1))
    pageSize = 15
    offset = (pageNo - 1) * pageSize
    conn = get_db_connection()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT 
            q.*,
            qt.typeName 
        FROM 
            question q
        INNER JOIN 
            questiontype qt 
        ON 
            q.questionTypeID = qt.typeID
        WHERE 
            q.unitId = %s
            AND q.isActive = true
    """
    values = [unitId]

    if searchString:
        query += "AND (questionText LIKE %s OR questionTypeID LIKE %s)"
        likePattern = f"%{searchString}%"
        values.extend([likePattern, likePattern])

    query += """
        ORDER BY questionTypeID
        LIMIT %s OFFSET %s
    """
    values.extend([pageSize, offset])

    cursor.execute(query, tuple(values))
    quesions = cursor.fetchall()

    count_query = "SELECT COUNT(*) as total FROM question WHERE unitId = %s AND isActive = true"
    countvalues = [unitId]
    if searchString:
        count_query += " AND (questionText LIKE %s OR questionTypeID LIKE %s)"
        likePattern = f"%{searchString}%"
        countvalues.extend([likePattern, likePattern])

    cursor.execute(count_query, tuple(countvalues))
    total_count = cursor.fetchone()['total']

    if not quesions:
        return jsonify({
            'isSuccess': True,
            'message': 'No contents found',
            'data': [],
            'data2': None,
            'totalCount': 0
        }), 200
    
    return jsonify({
        'isSuccess': True,
        'message': 'Successfully Retrieved',
        'data': quesions,
        'data2': None,
        'totalCount': total_count
    }), 200

def save_questionMultiple():
    data = request.form
    question_ID = data.get('questionID', 0, type=int)
    question_text = data.get('questionText')
    unit_id = data.get('unitId', type=int)
    questionTypeID = data.get('questionTypeID', type=int)
    
    choices = [
        data.get('choice1', type=int),
        data.get('choice2', type=int),
        data.get('choice3', type=int),
        data.get('choice4', type=int)
    ]
    
    correct_choice = data.get('correctChoice', type=int)
    image_path = data.get('imagePath')
    audio_path = data.get('audioPath')

    conn = get_db_connection()
    cursor = conn.cursor()

    if question_ID == 0 or question_ID is None:
        query = """INSERT INTO question (questionText, unitId, questionTypeID) VALUES (%s, %s, %s)"""
        values = (question_text, unit_id, questionTypeID)
        cursor.execute(query, values)
        conn.commit()
        question_id = cursor.lastrowid

        query_update = """
        UPDATE unit 
        SET totalItems = totalItems + 1
        WHERE unitID = %s
        """
        values_update = (unit_id,)
        cursor.execute(query_update, values_update)
        conn.commit()

        file = request.files.get('file')

        if file:
            if image_path or audio_path:

                if image_path:
                    result = upload_media(file)
                    audio_path = result
                    cursor.execute('UPDATE question SET imagePath = %s WHERE questionId = %s', (audio_path, question_id))
                elif audio_path:
                    result = upload_media(file)
                    audio_path = result
                    cursor.execute('UPDATE question SET audioPath = %s WHERE questionId = %s', (audio_path, question_id))

        cursor.execute(
            '''
            INSERT INTO questionchoice (questionID, choice1, choice2, choice3, choice4, correctChoice)
            VALUES (%s, %s, %s, %s, %s, %s)
            ''',
            (question_id, *choices, correct_choice)
        )
        conn.commit()
    else:
        query = """UPDATE question SET questionText = %s, unitId = %s WHERE questionID = %s"""
        values = (question_text, unit_id, question_ID)
        cursor.execute(query, values)
        conn.commit()

        cursor.execute(
            """
            UPDATE questionchoice 
            SET choice1 = %s, choice2 = %s, choice3 = %s, choice4 = %s, correctChoice = %s 
            WHERE questionID = %s
            """,
            (*choices, correct_choice, question_ID)
        )
        conn.commit()

        file = request.files.get('file')

        if file:
            if image_path or audio_path:

                if image_path:
                    result = upload_media(file)
                    audio_path = result
                    cursor.execute('UPDATE question SET imagePath = %s, audioPath = null WHERE questionId = %s', (audio_path, question_ID))
                elif audio_path:
                    result = upload_media(file)
                    audio_path = result
                    cursor.execute('UPDATE question SET audioPath = %s, imagePath = null WHERE questionId = %s', (audio_path, question_ID))
            conn.commit()


    conn.close()
    return jsonify({'message': 'Question and choices saved successfully.'}), 200


def get_multiple_choice():
    questionID = request.args.get('questionID')
    print(questionID)
    conn = get_db_connection()
    cursor = conn.cursor(dictionary = True)
    query = """
        SELECT * FROM questionchoice WHERE questionID = %s
    """
    values = [questionID]
    cursor.execute(query, tuple(values))
    multiple_choices = cursor.fetchone()
    print(multiple_choices)
    count_query = "SELECT COUNT(*) as total FROM questionchoice WHERE questionID = %s"
    countvalues = [questionID]

    cursor.execute(count_query, tuple(countvalues))
    total_count = cursor.fetchone()['total']

    if not multiple_choices:
        return jsonify({
            'isSuccess': True,
            'message': 'No contents found',
            'data': [],
            'data2': None,
            'totalCount': 0
        }), 200
    return jsonify({
                'isSuccess': True,
                'message': 'Successfully Retrieved',
                'data': multiple_choices,
                'data2': None,
                'totalCount': total_count
            }), 200
  
def get_matching_type():
    questionMatchingTypeID = request.args.get('questionMatchingTypeID')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary = True)
    query = """
        SELECT * FROM questionmatchingtype WHERE questionID = %s
    """
    cursor.execute(query, [questionMatchingTypeID,])
    matching_type = cursor.fetchone()

    if not matching_type:
        return jsonify({
            'isSuccess': True,
            'message': 'No contents found',
            'data': [],
            'data2': None,
            'totalCount': 0
        }), 200
    return jsonify({
                'isSuccess': True,
                'message': 'Successfully Retrieved',
                'data': matching_type,
                'data2': None,
                'totalCount': 1
            }), 200

def save_question_match():
    data = request.json

    question_text = data.get('questionText')
    print(question_text)
    unit_id = data.get('unitId')
    question_type_id = data.get('questionTypeID')
    questionMatchingTypeId = data.get('questionMatchingTypeID')
    choices = [
        data.get('word1'),
        data.get('word2'),
        data.get('word3'),
        data.get('word4'),
        data.get('match1'),
        data.get('match2'),
        data.get('match3'),
        data.get('match4')
    ]

    conn = get_db_connection()
    cursor = conn.cursor()
    if questionMatchingTypeId == 0 or questionMatchingTypeId == None:
        cursor.execute(
            '''
            INSERT INTO question (questionText, unitId, questionTypeID)
            VALUES (%s, %s, %s)
            ''',
            (question_text, unit_id, question_type_id)
        )

        conn.commit()
        question_id = cursor.lastrowid
        query_update = """
            UPDATE unit 
            SET totalItems = totalItems + 1
            WHERE unitID = %s
            """
        values_update = (unit_id,)
        cursor.execute(query_update, values_update)
        conn.commit()

        cursor.execute(
            '''
            INSERT INTO questionmatchingtype (questionID, word1, word2, word3, word4, match1, match2, match3, match4)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''',
            (question_id, choices[0], choices[1], choices[2], choices[3], choices[4], choices[5], choices[6], choices[7])
        )
        
        conn.commit()
        conn.close()
    
    else:
        cursor.execute(
            '''
            SELECT questionID FROM questionmatchingtype 
            WHERE questionMatchingTypeID = %s
            ''',
            (questionMatchingTypeId,)
        )

        result = cursor.fetchone()
        question_id = result[0]
        cursor.execute(
            '''
            UPDATE question
            SET questionText = %s
            WHERE questionID = %s
            ''',
            (question_text, question_id)
        )
                
        cursor.execute(
            '''
            UPDATE questionmatchingtype
            SET word1 = %s, word2 = %s, word3 = %s, word4 = %s, match1 = %s, match2 = %s, match3 = %s, match4 = %s
            WHERE questionID = %s AND questionMatchingTypeID = %s
            ''',
            (choices[0], choices[1], choices[2], choices[3], choices[4], choices[5], choices[6], choices[7], question_id, questionMatchingTypeId)
        )

        conn.commit()
        conn.close()
    return jsonify({'message': 'Question and choices saved successfully.'}), 200

def questionInactive():
    questionID = int(request.args.get('questionID'))
    unit_id = int(request.args.get('unitID'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        UPDATE question SET isActive = false where questionID = %s
    """
    values = [questionID,]
    cursor.execute(query, values)
    conn.commit()

    query_update = """
        UPDATE unit 
        SET totalItems = totalItems - 1
        WHERE unitID = %s
        """
    values_update = (unit_id,)
    cursor.execute(query_update, values_update)
    conn.commit()

    return jsonify({'isSuccess': True, "message": "Content updated successfully"}), 200
