
from flask import request, jsonify
from db import get_db_connection

def save_section():
    print("yes")
    data = request.get_json()

    section_id = data.get('sectionId')
    section_number = data.get('sectionNumber')
    title = data.get('title')
    langID = data.get('languageID')
    is_premium = data.get('isPremium')
    if(is_premium == False):
        is_premium = 0
    else:
        is_premium = 1
    description = data.get('description')

    if not section_number or not title or not description:
         return jsonify({
            'isSuccess': False,
            'message': 'Saving Section Failed',
            'data': None,
            'data2': None,
            'totalCount': None
        }), 200
    conn = None
    cursor = None
    conn = get_db_connection()
    cursor = conn.cursor()
    if(section_id == 0 or section_id is None):

        query = "SELECT * FROM section WHERE sectionNumber = %s"
        cursor.execute(query, (section_number,))
        existing_section = cursor.fetchone()
        if existing_section:
            return jsonify({
                'isSuccess': False,
                'message': 'Section Number is already existing. Please select another section number.',
                'data': None,
                'data2': None,
                'totalCount': None
            }), 200
        
        query = """
        INSERT INTO section (sectionNumber, title, isPremium, description, languageID)
        VALUES (%s, %s, %s, %s, %s)
        """
        values = (section_number, title, is_premium, description, langID)
    else:
        query = "SELECT * FROM section WHERE sectionNumber = %s AND sectionId != %s"
        cursor.execute(query, (section_number, section_id))
        conflicting_section = cursor.fetchone()
        if conflicting_section:
            return jsonify({
                'isSuccess': False,
                'message': 'Section Number is already existing. Please select another section number.',
                'data': None,
                'data2': None,
                'totalCount': None
            }), 200
        
        query = """
        UPDATE section SET sectionNumber = %s, title = %s, isPremium = %s, description = %s WHERE sectionId = %s
        """
        values = (section_number, title, is_premium, description, section_id)

    cursor.execute(query, values)
    conn.commit()

    return jsonify({'isSuccess': True,"message": "Section saved successfully"}), 201

def get_Sections():
    langID = request.args.get('languageID')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM section WHERE languageID = %s and isActive = true"
    values = (langID,)
    cursor.execute(query, values)
    sections = cursor.fetchall()
    for section in sections:
        section['isPremium'] = bool(section['isPremium'])
    if not sections:
        return jsonify({
            'isSuccess': True,
            'message': 'No sections found',
            'data': [],
            'data2': None,
            'totalCount': 0
        }), 200
    return jsonify({
                'isSuccess': True,
                'message': 'Successfully Retrieved',
                'data': sections,
                'data2': None,
                'totalCount': None 
            }), 200

def get_Language():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM language"
    cursor.execute(query)
    languages = cursor.fetchall()
    if not languages:
        return jsonify({
            'isSuccess': True,
            'message': 'No sections found',
            'data': [],
            'data2': None,
            'totalCount': 0
        }), 200
    return jsonify({
                'isSuccess': True,
                'message': 'Successfully Retrieved',
                'data': languages,
                'data2': None,
                'totalCount': None 
            }), 200

def save_units():
    data = request.get_json()

    unitID = data.get('unitID')
    unitNumber = data.get('unitNumber')
    title = data.get('title')
    description = data.get('description')
    sectionID = data.get('sectionID')

    
    if not unitNumber or not title or not description:
        return jsonify({
            'isSuccess': False,
            'message': 'Saving Unit Failed',
            'data': None,
            'data2': None,
            'totalCount': None
        }), 200
        
    conn = get_db_connection()
    cursor = conn.cursor()

        
    if unitID == 0 or unitID is None:
        query = """
            INSERT INTO unit (unitNumber, title, description, sectionID, totalItems)
            VALUES (%s, %s, %s, %s, %s)
            """
        values = (unitNumber, title, description, sectionID, 0)
        cursor.execute(query, values)
        unitID = cursor.lastrowid  

            
        queryUsers = "SELECT userPlayerId FROM Vista"
        cursor.execute(queryUsers)
        users = cursor.fetchall()
        isLocked = True if unitNumber > 1 else False
  
        for user in users:
            userPlayerId = user[0]
            userUnitQuery = """
                    INSERT INTO userunit (userPlayerId, unitId, totalCorrectAnswers, totalScore, isLocked)
                    VALUES (%s, %s, %s, %s, %s)
                """
            userUnitValues = (userPlayerId, unitID, 0, 0, isLocked)             
            cursor.execute(userUnitQuery, userUnitValues)
    else:
            
        query = """
            UPDATE unit SET unitNumber = %s, title = %s, description = %s WHERE unitID = %s
            """
        values = (unitNumber, title, description, unitID)
        cursor.execute(query, values)

        
    conn.commit()
    return jsonify({'isSuccess': True, "message": "Unit saved successfully"}), 200

def get_Units():
    sectionID = request.args.get('sectionID')
    searchString = request.args.get('searchString')
    pageNo = int(request.args.get('pageNo', 1))
    pageSize = 15
    offset = (pageNo - 1) * pageSize
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT * FROM unit
        WHERE sectionID = %s and isActive = true
    """
    values = [sectionID]

    if searchString:
        query += "AND (title LIKE %s OR description LIKE %s)"
        likePattern = f"%{searchString}%"
        values.extend([likePattern, likePattern])
    
    query += """
        ORDER BY unitNumber
        LIMIT %s OFFSET %s
    """
    values.extend([pageSize, offset])

    cursor.execute(query, tuple(values))
    units = cursor.fetchall()
    count_query = "SELECT COUNT(*) as total FROM unit WHERE sectionID = %s"
    countvalues = [sectionID]
    if searchString:
        count_query += " AND (title LIKE %s OR  description LIKE %s)"
        likePattern = f"%{searchString}%"
        countvalues.extend([likePattern, likePattern])

    cursor.execute(count_query, tuple(countvalues))
    total_count = cursor.fetchone()['total']

    if not units:
        return jsonify({
            'isSuccess': True,
            'message': 'No units found',
            'data': [],
            'data2': None,
            'totalCount': 0
        }), 200
    return jsonify({
                'isSuccess': True,
                'message': 'Successfully Retrieved',
                'data': units,
                'data2': None,
                'totalCount': total_count
            }), 200

def sectionInactive():
    sectionID = int(request.args.get('sectionID')) 
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        UPDATE section SET isActive = false where sectionID = %s
    """
    values = [sectionID,]
    cursor.execute(query, values)
    conn.commit()
    return jsonify({'isSuccess': True, "message": "Content updated successfully"}), 200

def unitInactive():
    unitID = int(request.args.get('unitID')) 
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query_update = """
        UPDATE unit SET isActive = false WHERE unitID = %s
    """
    values = [unitID,]
    cursor.execute(query_update, values)

    query_delete = """
        DELETE FROM userUnit WHERE unitID = %s
    """
    cursor.execute(query_delete, values)

    conn.commit()

    return jsonify({'isSuccess': True, "message": "Content updated and userUnit records deleted successfully"}), 200