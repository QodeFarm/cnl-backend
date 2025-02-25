import MySQLdb  # type: ignore
from django.conf import settings


query = {
"Sales_Over_the_Last_12_Months" : "SELECT DATE_FORMAT(sio.invoice_date, '%M-%Y') AS month_year, SUM(sio.total_amount) AS total_sales FROM sale_invoice_orders sio WHERE sio.invoice_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH) GROUP BY YEAR(sio.invoice_date), MONTH(sio.invoice_date) ORDER BY YEAR(sio.invoice_date), MONTH(sio.invoice_date);",

"Compare_weekly_sales_and_growth" : """WITH weekly_sales AS (
    -- Current week sales
    SELECT 
        SUM(total_amount) as current_week_sales,
        SUM(CASE 
            WHEN invoice_date >= DATE_SUB(DATE(NOW()), INTERVAL WEEKDAY(NOW()) DAY) 
                 AND invoice_date <= NOW() 
            THEN total_amount 
            ELSE 0 
        END) as current_week_total,
        -- Last week sales
        SUM(CASE 
            WHEN invoice_date >= DATE_SUB(DATE(NOW()), INTERVAL WEEKDAY(NOW()) + 7 DAY) 
                 AND invoice_date < DATE_SUB(DATE(NOW()), INTERVAL WEEKDAY(NOW()) DAY) 
            THEN total_amount 
            ELSE 0 
        END) as last_week_total
    FROM sale_invoice_orders
    WHERE invoice_date >= DATE_SUB(DATE(NOW()), INTERVAL 14 DAY) -- Limit to last 2 weeks for performance
)
SELECT 
    current_week_total as current_week_sales,
    last_week_total as last_week_sales,
    ROUND(
        CASE 
            WHEN last_week_total = 0 THEN NULL
            ELSE ((current_week_total - last_week_total) / last_week_total * 100)
        END, 
        2
    ) as percentage_change
FROM weekly_sales;""",

"Purchase_Over_the_Last_12_Months" : "SELECT DATE_FORMAT(invoice_date, '%M-%Y') AS month_year, SUM(total_amount) AS monthly_purchases FROM purchase_invoice_orders WHERE invoice_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH) GROUP BY YEAR(invoice_date), MONTH(invoice_date) ORDER BY YEAR(invoice_date), MONTH(invoice_date);", 

"Compare_weekly_purchase_and_growth" : """WITH weekly_purchases AS (
    -- Current week purchases
    SELECT 
        SUM(total_amount) as current_week_purchases,
        SUM(CASE 
            WHEN invoice_date >= DATE_SUB(DATE(NOW()), INTERVAL WEEKDAY(NOW()) DAY) 
                 AND invoice_date <= NOW() 
            THEN total_amount 
            ELSE 0 
        END) as current_week_total,
        -- Last week purchases
        SUM(CASE 
            WHEN invoice_date >= DATE_SUB(DATE(NOW()), INTERVAL WEEKDAY(NOW()) + 7 DAY) 
                 AND invoice_date < DATE_SUB(DATE(NOW()), INTERVAL WEEKDAY(NOW()) DAY) 
            THEN total_amount 
            ELSE 0 
        END) as last_week_total
    FROM purchase_invoice_orders
    WHERE invoice_date >= DATE_SUB(DATE(NOW()), INTERVAL 14 DAY) -- Limit to last 2 weeks for performance
)
SELECT 
    current_week_total as current_week_purchases,
    last_week_total as last_week_purchases,
    ROUND(
        CASE 
            WHEN last_week_total = 0 THEN NULL
            ELSE ((current_week_total - last_week_total) / last_week_total * 100)
        END, 
        2
    ) as percentage_purchase_change
FROM weekly_purchases;""",

"Top_5_Itmes_Sold_In_Last_30_Days" : "SELECT p.name AS product_name, SUM(i.quantity) AS total_sold_quantity FROM sale_invoice_items i JOIN products p ON i.product_id = p.product_id WHERE i.created_at >= DATE_SUB(CURDATE(), INTERVAL 300 DAY) GROUP BY i.product_id, p.name ORDER BY total_sold_quantity DESC LIMIT 5;",

"Top_5_Customers_In_Last_6_Months" : "SELECT c.name AS CustomerName, SUM(so.item_value) AS TotalAmount FROM sale_orders so INNER JOIN customers c ON so.customer_id = c.customer_id WHERE so.order_date >= DATE_ADD(CURDATE(), INTERVAL -6 MONTH) GROUP BY c.name ORDER BY TotalAmount DESC LIMIT 5;",

"Top_5_Items_Groups_In_Last_6_Months" : "SELECT g.group_name AS item_group, SUM(i.quantity * i.rate) AS total_amount FROM sale_invoice_items i JOIN products p ON i.product_id = p.product_id  JOIN product_groups g ON p.product_group_id = g.product_group_id  JOIN sale_invoice_orders o ON i.sale_invoice_id = o.sale_invoice_id  WHERE o.invoice_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)  GROUP BY g.group_name ORDER BY total_amount DESC LIMIT 5;",

"Top_5_Sold_Items_In_Current_FY" : "WITH financial_year AS (SELECT CASE WHEN MONTH(CURDATE()) < 4 THEN DATE(CONCAT(YEAR(CURDATE()) - 1, '-04-01')) ELSE DATE(CONCAT(YEAR(CURDATE()), '-04-01')) END AS fy_start_date, CASE WHEN MONTH(CURDATE()) < 4 THEN DATE(CONCAT(YEAR(CURDATE()), '-03-31')) ELSE DATE(CONCAT(YEAR(CURDATE()) + 1, '-03-31')) END AS fy_end_date) SELECT p.name AS item_name, SUM(i.quantity * i.rate) AS total_amount FROM sale_invoice_items i JOIN sale_invoice_orders o ON i.sale_invoice_id = o.sale_invoice_id JOIN products p ON i.product_id = p.product_id CROSS JOIN financial_year fy WHERE o.invoice_date BETWEEN fy.fy_start_date AND fy.fy_end_date GROUP BY p.name ORDER BY total_amount DESC LIMIT 5;",

"Sales_Order_Trend_Graph" : "WITH MonthlySalesData AS (SELECT DATE_FORMAT(so.order_date, '%M-%Y') AS month_name_year, COUNT(DISTINCT so.sale_order_id) AS total_sales_orders, COUNT(DISTINCT si.sale_order_id) AS invoices_converted, COUNT(DISTINCT sr.sale_invoice_id) AS returns_converted  FROM sale_orders so LEFT JOIN sale_invoice_orders si ON so.sale_order_id = si.sale_order_id LEFT JOIN sale_return_orders sr ON si.sale_invoice_id = sr.sale_invoice_id  WHERE so.order_date >= CURDATE() - INTERVAL 12 MONTH  GROUP BY month_name_year )SELECT month_name_year, total_sales_orders, invoices_converted, returns_converted, (total_sales_orders - invoices_converted - returns_converted) AS pending_sales_orders FROM MonthlySalesData ORDER BY STR_TO_DATE(month_name_year, '%M-%Y') DESC;",

"Product_Not_Sold_In_30_Days_For_Table" : "SELECT p.name AS product_name FROM products p JOIN product_groups pg ON p.product_group_id = pg.product_group_id WHERE NOT EXISTS ( SELECT 1 FROM sale_invoice_items si WHERE si.product_id = p.product_id AND si.created_at >= DATE_SUB(CURDATE(), INTERVAL 30 DAY) );",

"Customers_With_No_Sales_In_30_Days_For_Table" : "SELECT c.name AS customer_name FROM customers c WHERE NOT EXISTS ( SELECT 1  FROM sale_orders o WHERE o.customer_id = c.customer_id AND o.order_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY) );",

"Pending_For_Table" : "SELECT 'Sales Order' AS order_type, COALESCE(count(order_no), 0) AS order_count, COALESCE(sum(item_value), 0) AS total_value FROM sale_orders WHERE order_status_id = (SELECT order_status_id FROM order_statuses WHERE status_name = 'Pending') UNION SELECT 'Sales Invoice' AS order_type, COALESCE(count(invoice_no), 0) AS order_count, COALESCE(sum(item_value), 0) AS total_value FROM sale_invoice_orders WHERE order_status_id = (SELECT order_status_id FROM order_statuses WHERE status_name = 'Pending') UNION SELECT 'Purchase Order' AS order_type, COALESCE(count(purchase_order_id), 0) AS order_count, COALESCE(sum(item_value), 0) AS total_value FROM purchase_orders WHERE order_status_id = (SELECT order_status_id FROM order_statuses WHERE status_name = 'Pending') UNION SELECT 'Purchase Invoice' AS order_type, COALESCE(count(purchase_invoice_id), 0) AS order_count, COALESCE(sum(item_value), 0) AS total_value FROM purchase_invoice_orders WHERE order_status_id = (SELECT order_status_id FROM order_statuses WHERE status_name = 'Pending');"
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
