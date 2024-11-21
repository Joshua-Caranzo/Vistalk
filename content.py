
from flask import request, jsonify
from db import get_db_connection
from setup import upload_media

def get_ContentTypes():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM contenttype"
    cursor.execute(query)
    contentTypes = cursor.fetchall()
    if not contentTypes:
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
                'data': contentTypes,
                'data2': None,
                'totalCount': None 
            }), 200

def save_content():
    content_id = int(request.form.get('contentId', 0))
    content_text = request.form.get('contentText')
    english_translation = request.form.get('englishTranslation')
    language_id = int(request.form.get('languageId'))
    content_type_id = int(request.form.get('contentTypeId'))
    forPronunciation = request.form.get('forPronunciation')
    if(forPronunciation == 'false'):
            forPronunciation = 0
    else:
            forPronunciation = 1
            
    is_indictionary = request.form.get('isInDictionary')
    if(is_indictionary == 'false'):
            is_indictionary = 0
    else:
            is_indictionary = 1

    audio_file = request.files.get('contentAudioFile')
    audio_path = request.form.get('audioPath')
    if audio_file:
        result = upload_media(audio_file)
        audio_path = result

    syllables_data = []
    index = 0
    while True:
        syllable_content_id = request.form.get(f'syllables[{index}].contentId')
        if syllable_content_id is None:
            break
        syllable = {
            'id': int(request.form.get(f'syllables[{index}].id')),
            'contentId': int(syllable_content_id),
            'syllableText': request.form.get(f'syllables[{index}].syllableText'),
            'audioPath': request.form.get(f'syllables[{index}].syllableText'),
            'orderNumber': int(request.form.get(f'syllables[{index}].orderNumber')),
        }
        syllable_audio_file = request.files.get(f'syllables[{index}].audioFile')
        syllable['audioPath'] = request.form.get(f'syllables[{index}].audioPath')

        if syllable_audio_file:
            result = upload_media(syllable_audio_file)
            syllable_audio_path = result
            syllable['audioPath'] = syllable_audio_path
        syllables_data.append(syllable)
        index += 1

    definitions_data = []
    index = 0
    while True:
        definition_content_id = request.form.get(f'definitions[{index}].contentId')
        if definition_content_id is None:
            break
        definition = {
            'id': int(request.form.get(f'definitions[{index}].id')),
            'contentId': int(definition_content_id),
            'nativeDefinition': request.form.get(f'definitions[{index}].nativeDefinition'),
            'englishDefinition': request.form.get(f'definitions[{index}].englishDefinition'),
            'orderNumber': int(request.form.get(f'definitions[{index}].orderNumber')),
        }
        definitions_data.append(definition)
        index += 1

    examples_data = []
    index = 0
    while True:
        example_content_id = request.form.get(f'examples[{index}].contentId')
        if example_content_id is None:
            break
        example = {
            'id': int(request.form.get(f'examples[{index}].id')),
            'contentId': int(example_content_id),
            'nativeExample': request.form.get(f'examples[{index}].nativeExample'),
            'englishExample': request.form.get(f'examples[{index}].englishExample'),
            'orderNumber': int(request.form.get(f'examples[{index}].orderNumber')),
        }
        examples_data.append(example)
        index += 1

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if content_id == 0:
            sql_content = """
                INSERT INTO content (contentText, englishTranslation, audioPath, languageId, contentTypeId, isInDictionary, forPronunciation)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql_content, (
                content_text,
                english_translation,
                audio_path,
                language_id,
                content_type_id,
                is_indictionary,
                forPronunciation
            ))
            conn.commit()
            content_id = cursor.lastrowid

            
            for syllable in syllables_data:
                sql_syllable = """
                    INSERT INTO contentsyllable (contentId, syllableText, audioPath, orderNumber)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(sql_syllable, (
                    content_id,
                    syllable['syllableText'],
                    syllable['audioPath'],
                    syllable['orderNumber']
                ))
                conn.commit()

            
            for definition in definitions_data:
                sql_definition = """
                    INSERT INTO contentdefinition (contentId, nativeDefinition, englishDefinition, orderNumber)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(sql_definition, (
                    content_id,
                    definition['nativeDefinition'],
                    definition['englishDefinition'],
                    definition['orderNumber']
                ))
                conn.commit()

            
            for example in examples_data:
                sql_example = """
                    INSERT INTO contentexample (contentId, nativeExample, englishExample, orderNumber)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(sql_example, (
                    content_id,
                    example['nativeExample'],
                    example['englishExample'],
                    example['orderNumber']
                ))
                conn.commit()

        else:
            sql_update_content = """
                UPDATE content
                SET contentText = %s, englishTranslation = %s, audioPath = %s, languageId = %s, contentTypeId = %s, isInDictionary = %s, forPronunciation = %s
                WHERE contentId = %s
            """
            
            cursor.execute(sql_update_content, (
                content_text,
                english_translation,
                audio_path,
                language_id,
                content_type_id,
                is_indictionary,
                forPronunciation,
                content_id
            ))
            
            conn.commit()

            
            existing_syllables = {syllable['id'] for syllable in syllables_data}
            cursor.execute("SELECT * FROM contentsyllable WHERE contentId = %s", (content_id,))
            stored_syllables = set()
            rows = cursor.fetchall()

            for row in rows:
                try:
                    stored_syllables.add(row[0])                
                except Exception as e:
                    print(f"Error adding row to stored_syllables: {e}")

            for syllable in syllables_data:
                if syllable['id'] in stored_syllables:
                    sql_update_syllable = """
                        UPDATE contentsyllable
                        SET syllableText = %s, audioPath = %s, orderNumber = %s
                        WHERE id = %s
                    """
                    cursor.execute(sql_update_syllable, (
                        syllable['syllableText'],
                        syllable['audioPath'],
                        syllable['orderNumber'],
                        syllable['id']
                    ))
                else:
                    sql_insert_syllable = """
                        INSERT INTO contentsyllable (contentId, syllableText, audioPath, orderNumber)
                        VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(sql_insert_syllable, (
                        content_id,
                        syllable['syllableText'],
                        syllable['audioPath'],
                        syllable['orderNumber']
                    ))

            for id in stored_syllables - existing_syllables:
                cursor.execute("DELETE FROM contentsyllable WHERE id = %s", (id,))

            conn.commit()
           
            
            existing_definitions = {definition['id'] for definition in definitions_data}
            cursor.execute("SELECT * FROM contentdefinition WHERE contentId = %s", (content_id,))

            stored_definitions = set()
            rows = cursor.fetchall()
            for row in rows:
                try:
                    stored_definitions.add(row[0])
                except Exception as e:
                    print(f"Error adding row to stored_definitions: {e}")

            for definition in definitions_data:
                if definition['id'] in stored_definitions:
                    sql_update_definition = """
                        UPDATE contentdefinition
                        SET nativeDefinition = %s, englishDefinition = %s, orderNumber = %s
                        WHERE contentId = %s
                    """
                    cursor.execute(sql_update_definition, (
                        definition['nativeDefinition'],
                        definition['englishDefinition'],
                        definition['orderNumber'],
                        definition['contentId']
                    ))
                else:
                    sql_insert_definition = """
                        INSERT INTO contentdefinition (contentId, nativeDefinition, englishDefinition, orderNumber)
                        VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(sql_insert_definition, (
                        content_id,
                        definition['nativeDefinition'],
                        definition['englishDefinition'],
                        definition['orderNumber']
                    ))

            for id in stored_definitions - existing_definitions:
                cursor.execute("DELETE FROM contentdefinition WHERE id = %s", (id,))

            conn.commit()

            
            existing_examples = {example['id'] for example in examples_data}
            cursor.execute("SELECT * FROM contentexample WHERE contentId = %s", (content_id,))

            stored_examples = set()
            rows = cursor.fetchall()
            for row in rows:
                try:
                    stored_examples.add(row[0])                
                except Exception as e:
                    print(f"Error adding row to stored_examples: {e}")

            for example in examples_data:
                if example['id'] in stored_examples:
                    sql_update_example = """
                        UPDATE contentexample
                        SET nativeExample = %s, englishExample = %s, orderNumber = %s
                        WHERE contentId = %s
                    """
                    cursor.execute(sql_update_example, (
                        example['nativeExample'],
                        example['englishExample'],
                        example['orderNumber'],
                        example['contentId']
                    ))
                else:
                    sql_insert_example = """
                        INSERT INTO contentexample (contentId, nativeExample, englishExample, orderNumber)
                        VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(sql_insert_example, (
                        content_id,
                        example['nativeExample'],
                        example['englishExample'],
                        example['orderNumber']
                    ))

            for id in stored_examples - existing_examples:
                cursor.execute("DELETE FROM contentexample WHERE id = %s", (id,))

            conn.commit()

        return jsonify({'isSuccess': True, "message": "Content saved successfully"}), 201

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'isSuccess': False, "message": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_Contents():
    langID = request.args.get('languageID')
    contentTypeId = request.args.get('contentTypeID')
    searchString = request.args.get('searchString')
    pageNo = int(request.args.get('pageNo', 1))
    pageSize = 10
    offset = (pageNo - 1) * pageSize
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT * FROM content where languageID = %s and isActive = true
    """
    values = [langID,]

    if searchString:
        query += " AND (contentText LIKE %s OR englishTranslation LIKE %s)"
        likePattern = f"%{searchString}%"
        values.extend([likePattern, likePattern])
    
    if contentTypeId:
        query += " AND (contentTypeId = %s)"
        values.extend([contentTypeId])

    query += """
        ORDER BY contentText
        LIMIT %s OFFSET %s
    """
    values.extend([pageSize, offset])
    cursor.execute(query, tuple(values))
    contents = cursor.fetchall()
    count_query = "SELECT COUNT(*) as total FROM content where languageID = %s and isActive = true"
    countvalues = [langID]
    if searchString:
        count_query += " AND (contentText LIKE %s OR englishTranslation LIKE %s)"
        likePattern = f"%{searchString}%"
        countvalues.extend([likePattern, likePattern])

    if contentTypeId:
        count_query += " AND (contentTypeId = %s)"
        countvalues.extend([contentTypeId])

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

def get_Contents_All():
    langID = request.args.get('languageID')
    contentTypeId = 1 

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    
    query = """
        SELECT * FROM content
        WHERE languageID = %s AND contentTypeId = %s AND isActive = true
        ORDER BY contentText
    """
    values = [langID, contentTypeId]

    
    cursor.execute(query, tuple(values))
    contents = cursor.fetchall()
    
    
    count_query = """
        SELECT COUNT(*) as total FROM content
        WHERE languageID = %s AND contentTypeId = %s AND isActive = true
    """
    cursor.execute(count_query, tuple(values))
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


def getContentById():
    contentId = request.args.get('contentId')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT * FROM content where contentID = %s
    """
    values = [contentId,]

    cursor.execute(query, tuple(values))
    contents = cursor.fetchone()
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
                'totalCount': 1
            }), 200

def getSyllablesByContentId():
    contentId = request.args.get('contentId')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT * FROM contentsyllable where contentID = %s
    """
    values = [contentId,]

    cursor.execute(query, tuple(values))
    syllables = cursor.fetchall()
    if not syllables:
        return jsonify({
            'isSuccess': True,
            'message': 'No syllables found',
            'data': [],
            'data2': None,
            'totalCount': 0
        }), 200
    return jsonify({
                'isSuccess': True,
                'message': 'Successfully Retrieved',
                'data': syllables,
                'data2': None,
                'totalCount': 0
            }), 200

def getDefinitionByContentId():
    contentId = request.args.get('contentId')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT * FROM contentdefinition where contentID = %s
    """
    values = [contentId,]

    cursor.execute(query, tuple(values))
    definitions = cursor.fetchall()
    if not definitions:
        return jsonify({
            'isSuccess': True,
            'message': 'No definitions found',
            'data': [],
            'data2': None,
            'totalCount': 0
        }), 200
    return jsonify({
                'isSuccess': True,
                'message': 'Successfully Retrieved',
                'data': definitions,
                'data2': None,
                'totalCount': 0
            }), 200

def getExamplesByContentId():
    contentId = request.args.get('contentId')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT * FROM contentexample where contentID = %s
    """
    values = [contentId,]

    cursor.execute(query, tuple(values))
    examples = cursor.fetchall()
    if not examples:
        return jsonify({
            'isSuccess': True,
            'message': 'No examples found',
            'data': [],
            'data2': None,
            'totalCount': 0
        }), 200
    return jsonify({
                'isSuccess': True,
                'message': 'Successfully Retrieved',
                'data': examples,
                'data2': None,
                'totalCount': 0
            }), 200

def getFileByFileName():
    file_url = request.args.get('fileName') 
    
    if not file_url:
        return jsonify({"error": "fileName parameter is required"}), 400
    
    return jsonify({"file_url": file_url})
    
def contentInactive():
    contentId = int(request.args.get('contentId')) 
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        UPDATE content SET isActive = false where contentID = %s
    """
    values = [contentId,]
    cursor.execute(query, values)
    conn.commit()
    return jsonify({'isSuccess': True, "message": "Content updated successfully"}), 200

def sectionInactive():
    contentId = int(request.args.get('contentId')) 
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        UPDATE content SET isActive = false where contentID = %s
    """
    values = [contentId,]
    cursor.execute(query, values)
    conn.commit()
    return jsonify({'isSuccess': True, "message": "Content updated successfully"}), 200


