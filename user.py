
import jwt
from datetime import datetime, timedelta, timezone, date
from flask import request, jsonify
import hashlib
import emailService
from db import SECRET_KEY , get_db_connection
import os
from setup import upload_media
def generate_token(user_name):
    expiration_time = datetime.now(timezone.utc) + timedelta(days=1)
    token = jwt.encode({
        'sub': user_name,
        'exp': expiration_time
    }, SECRET_KEY, algorithm='HS256')
    return token

def login():
    email = request.args.get('email')
    password = request.args.get('hashedPassword')

    if not email or not password:
        return jsonify({
            'isSuccess': False,
            'message': 'Email and password are required',
            'data': None,
            'data2': None,
            'totalCount': None
        }), 200

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT name, encryptedpassword FROM user WHERE email = %s AND isAdmin = true", (email,))
        user = cursor.fetchone()

        if user and password == user['encryptedpassword']:
            token = generate_token(user['name'])
            return jsonify({
                'isSuccess': True,
                'message': 'Login successful',
                'data': {
                    'name': user['name'],
                    'token': token
                },
                'data2': None,
                'totalCount': None 
            }), 200
        else:
            return jsonify({
                'isSuccess': False,
                'message': 'Invalid credentials',
                'data': None,
                'data2': None,
                'totalCount': None
            }), 200
    finally:
        cursor.close()
        conn.close()

def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

def createVista():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    languageId = data.get('languageId')
    if not email or not password or not name:
        return jsonify({
            'isSuccess': False,
            'message': 'All fields are required',
            'data': None,
            'data2': None,
            'totalCount': None
        }), 200

    if is_email_in_use(email):
        return jsonify({
            'isSuccess': False,
            'message': 'Email already in use, please use another email',
            'data': None,
            'data2': None,
            'totalCount': None
        }), 200
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = """
        INSERT INTO user (name, email, encryptedPassword, isActive, isAdmin, isPlayer, isAccountLocked, failedLogins) 
        VALUES (%s, %s, %s, %s, %s, %s, %s , %s)
        """
        cursor.execute(query, (name, email, hash_password(password), 1, 0, 1, 0, 0))
        conn.commit()
        userId = cursor.lastrowid

        vistaQuery = """
        INSERT INTO vista (userPlayerId, vCoin, currentLanguageId, numberPronounced) 
        VALUES (%s, %s, %s,%s)
        """
        cursor.execute(vistaQuery, (userId, 0, languageId, 20))
        conn.commit()
        print('user error')
        
        sectionQuery = """
        SELECT u.unitId, u.unitNumber
        FROM unit u 
        INNER JOIN section s ON s.sectionId = u.sectionID 
        WHERE s.languageID = %s and u.isActive = 1
        """
        cursor.execute(sectionQuery, (languageId,))
        unitIds = cursor.fetchall()

        
        for unit in unitIds:
            isLocked = 0 if unit['unitNumber'] == 1 else 1
            userUnitQuery = """
            INSERT INTO userunit (userPlayerId, unitId, totalCorrectAnswers, totalScore, isLocked) 
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(userUnitQuery, (userId, unit['unitId'], 0, 0, isLocked))
        
        itemQuery = """
        SELECT i.itemId 
        FROM powerup p 
        INNER JOIN item i ON i.itemID = p.itemId WHERE i.isActive = true
        """
        cursor.execute(itemQuery)
        itemIds = cursor.fetchall()

        for item in itemIds:
            userItemQuery = """
            INSERT INTO useritem (userPlayerId, itemId, quantity) 
            VALUES (%s, %s, %s)
            """
            cursor.execute(userItemQuery, (userId, item['itemId'], 0))
        
        today = datetime.now().date()
        dailyTaskQuery = """
        SELECT taskID, taskDate  FROM dailytask 
        WHERE taskDate >= %s
        """
        cursor.execute(dailyTaskQuery, (today,))
        dailyTasks = cursor.fetchall()
        print(dailyTasks)
        for task in dailyTasks:
            taskId = task['taskID']
            taskDate = task['taskDate']
            playerDailyTaskQuery = """
            INSERT INTO playerdailytask (taskId, userPlayerId, isCompleted, isClaimed) 
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(playerDailyTaskQuery, (taskId, userId, 0, 0))

            eventLogQuery = """
            INSERT INTO eventlogs (dailyTaskId, userPlayerId, currentValue, eventDate) 
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(eventLogQuery, (taskId, userId, 0, taskDate))
        
        conn.commit()
        print('otheres')

        
        subject = "Welcome to Vistalk"
        message = """
        Maayong Adlaw, Vista!

        Welcome to the Vistalk Family! We're excited to help you learn Visayan. Enjoy the journey with the Vistalk App!

        Daghang Salamat,
        The Vistalk Team
        """
        emailService.send_email(email, subject, message)
        return jsonify({'isSuccess': True, "message": "User registered successfully"}), 200

    except Exception as e:
        print(str(e))
        conn.rollback()
        return jsonify({'isSuccess': False, "message": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


def lock_account(email, conn):
    cursor = conn.cursor()
    lockout_time = datetime.now() + timedelta(days=1)
    cursor.execute("""
        UPDATE user
        SET isAccountLocked = true, 
            logInTimeLockOut = %s,
            failedlogins = 0
        WHERE email = %s
    """, (lockout_time, email))
    conn.commit()
    cursor.close()

def loginVista():
    email = request.args.get('email')
    password = request.args.get('hashedPassword')

    if not email or not password:
        return jsonify({
            'isSuccess': False,
            'message': 'Email and password are required',
            'data': None,
            'data2': None,
            'totalCount': None
        }), 200
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT userID as id, name, encryptedpassword, failedlogins, isAccountLocked, logInTimeLockOut, isActive
            FROM user
            WHERE email = %s AND isPlayer = true
        """, (email,))
        user = cursor.fetchone()

        if not user:
            return jsonify({
                'isSuccess': False,
                'message': 'User is not found',
                'data': None,
                'data2': None,
                'totalCount': None
            }), 200
        
        if user['isActive'] == False:
            return jsonify({
                'isSuccess': False,
                'message': 'Inactive',
                'data': None,
                'data2': None,
                'totalCount': None
            }), 201

        if user['isAccountLocked']:
            if datetime.now() < user['logInTimeLockOut']:
                return jsonify({
                    'isSuccess': False,
                    'message': 'Your account is locked. Please try again tomorrow.',
                    'data': None,
                    'data2': None,
                    'totalCount': None
                }), 200
            else:
                cursor.execute("""
                    UPDATE user
                    SET isAccountLocked = false, logInTimeLockOut = NULL
                    WHERE email = %s
                """, (email,))
                conn.commit()
        
        if password == user['encryptedpassword']:
            print(user)
            token = generate_token(user['name'])
            cursor.execute("""
                UPDATE user
                SET failedlogins = 0
                WHERE email = %s
            """, (email,))
            conn.commit()
            return jsonify({
                'isSuccess': True,
                'message': 'Login successful',
                'data': {
                    'name': user['name'],
                    'token': token,
                    'id': str(user['id'])
                },
                'data2': None,
                'totalCount': None 
            }), 200
        else:
            new_failed_logins = user['failedlogins'] + 1
            if new_failed_logins >= 5:
                lock_account(email, conn)
                return jsonify({
                    'isSuccess': False,
                    'message': 'Too many failed login attempts. Your account is locked for one day.',
                    'data': None,
                    'data2': None,
                    'totalCount': None
                }), 200
            else:
                cursor.execute("""
                    UPDATE user
                    SET failedlogins = %s
                    WHERE email = %s
                """, (new_failed_logins, email))
                conn.commit()
                return jsonify({
                    'isSuccess': False,
                    'message': 'Invalid credentials',
                    'data': None,
                    'data2': None,
                    'totalCount': None
                }), 200
    finally:
        cursor.close()
        conn.close()

def is_email_in_use(email):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = "SELECT email FROM user WHERE email = %s"
        cursor.execute(query, (email,))
        result = cursor.fetchone()
        return result is not None
    except Exception as e:
        return jsonify({'isSuccess': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

def forgotPassword():
    data = request.json
    email = data.get('email')
    hashedPassword = data.get('hashedPassword')
    currentPassword = data.get('currenthashedPassword')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if currentPassword:
        cursor.execute("""
            SELECT encryptedPassword FROM user
            WHERE email = %s
        """, (email,))
        user = cursor.fetchone()
        if not user:
            return jsonify({
                'isSuccess': False,
                'message': 'User not found!',
                'data': None,
                'data2': None,
                'totalCount': None
            }), 404

        stored_password = user['encryptedPassword']

        if stored_password != currentPassword:
            return jsonify({
                'isSuccess': False,
                'message': 'Current password is incorrect!',
                'data': None,
                'data2': None,
                'totalCount': None
            }), 200

    cursor.execute("""
        UPDATE user
        SET encryptedPassword = %s
        WHERE email = %s
    """, (hashedPassword, email))
    conn.commit()

    return jsonify({
        'isSuccess': True,
        'message': 'Password updated successfully!',
        'data': None,
        'data2': None,
        'totalCount': None
    }), 200

def get_Users():
    searchString = request.args.get('searchString')
    pageNo = int(request.args.get('pageNo', 1))
    isShowSubscriber = request.args.get('isShowSubscriber')
    showInactive = request.args.get('showInactive')
    print(isShowSubscriber, showInactive)

    if(isShowSubscriber == 'false'):
        isShowSubscriber = 0
    else:
        isShowSubscriber = 1
    
    if(showInactive == 'false'):
        showInactive = 0
    else:
        showInactive = 1
    
    pageSize = 15
    offset = (pageNo - 1) * pageSize
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT v.*, u.name, u.email, u.imagePath
        FROM vista v
        INNER JOIN user u ON u.userId = v.userPlayerId
        WHERE (%s = False or u.isActive = 1) AND u.Isplayer = TRUE AND (%s = False OR v.isPremium = 1)
    """
    
    values = [showInactive, isShowSubscriber]

    if searchString:
        query += " AND (u.name LIKE %s OR u.email LIKE %s)"
        likePattern = f"%{searchString}%"
        values.extend([likePattern, likePattern])

    query += """
        ORDER BY u.name
        LIMIT %s OFFSET %s
    """
    values.extend([pageSize, offset])

    cursor.execute(query, tuple(values))
    users = cursor.fetchall()
    print(users)
    for user in users:
        user['powerUps'] = get_UserPowerUps(user['userPlayerId'])

    count_query = """
        SELECT COUNT(*) AS total 
        FROM vista v
        INNER JOIN user u ON u.userId = v.userPlayerId
        WHERE u.isActive = TRUE AND u.Isplayer = TRUE
    """
    
    count_values = []
    
    if searchString:
        count_query += " AND (u.name LIKE %s OR u.email LIKE %s)"
        count_values.extend([likePattern, likePattern])

    cursor.execute(count_query, tuple(count_values))
    total_count = cursor.fetchone()['total']

    if not users:
        return jsonify({
            'isSuccess': True,
            'message': 'No users found',
            'data': [],
            'totalCount': 0
        }), 200

    return jsonify({
        'isSuccess': True,
        'message': 'Successfully retrieved',
        'data': users,
        'totalCount': total_count
    }), 200

def get_UserPowerUps(userID):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT p.name, ui.itemId, ui.quantity, i.filePath FROM powerup p inner join useritem ui on ui.itemId = p.itemID inner join item i on i.itemID = ui.itemID WHERE userplayerID = %s AND isImplemented = true;"
    values = (userID,)
    cursor.execute(query, values)
    powerUps = cursor.fetchall()
    return powerUps

def editVistaProfile():
    data = request.form
    name = data.get('name')
    email = data.get('email')
    userID = data.get('userId')
    file = request.files.get('file')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        update_query = """
            UPDATE user
            SET name = %s, email = %s
            WHERE userID = %s
        """
        cursor.execute(update_query, (name, email, userID))
        print("next here")
        if(file != None):
            result = upload_media(file)
            new_file_name = result
           
            image_update_query = """
                UPDATE user
                SET ImagePath = %s
                WHERE userID = %s
            """
            cursor.execute(image_update_query, (new_file_name, userID))
        
        conn.commit()
        return jsonify({
            'isSuccess': True,
            'message': 'Profile Successfully Updated!',
            'data': [],
            'totalCount': 0
        }), 200
    
    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify({
            'isSuccess': False,
            'message': 'Profile Update Failed!',
            'data': [],
            'totalCount': 0
        }), 200
    
    finally:
        cursor.close()
        conn.close()

def deactivateVistaAccount():
    data = request.json
    user_id = data.get('userId')
    if not user_id:
        return jsonify({
            'isSuccess': False,
            'message': 'User ID is required',
            'data': None
        }), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            UPDATE user
            SET IsActive = 0
            WHERE userID = %s
        """, (user_id,))
        conn.commit()

        return jsonify({
            'isSuccess': True,
            'message': 'Account deactivated successfully',
            'data': None
        }), 200

    except Exception as e:
        conn.rollback()
        return jsonify({
            'isSuccess': False,
            'message': str(e),
            'data': None
        }), 500

def reActivateVista():
    data = request.json
    email = data.get('email')
    if not email:
        return jsonify({
            'isSuccess': False,
            'message': 'User ID is required',
            'data': None
        }), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            UPDATE user
            SET IsActive = 1
            WHERE email = %s
        """, (email,))
        conn.commit()

        return jsonify({
            'isSuccess': True,
            'message': 'Account reactivated successfully',
            'data': None
        }), 200

    except Exception as e:
        conn.rollback()
        return jsonify({
            'isSuccess': False,
            'message': str(e),
            'data': None
        }), 500

def getUserDetails():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    userID = request.args.get('userID')

    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())  
    end_of_week = start_of_week + timedelta(days=6)  
    query = """SELECT u.UserID as id, u.name, u.email, u.imagePath, v.vCoin, v.currentLanguageId, 
                        v.vcoin, v.isPremium as isSubscribed, v.premiumExpiry as expirationDate,
                      (SELECT COUNT(*) FROM userunit uu 
                       INNER JOIN user u ON u.userId = uu.userPlayerID
                       WHERE u.isActive = true AND u.isPlayer = true AND u.userID = %s AND uu.isLocked = false) unitsUnlocked,
                      (SELECT MAX(totalScore) FROM userunit uu  
                       INNER JOIN user u ON u.userId = uu.userPlayerID
                       WHERE u.isActive = true AND u.isPlayer = true AND u.userID = %s AND uu.isLocked = false) highestScore
               FROM user u 
               INNER JOIN vista v ON u.userID = v.userPlayerID 
               WHERE u.isActive = true AND u.isPlayer = true AND u.userID = %s"""
    values = [userID, userID, userID]
    cursor.execute(query, values)
    userProfile = cursor.fetchone()

    if not userProfile:
        return jsonify({
            'isSuccess': True,
            'message': 'No sections found',
            'data': [],
            'data2': None,
            'totalCount': 0
        }), 200

    
    score_query = """
        SELECT dateDaily, score FROM dailyscore
        WHERE userPlayerId = %s AND dateDaily BETWEEN %s AND %s
        ORDER BY dateDaily ASC
    """
    cursor.execute(score_query, (userID, start_of_week, end_of_week))
    weekly_scores = cursor.fetchall()
    total_weekly_score = 0
    
    week_scores = { (start_of_week + timedelta(days=i)).strftime("%A"): 0 for i in range(7) }

    
    for record in weekly_scores:
        day_name = record['dateDaily'].strftime("%A")  
        week_scores[day_name] = record['score']
        total_weekly_score += record['score'] 

    userProfile['weeklyScoreGraph'] = week_scores
    userProfile['totalWeeklyScore'] = total_weekly_score
    print(total_weekly_score)
    print(userProfile['totalWeeklyScore'])

    return jsonify({
        'isSuccess': True,
        'message': 'Successfully Retrieved',
        'data': userProfile,
        'data2': None,
        'totalCount': None 
    }), 200
