from flask import request, jsonify
import os
from db import get_db_connection
from setup import upload_media

def save_item():
    conn = get_db_connection()
    cursor = conn.cursor()

    item_typeId = int(request.form.get('itemTypeID'))
    item_id = request.form.get('itemID') 
    is_update = item_id is not None and item_id != '0'

    if is_update:
        item_id = int(item_id)
    else:
        item_id = None

    if item_typeId == 1:
        vcoin_price = float(request.form.get('vcoinPrice'))
        is_premium = request.form.get('isPremium')

        if(is_premium == 'false'):
            is_premium = 0
        else:
            is_premium = 1

        item_name = request.form.get('name')
        description = request.form.get('description')
        isImplemented = request.form.get('isImplemented')
        if(isImplemented == 'false'):
            isImplemented = 0
        else:
            isImplemented = 1
        
        image_file = request.files.get('itemImageFile')
        audio_file_path =request.form.get('filePath')
        if image_file:
            result = upload_media(image_file)
            audio_file_path = result

        if is_update:
            sql_content = """
                UPDATE item
                SET vcoinPrice = %s, isPremium = %s, filePath = %s
                WHERE itemID = %s
            """
            cursor.execute(sql_content, (
                vcoin_price,
                is_premium,
                audio_file_path,
                item_id
            ))

            sql_content = """
                UPDATE powerup
                SET name = %s, description = %s, isImplemented = %s
                WHERE itemID = %s
            """
            cursor.execute(sql_content, (
                item_name,
                description,
                isImplemented,
                item_id
            ))
            conn.commit()

        else:
            # Insert new item and powerUp records
            sql_content = """
                INSERT INTO item (itemTypeID, vcoinPrice, isPremium, filePath)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql_content, (
                item_typeId,
                vcoin_price,
                is_premium,
                audio_file_path
            ))
            conn.commit()
            item_id = cursor.lastrowid

            sql_content = """
                INSERT INTO powerup (itemID, name, description, isImplemented)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql_content, (
                item_id,
                item_name,
                description,
                isImplemented
            ))

    elif item_typeId == 3:
        item_id = int(request.form.get('coinBagId'))
        price = float(request.form.get('moneyPrice'))
        bagName = request.form.get('coinBagName')
        quantity = int(request.form.get('quantity'))

        if item_id != 0:
            # Update existing coinBag record
            sql_content = """
                UPDATE coinbag
                SET quantity = %s, moneyPrice = %s, coinBagName = %s
                WHERE coinBagId = %s
            """
            cursor.execute(sql_content, (
                quantity,
                price,
                bagName,
                item_id
            ))

        else:
            # Insert new coinBag record
            sql_content = """
                INSERT INTO coinbag (quantity, moneyPrice, coinBagName)
                VALUES (%s, %s, %s)
            """
            cursor.execute(sql_content, (
                quantity,
                price,
                bagName
            ))
    print(item_id)
    if not is_update and item_id is not None: 
        cursor.execute("SELECT userID FROM user WHERE isActive = 1 and isPlayer = 1")
        active_users = cursor.fetchall()

        user_item_inserts = [
            (user[0], item_id, 0) for user in active_users
        ]
        cursor.executemany(
            "INSERT INTO useritem (userPlayerID, itemID, quantity) VALUES (%s, %s, %s)",
            user_item_inserts
        )

        conn.commit()
        return jsonify({'isSuccess': True, "message": "Item saved successfully"}), 201
    
    else:
        return jsonify({'isSuccess': False, "message": "Invalid itemTypeID provided"}), 200

def getItemType():
    con =get_db_connection()
    cursor = con.cursor(dictionary=True)
    query = "SELECT * FROM itemtype"
    cursor.execute(query)
    itemTypes = cursor.fetchall()
    if not itemTypes:
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
                'data': itemTypes,
                'data2': None,
                'totalCount': None 
            }), 200

def get_items():
    itemTypeID = request.args.get('itemTypeID')
    searchString = request.args.get('searchString')
    pageNo = int(request.args.get('pageNo', 1))
    pageSize = 15
    offset = (pageNo - 1) * pageSize

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = ""
    values = []

    if itemTypeID == '1':
        # Inner join with powerUp table
        query = """
            SELECT i.*, pu.name, pu.description, pu.isImplemented
            FROM item i
            INNER JOIN powerup pu ON pu.itemID = i.itemID 
            WHERE i.isActive = true
        """
        if searchString:
            query += " AND (pu.name LIKE %s OR pu.description LIKE %s)"
            likePattern = f"%{searchString}%"
            values.extend([likePattern, likePattern])
        query += " ORDER BY pu.name LIMIT %s OFFSET %s"
    elif itemTypeID == '2':
        # Inner join with backgroundMusic table
        query = """
            SELECT i.*, mu.musicTitle, mu.musicGenre 
            FROM item i
            INNER JOIN backgroundmusic mu ON mu.itemID = i.itemID 
            WHERE i.isActive = true
        """
        if searchString:
            query += " AND mu.musicTitle LIKE %s"
            likePattern = f"%{searchString}%"
            values.append(likePattern)
        query += " ORDER BY mu.musicTitle LIMIT %s OFFSET %s"
    elif itemTypeID == '3':
        # Select from coinBag table instead of item
        query = """
            SELECT cb.* 
            FROM coinbag cb
            WHERE cb.isActive = true
        """
        if searchString:
            query += " AND cb.coinBagName LIKE %s"
            likePattern = f"%{searchString}%"
            values.append(likePattern)
        query += " ORDER BY cb.coinBagName LIMIT %s OFFSET %s"
    else:
        # Handle invalid itemTypeID case if needed
        return jsonify({
            'isSuccess': False,
            'message': 'Invalid itemTypeID provided',
            'data': [],
            'data2': None,
            'totalCount': 0
        }), 400

    # Add pagination
    values.extend([pageSize, offset])

    cursor.execute(query, tuple(values))
    items = cursor.fetchall()
    if itemTypeID in ['1', '2']:
        for item in items:
            item['isPremium'] = bool(item['isPremium'])

    count_query = ""
    count_values = []

    if itemTypeID == '1':
        count_query = """
            SELECT COUNT(*) as total 
            FROM item i 
            INNER JOIN powerup pu ON pu.itemID = i.itemID 
            WHERE i.isActive = true
        """
        if searchString:
            count_query += " AND (pu.name LIKE %s OR pu.description LIKE %s)"
            count_values.extend([likePattern, likePattern])
    elif itemTypeID == '2':
        count_query = """
            SELECT COUNT(*) as total 
            FROM item i 
            INNER JOIN backgroundmusic mu ON mu.itemID = i.itemID 
            WHERE i.isActive = true
        """
        if searchString:
            count_query += " AND mu.musicTitle LIKE %s"
            count_values.append(likePattern)
    elif itemTypeID == '3':
        count_query = """
            SELECT COUNT(*) as total 
            FROM coinBag cb 
            WHERE cb.isActive = true
        """
        if searchString:
            count_query += " AND cb.coinBagName LIKE %s"
            count_values.append(likePattern)

    cursor.execute(count_query, tuple(count_values))
    total_count = cursor.fetchone()['total']

    if not items:
        return jsonify({
            'isSuccess': True,
            'message': 'No items found',
            'data': [],
            'data2': None,
            'totalCount': 0
        }), 200

    return jsonify({
        'isSuccess': True,
        'message': 'Successfully Retrieved',
        'data': items,
        'data2': None,
        'totalCount': total_count
    }), 200
    
def itemInactive():
    itemId = int(request.args.get('itemId')) 
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        UPDATE item SET isActive = false where itemID = %s
    """
    values = [itemId,]
    cursor.execute(query, values)
    conn.commit()
    return jsonify({'isSuccess': True, "message": "Item updated successfully"}), 200

def coinBagInactive():
    itemId = int(request.args.get('coinBagId')) 
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        UPDATE coinbag SET isActive = false where coinBagId = %s
    """
    values = [itemId,]
    cursor.execute(query, values)
    conn.commit()
    return jsonify({'isSuccess': True, "message": "Item updated successfully"}), 200


