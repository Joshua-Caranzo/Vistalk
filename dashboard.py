from db import get_db_connection
from flask import request, jsonify
import os
from datetime import datetime, timedelta, date

def getLeaderBoards():
    granularity = request.args.get('granularity')  
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    today = date.today()
    
    if granularity == "Daily":
        start_date = today
        end_date = today
    elif granularity == "Weekly":
        start_date = today - timedelta(days=today.weekday())  
        end_date = start_date + timedelta(days=6)  
    elif granularity == "Monthly":
        start_date = today.replace(day=1)  
        end_date = (start_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)  
    elif granularity == "Yearly":
        start_date = today.replace(month=1, day=1)  
        end_date = today.replace(month=12, day=31)  
    else:  
        start_date = date(2000, 1, 1)  
        end_date = today

    query = """
        SELECT u.name, u.imagePath, 
               (SELECT SUM(score) FROM dailyScore ds 
                WHERE ds.userPlayerId = v.userPlayerID 
                AND ds.dateDaily BETWEEN %s AND %s) as totalScore 
        FROM vista v 
        INNER JOIN user u ON u.UserID = v.userPlayerID 
        WHERE u.isPlayer = 1 AND u.isActive = 1 
        GROUP BY u.name, u.imagePath, totalScore
        ORDER BY totalScore DESC
        LIMIT 10
    """
    
    cursor.execute(query, (start_date, end_date))
    vistas = cursor.fetchall()
    print(vistas)
    if not vistas:
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
        'data': vistas,
        'data2': None,
        'totalCount': None 
    }), 200

def getStatusVista():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT 
        COUNT(CASE WHEN user.isactive = 1 THEN 1 END) AS active,
        COUNT(CASE WHEN user.isactive = 0 THEN 1 END) AS inactive
    FROM 
        vista 
    INNER JOIN 
        user ON vista.userPlayerID = user.userID;
    """
    cursor.execute(query)
    vistas = cursor.fetchone()

    if not vistas:
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
        'data': vistas,
        'data2': None,
        'totalCount': None 
    }), 200

def getLanguageUsers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT l.name as languageName, COUNT(*) AS userCount
            FROM vista
            INNER JOIN user ON user.userId = vista.userPlayerId
            INNER JOIN language l ON l.languageId = vista.currentLanguageId
            WHERE user.isActive = true
            GROUP BY l.name;
    """
    cursor.execute(query)
    vistas = cursor.fetchall()

    if not vistas:
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
        'data': vistas,
        'data2': None,
        'totalCount': None 
    }), 200

def getSubscriptionData():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
            SELECT 
                s.subscriptionName AS type,
                MONTH(ct.transactionDate) AS month,
                COUNT(ct.subscriptionID) AS subscriptionCount
            FROM 
                coinTransaction ct
            INNER JOIN 
                subscription s ON s.Id = ct.subscriptionId
            GROUP BY 
                s.subscriptionName, MONTH(ct.transactionDate)
            ORDER BY 
                s.subscriptionName, MONTH(ct.transactionDate);

    """
    cursor.execute(query)
    vistas = cursor.fetchall()

    if not vistas:
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
        'data': vistas,
        'data2': None,
        'totalCount': None 
    }), 200

def userRatings():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
            SELECT 
                rating AS type,
                MONTH(ratingDate) AS month,
                COUNT(rating) AS ratingCount
            FROM 
                rating
            GROUP BY 
                rating, MONTH(ratingDate)
            ORDER BY 
                month, rating
    """
    
    cursor.execute(query)
    rating = cursor.fetchall()

    if not rating:
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
        'data': rating,
        'data2': None,
        'totalCount': None 
    }), 200
    
def salesReport():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    granular = request.args.get('granular')

    
    granular_mapping = {
        "Daily": "daily",
        "Weekly": "weekly",
        "Monthly": "monthly",
        "Yearly": "yearly",
        "All Time": "all_time"
    }

    
    granular_value = granular_mapping.get(granular, None)

    
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())  
    end_of_week = start_of_week + timedelta(days=6)  

    query = """
        SELECT 
            SUM(amountPaid) AS totalAmountPaid
        FROM cointransaction
        WHERE 
    """
    
    if granular_value == 'daily':
        query += "DATE(transactionDate) = DATE(NOW())"  
    elif granular_value == 'weekly':
        query += "transactionDate BETWEEN DATE(%s) AND DATE(%s)"  
        query_params = (start_of_week.strftime('%Y-%m-%d'), end_of_week.strftime('%Y-%m-%d'))
    elif granular_value == 'monthly':
        query += "MONTH(transactionDate) = MONTH(NOW()) AND YEAR(transactionDate) = YEAR(NOW())"  
    elif granular_value == 'yearly':
        query += "YEAR(transactionDate) = YEAR(NOW())"  
    else:
        query += "1"  

    cursor.execute(query, locals().get('query_params', ()))
    sales = cursor.fetchone()  
    total_amount_paid = sales['totalAmountPaid'] if sales and sales['totalAmountPaid'] is not None else 0

    if not sales or total_amount_paid is None:
        return jsonify({
            'isSuccess': True,
            'message': 'No sales data found',
            'data': total_amount_paid,
            'totalAmountPaid': 0,  
            'data2': None,
            'totalCount': 0
        }), 200

    return jsonify({
        'isSuccess': True,
        'message': 'Successfully Retrieved',
        'data': total_amount_paid,
        'data2': None,
        'totalCount': 1  
    }), 200

def salesReportCoinBags():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    granular = request.args.get('granular')

    
    granular_mapping = {
        "Daily": "daily",
        "Weekly": "weekly",
        "Monthly": "monthly",
        "Yearly": "yearly",
        "All Time": "all_time"
    }

    
    granular_value = granular_mapping.get(granular, None)

    
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())  
    end_of_week = start_of_week + timedelta(days=6)  

    query = """
        SELECT 
            SUM(amountPaid) AS totalAmountPaid
        FROM cointransaction
        WHERE coinBagId is not null AND
    """
    
    if granular_value == 'daily':
        query += "DATE(transactionDate) = DATE(NOW())"  
    elif granular_value == 'weekly':
        query += "transactionDate BETWEEN DATE(%s) AND DATE(%s)"  
        query_params = (start_of_week.strftime('%Y-%m-%d'), end_of_week.strftime('%Y-%m-%d'))
    elif granular_value == 'monthly':
        query += "MONTH(transactionDate) = MONTH(NOW()) AND YEAR(transactionDate) = YEAR(NOW())"  
    elif granular_value == 'yearly':
        query += "YEAR(transactionDate) = YEAR(NOW())"  
    else:
        query += "1"  

    cursor.execute(query, locals().get('query_params', ()))
    sales = cursor.fetchone()  
    total_amount_paid = sales['totalAmountPaid'] if sales and sales['totalAmountPaid'] is not None else 0

    if not sales or total_amount_paid is None:
        return jsonify({
            'isSuccess': True,
            'message': 'No sales data found',
            'data': total_amount_paid,
            'totalAmountPaid': 0,  
            'data2': None,
            'totalCount': 0
        }), 200

    return jsonify({
        'isSuccess': True,
        'message': 'Successfully Retrieved',
        'data': total_amount_paid,
        'data2': None,
        'totalCount': 1  
    }), 200

def salesSubscriptions():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    granular = request.args.get('granular')
    
    granular_mapping = {
        "Daily": "daily",
        "Weekly": "weekly",
        "Monthly": "monthly",
        "Yearly": "yearly",
        "All Time": "all_time"
    }
    
    granular_value = granular_mapping.get(granular, None)
    
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())  
    end_of_week = start_of_week + timedelta(days=6)  

    query = """
        SELECT 
            SUM(amountPaid) AS totalAmountPaid
        FROM cointransaction
        WHERE subscriptionId is not null AND
    """
    
    if granular_value == 'daily':
        query += "DATE(transactionDate) = DATE(NOW())"  
    elif granular_value == 'weekly':
        query += "transactionDate BETWEEN DATE(%s) AND DATE(%s)"  
        query_params = (start_of_week.strftime('%Y-%m-%d'), end_of_week.strftime('%Y-%m-%d'))
    elif granular_value == 'monthly':
        query += "MONTH(transactionDate) = MONTH(NOW()) AND YEAR(transactionDate) = YEAR(NOW())"  
    elif granular_value == 'yearly':
        query += "YEAR(transactionDate) = YEAR(NOW())"  
    else:
        query += "1"  

    cursor.execute(query, locals().get('query_params', ()))
    sales = cursor.fetchone()  
    total_amount_paid = sales['totalAmountPaid'] if sales and sales['totalAmountPaid'] is not None else 0

    if not sales or total_amount_paid is None:
        return jsonify({
            'isSuccess': True,
            'message': 'No sales data found',
            'data': total_amount_paid,
            'totalAmountPaid': 0,  
            'data2': None,
            'totalCount': 0
        }), 200

    return jsonify({
        'isSuccess': True,
        'message': 'Successfully Retrieved',
        'data': total_amount_paid,
        'data2': None,
        'totalCount': 1  
    }), 200

def getTotalSales():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    granular = request.args.get('granular')
    item = request.args.get('item')  

    granular_mapping = {
        "Daily": "daily",
        "Weekly": "weekly",
        "Monthly": "monthly",
        "Yearly": "yearly",
        "All Time": "all_time"
    }

    granular_value = granular_mapping.get(granular, None)

    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())  
    end_of_week = start_of_week + timedelta(days=6)

    query = """
        SELECT 
            ct.*, u.name, 
            CASE
                WHEN cb.coinBagName IS NOT NULL THEN cb.coinBagName 
                ELSE s.subscriptionName 
            END AS itemName,
            CASE 
                WHEN ct.coinBagID IS NOT NULL THEN 'Coin Bag' 
                ELSE 'Subscription' 
            END AS itemType 
        FROM 
            cointransaction ct 
        LEFT JOIN 
            coinbag cb ON cb.coinbagId = ct.coinbagID 
        LEFT JOIN 
            subscription s ON s.id = ct.subscriptionID
        INNER JOIN 
            user u ON u.userID = ct.userPlayerId
        WHERE 
    """
    
    if granular_value == 'daily':
        query += "DATE(transactionDate) = DATE(NOW())"
    elif granular_value == 'weekly':
        query += "transactionDate BETWEEN %s AND %s"
        query_params = (start_of_week.strftime('%Y-%m-%d'), end_of_week.strftime('%Y-%m-%d'))
    elif granular_value == 'monthly':
        query += "MONTH(transactionDate) = MONTH(NOW()) AND YEAR(transactionDate) = YEAR(NOW())"
    elif granular_value == 'yearly':
        query += "YEAR(transactionDate) = YEAR(NOW())"
    elif granular_value == 'all_time':
        query += "1"  
    else:
        return jsonify({
            'isSuccess': False,
            'message': 'Invalid granularity specified',
            'data': None,
            'totalCount': 0
        }), 400

    
    if item == "Subscription":
        query += " AND ct.subscriptionID IS NOT NULL"
    elif item == "Coin bag":
        query += " AND ct.coinBagID IS NOT NULL"
    
    cursor.execute(query, locals().get('query_params', ()))
    sales = cursor.fetchall()  

    if not sales:
        return jsonify({
            'isSuccess': True,
            'message': 'No sales data found',
            'data': sales,
            'totalCount': 0
        }), 200

    return jsonify({
        'isSuccess': True,
        'message': 'Successfully Retrieved',
        'data': sales,
        'totalCount': len(sales)  
    }), 200


def getPronunciationProgress():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    userId = request.args.get('userId')
    query = """
        SELECT 
            SUM(pronunciationScore = 1) AS correct, 
            SUM(pronunciationScore = 0) AS incorrect 
        FROM 
            pronounciationresult 
        WHERE 
            userPlayerID = %s;
    """
    cursor.execute(query, (userId,))
    vistas = cursor.fetchone()

    if not vistas:
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
        'data': vistas,
        'data2': None,
        'totalCount': None 
    }), 200