from flask import request, jsonify
from datetime import datetime
from db import get_db_connection 

def get_dailytask():
    searchString = request.args.get('searchString')
    pageNo = int(request.args.get('pageNo', 1))
    startDate = request.args.get('startDate')
    endDate = request.args.get('endDate')
    pageSize = 15
    offset = (pageNo - 1) * pageSize


    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    
    query = """
        SELECT dt.*, dtt.typeName FROM dailytask dt
        INNER JOIN dailytasktype dtt on dtt.id = dt.taskTypeId
        WHERE 1 = 1
    """
    values = []

    
    if searchString:
        query += " AND (dtt.typeName LIKE %s)"
        likePattern = f"%{searchString}%"
        values.extend([likePattern])
    
    if startDate and endDate:
        try:
            
            start_date = datetime.strptime(startDate, '%Y-%m-%d')
            end_date = datetime.strptime(endDate, '%Y-%m-%d')
            query += " AND dt.taskDate BETWEEN %s AND %s"
            values.extend([start_date, end_date])
        except ValueError:
            return jsonify({
                'isSuccess': False,
                'message': 'Invalid date format. Expected YYYY-MM-DD.',
                'data': [],
                'totalCount': 0
            }), 400

    
    query += """
        ORDER BY dt.taskDate DESC
        LIMIT %s OFFSET %s
    """
    values.extend([pageSize, offset])

    
    cursor.execute(query, tuple(values))
    tasks = cursor.fetchall()

    
    count_query = """
        SELECT COUNT(*) AS total
        FROM dailytask dt
        INNER JOIN dailytasktype dtt on dtt.id = dt.taskTypeId
        WHERE 1 = 1
    """
    count_values = []

    if searchString:
        count_query += " AND (dtt.typeName LIKE %s)"
        count_values.extend([likePattern])
    
    if startDate and endDate:
        count_query += " AND dt.taskDate BETWEEN %s AND %s"
        count_values.extend([start_date, end_date])

    cursor.execute(count_query, tuple(count_values))
    total_count = cursor.fetchone()['total']

    
    cursor.close()
    conn.close()

    if not tasks:
        return jsonify({
            'isSuccess': True,
            'message': 'No daily task found',
            'data': [],
            'totalCount': 0
        }), 200

    return jsonify({
        'isSuccess': True,
        'message': 'Successfully retrieved daily task',
        'data': tasks,
        'totalCount': total_count
    }), 200

def get_DailyTaskType():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM dailytasktype WHERE isImplemented = 1"
    cursor.execute(query)
    dailyTaskTypes = cursor.fetchall()
    if not dailyTaskTypes:
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
                'data': dailyTaskTypes,
                'data2': None,
                'totalCount': None 
            }), 200

def save_dailyTask():
    conn = get_db_connection()
    cursor = conn.cursor()

    
    task_typeId = int(request.form.get('taskTypeId'))
    task_ID = request.form.get('taskID')
    powerupId = request.form.get('powerUpId')
    is_update = task_ID is not None and task_ID != '0'

    if is_update:
        task_ID = int(task_ID)
    else:
        task_ID = None

    reward_Coins = float(request.form.get('rewardCoins'))
    task_Date = request.form.get('taskDate')
    quantity = request.form.get('quantity')

    if is_update:
        
        sql_content = """
            UPDATE dailytask
            SET rewardCoins = %s, taskDate = %s, taskTypeId = %s, quantity = %s, powerUpId = %s
            WHERE taskID = %s
        """
        cursor.execute(sql_content, (
            reward_Coins,
            task_Date,
            task_typeId,
            quantity,
            powerupId,
            task_ID
        ))

    else:
        sql_content = """
            INSERT INTO dailytask (rewardCoins, taskDate, taskTypeId, quantity, powerupId)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(sql_content, (
            reward_Coins,
            task_Date,
            task_typeId,
            quantity,
            powerupId
        ))

        task_id = cursor.lastrowid  

        selectUser = """
            SELECT userPlayerId FROM vista
        """
        cursor.execute(selectUser)
        users = cursor.fetchall()  
 
        sql_content_playerdailytask = """
            INSERT INTO playerdailytask (userPlayerID, taskID, isCompleted)
            VALUES (%s, %s, %s)
        """

        eventLogsQuery = """
            INSERT INTO eventlogs (eventDate, dailyTaskId, userPlayerID, currentValue)
            VALUES (%s, %s, %s, %s)
        """

        for user in users:
            user_player_id = user[0]
            cursor.execute(sql_content_playerdailytask, (
                user_player_id,  
                task_id,         
                False            
            ))
            cursor.execute(eventLogsQuery, (
                task_Date,
                task_id,  
                user_player_id,         
                0            
            ))

    conn.commit()
    return jsonify({'isSuccess': True, "message": "Daily Task saved successfully"}), 200

def deleteDailyTask():
    conn = get_db_connection()
    cursor = conn.cursor()
    task_id = int(request.args.get('taskID')) 

    print(task_id)
    try:     
        sql_delete_playerdailytask = """
            DELETE FROM playerdailytask
            WHERE taskID = %s
        """
        cursor.execute(sql_delete_playerdailytask, (task_id,))
        conn.commit()

        if cursor.rowcount == 0:
            print(f"No records found in playerdailytask for taskID {task_id}")
        
        
        sql_delete_dailytask = """
            DELETE FROM dailytask
            WHERE taskID = %s
        """
        cursor.execute(sql_delete_dailytask, (task_id,))

        
        if cursor.rowcount == 0:
            return jsonify({'isSuccess': False, "message": "No record found for the provided taskID in dailytask"}), 404

        
        conn.commit()

        
        return jsonify({'isSuccess': True, "message": "Daily Task deleted successfully"}), 200

    except Exception as e:
        
        conn.rollback()
        print(f"Error deleting daily task with ID {task_id}: {e}")
        
        
        return jsonify({'isSuccess': False, "message": "Error deleting Daily Task", "error": str(e)}), 500

    finally:
        
        cursor.close()
        conn.close()

def get_powerUps():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT p.* FROM powerup p inner join item i on i.itemId = p.itemID WHERe isImplemented = 1 and isActive = 1"
    cursor.execute(query)
    powerUps = cursor.fetchall()
    if not powerUps:
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
                'data': powerUps,
                'data2': None,
                'totalCount': None 
            }), 200
    
