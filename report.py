from flask import request, jsonify
from datetime import datetime
from db import get_db_connection 

def get_report():
    searchString = request.args.get('searchString')
    pageNo = int(request.args.get('pageNo', 1))
    hasResponded = request.args.get('hasResponded')
    startDate = request.args.get('startDate')
    endDate = request.args.get('endDate')
    pageSize = 15
    offset = (pageNo - 1) * pageSize

    if(hasResponded == 'false'):
        hasResponded = 0
    else:
        hasResponded = 1

        """ (%s = FALSE OR ur.hasResponded = 1) """

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Base query
    query = """
        SELECT ur.*, u.name, u.email
        FROM userreport ur
        INNER JOIN user u ON u.userId = ur.userPlayerID
        WHERE ur.hasResponded = %s
    """
    values = [hasResponded]

    # Add search filter
    if searchString:
        query += " AND (u.name LIKE %s OR u.email LIKE %s OR ur.reportText LIKE %s)"
        likePattern = f"%{searchString}%"
        values.extend([likePattern, likePattern, likePattern])

    # Add date range filter
    if startDate and endDate:
        try:
            # Validate dates
            start_date = datetime.strptime(startDate, '%Y-%m-%d')
            end_date = datetime.strptime(endDate, '%Y-%m-%d')
            query += " AND ur.reportDate >= %s AND ur.reportDate < %s"
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
        ORDER BY ur.reportDate DESC
        LIMIT %s OFFSET %s
    """
    values.extend([pageSize, offset])

    # Execute query
    cursor.execute(query, tuple(values))
    reports = cursor.fetchall()

    # Count total entries for pagination
    count_query = """
        SELECT COUNT(*) AS total
        FROM userreport ur
        INNER JOIN user u ON u.userId = ur.userPlayerID
        WHERE 1 = 1
    """
    count_values = []

    if searchString:
        count_query += " AND (u.name LIKE %s OR u.email LIKE %s OR ur.reportText LIKE %s)"
        count_values.extend([likePattern, likePattern, likePattern])
    
    if startDate and endDate:
        count_query += " AND ur.reportDate >= %s AND ur.reportDate < %s"
        count_values.extend([start_date, end_date])

    cursor.execute(count_query, tuple(count_values))
    total_count = cursor.fetchone()['total']

    # Close database connection
    cursor.close()
    conn.close()

    if not reports:
        return jsonify({
            'isSuccess': True,
            'message': 'No reports found',
            'data': [],
            'totalCount': 0
        }), 200

    return jsonify({
        'isSuccess': True,
        'message': 'Successfully retrieved reports',
        'data': reports,
        'totalCount': total_count
    }), 200

def reportResponded():
    reportID = int(request.args.get('reportID')) 
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        UPDATE userreport SET hasResponded = TRUE where reportID = %s
    """
    print(query)
    values = [reportID,]
    cursor.execute(query, values)
    conn.commit()
    return jsonify({'isSuccess': True, "message": "Report updated successfully"}), 200
