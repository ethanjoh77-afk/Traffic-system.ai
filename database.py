def get_data():
    conn = sqlite3.connect("traffic.db")
    c = conn.cursor()

    c.execute("""
    SELECT timestamp, cars, buses, trucks, people 
    FROM traffic_data 
    ORDER BY id DESC 
    LIMIT 30
    """)

    rows = c.fetchall()
    conn.close()

    # convert to JSON-friendly format
    data = []
    for row in rows:
        data.append({
            "time": row[0],
            "cars": row[1],
            "buses": row[2],
            "trucks": row[3],
            "people": row[4]
        })

    return data