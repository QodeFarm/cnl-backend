import MySQLdb  # type: ignore
from django.conf import settings


query = {
"Sales_Over_the_Last_12_Months" : "SELECT DATE_FORMAT(sio.invoice_date, '%M-%Y') AS month_year, SUM(sio.total_amount) AS total_sales FROM sale_invoice_orders sio WHERE sio.invoice_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH) GROUP BY YEAR(sio.invoice_date), MONTH(sio.invoice_date) ORDER BY YEAR(sio.invoice_date), MONTH(sio.invoice_date);",

"Purchase_Over_the_Last_12_Months" : "SELECT DATE_FORMAT(invoice_date, '%M-%Y') AS month_year, SUM(total_amount) AS monthly_purchases FROM purchase_invoice_orders WHERE invoice_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH) GROUP BY YEAR(invoice_date), MONTH(invoice_date) ORDER BY YEAR(invoice_date), MONTH(invoice_date);", 

"Top_5_Itmes_Sold_In_Last_30_Days" : "SELECT p.name AS product_name, SUM(i.quantity) AS total_sold_quantity FROM sale_invoice_items i JOIN products p ON i.product_id = p.product_id WHERE i.created_at >= DATE_SUB(CURDATE(), INTERVAL 30 DAY) GROUP BY i.product_id, p.name ORDER BY total_sold_quantity DESC LIMIT 5;",

"Top_5_Items_Groups_In_Last_6_Months" : "SELECT g.group_name AS item_group, SUM(i.quantity * i.rate) AS total_amount FROM sale_invoice_items i JOIN products p ON i.product_id = p.product_id  JOIN product_groups g ON p.product_group_id = g.product_group_id  JOIN sale_invoice_orders o ON i.sale_invoice_id = o.sale_invoice_id  WHERE o.invoice_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)  GROUP BY g.group_name ORDER BY total_amount DESC LIMIT 5;",

"Top_5_Sold_Items_In_Current_FY" : "WITH financial_year AS (SELECT CASE WHEN MONTH(CURDATE()) < 4 THEN DATE(CONCAT(YEAR(CURDATE()) - 1, '-04-01')) ELSE DATE(CONCAT(YEAR(CURDATE()), '-04-01')) END AS fy_start_date, CASE WHEN MONTH(CURDATE()) < 4 THEN DATE(CONCAT(YEAR(CURDATE()), '-03-31')) ELSE DATE(CONCAT(YEAR(CURDATE()) + 1, '-03-31')) END AS fy_end_date) SELECT p.name AS item_name, SUM(i.quantity * i.rate) AS total_amount FROM sale_invoice_items i JOIN sale_invoice_orders o ON i.sale_invoice_id = o.sale_invoice_id JOIN products p ON i.product_id = p.product_id CROSS JOIN financial_year fy WHERE o.invoice_date BETWEEN fy.fy_start_date AND fy.fy_end_date GROUP BY p.name ORDER BY total_amount DESC LIMIT 5;"
}

def execute_query(query):
    """Executes the given SQL query and returns the result."""
    db_config = settings.DATABASES['default']
    
    # Ensure all required database configurations are present
    connection = MySQLdb.connect(
        host=db_config.get('HOST', 'localhost'),
        user=db_config.get('USER', ''),
        password=db_config.get('PASSWORD', ''),
        database=db_config.get('NAME', ''),
        port=int(db_config.get('PORT', 3306)),
    )    
    cursor = connection.cursor()

    try:
        cursor.execute("SET SESSION sql_mode = (SELECT REPLACE(@@sql_mode, 'ONLY_FULL_GROUP_BY', ''));")
        cursor.execute(query)  
        if query:
            results = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in results]
        return {"message": "Query executed successfully"}
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": str(e)}
    
    finally:
        # Close the cursor and the connection after the query is executed
        cursor.close()
        connection.close()
