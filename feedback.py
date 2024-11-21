from flask import request, jsonify
from datetime import datetime
from db import get_db_connection  # assuming you have a separate db connection file

def get_feedback():
    searchString = request.args.get('searchString')
    pageNo = int(request.args.get('pageNo', 1))
    startDate = request.args.get('startDate')
    endDate = request.args.get('endDate')
    pageSize = 15
    offset = (pageNo - 1) * pageSize
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Base query
    query = """
        SELECT uf.*, u.name, u.email
        FROM userfeedback uf
        INNER JOIN user u ON u.userId = uf.userPlayerID
        WHERE 1 = 1
    """
    values = []

    # Add search filter
    if searchString:
        query += " AND (u.name LIKE %s OR u.email LIKE %s OR uf.feedbackText LIKE %s)"
        likePattern = f"%{searchString}%"
        values.extend([likePattern, likePattern, likePattern])

    # Add date range filter
    if startDate and endDate:
        try:
            # Validate dates
            start_date = datetime.strptime(startDate, '%Y-%m-%d')
            end_date = datetime.strptime(endDate, '%Y-%m-%d')
            query += " AND uf.feedbackDate BETWEEN %s AND %s"
            values.extend([start_date, end_date])
        except ValueError:
            return jsonify({
                'isSuccess': False,
                'message': 'Invalid date format. Expected YYYY-MM-DD.',
                'data': [],
                'totalCount': 0
            }), 400

    # Add ordering, limit, and offset
    query += """
        ORDER BY uf.feedbackDate DESC
        LIMIT %s OFFSET %s
    """
    values.extend([pageSize, offset])

    # Execute query
    cursor.execute(query, tuple(values))
    feedbacks = cursor.fetchall()

    # Count total entries for pagination
    count_query = """
        SELECT COUNT(*) AS total
        FROM userfeedback uf
        INNER JOIN user u ON u.userId = uf.userPlayerID
        WHERE 1 = 1
    """
    count_values = []

    if searchString:
        count_query += " AND (u.name LIKE %s OR u.email LIKE %s OR uf.feedbackText LIKE %s)"
        count_values.extend([likePattern, likePattern, likePattern])
    
    if startDate and endDate:
        count_query += " AND uf.feedbackDate BETWEEN %s AND %s"
        count_values.extend([start_date, end_date])

    cursor.execute(count_query, tuple(count_values))
    total_count = cursor.fetchone()['total']

    # Close database connection
    cursor.close()
    conn.close()

    if not feedbacks:
        return jsonify({
            'isSuccess': True,
            'message': 'No feedbacks found',
            'data': [],
            'totalCount': 0
        }), 200

    return jsonify({
        'isSuccess': True,
        'message': 'Successfully retrieved feedbacks',
        'data': feedbacks,
        'totalCount': total_count
    }), 200
