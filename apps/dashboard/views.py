from django.shortcuts import render
from rest_framework.views import APIView
from decimal import Decimal
from django.db import connection
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import ReportDefinition
from .serializers import ReportDefinitionSerializer
import json
from collections import defaultdict
from django.conf import settings
from .utils import (prepare_monthly_sales_data, prepare_trend_data, prepare_high_selling_data, prepare_revenue_data, prepare_revenue_series,)

# Create your views here.

class dashoardView(APIView):
    def get(self, request, **kwargs):
        try:
            report = ReportDefinition.objects.get(
                query_name=kwargs.get('query_name'))
            serializer = ReportDefinitionSerializer(report).data
            with connection.cursor() as cursor:
                query = serializer.get('query')
                cursor.execute(query)
                results = cursor.fetchall()
            
            if 'monthly-sales' == kwargs.get('query_name'):
                response_data = prepare_monthly_sales_data(results)

            elif kwargs.get('query_name') in ['sales-order-trend-daily', 'sales-order-trend-weekly', 'sales-order-trend-monthly']:
                response_data = prepare_trend_data(
                    results,
                    labels=["dates", "order_count", "invoices", "returns"],
                    data_indexes=[0, 1, 2, 3]
                )

            elif 'Sales-Performance-by-Customer' == kwargs.get('query_name'):
                customers = set()
                categories = set()
                sales_data = defaultdict(lambda: defaultdict(float))

                for customer, category, sales in results:
                    customers.add(customer)
                    categories.add(category)
                    sales_data[customer][category] = float(sales)

                sorted_customers = sorted(customers)
                sorted_categories = sorted(categories)

                response_data = {
                    "cust_name_list": sorted_customers,
                    "prod_category_list": sorted_categories,
                    "price_list": [
                        [sales_data[customer].get(category, 0.0) for customer in sorted_customers]
                        for category in sorted_categories
                    ]
                }

            elif 'High-Selling-Products-monthly' == kwargs.get('query_name'):
                months = [
                    "January", "February", "March", "April", "May", "June",
                    "July", "August", "September", "October", "November", "December"
                ]
                response_data = prepare_high_selling_data(results, months)

            elif 'High-Selling-Products-weekly' == kwargs.get('query_name'):
                # Assuming results includes weeks in chronological order
                weeks = sorted(set(entry[0] for entry in results))
                response_data = prepare_high_selling_data(results, weeks)

            elif 'High-Selling-Products-yearly' == kwargs.get('query_name'):
                years = sorted(set(entry[0] for entry in results))
                response_data = prepare_high_selling_data(results, years)

            revenue_map = {
                'todays_revenue': "todays_revenue",
                'yesterday_revenue': "yesterday_revenue",
                'last_7_days_revenue': "last_7_days_revenue",
                'last_12_months_revenue': "Last Year"
            }
            query_name = kwargs.get('query_name')

            if query_name in revenue_map:
                response_data = prepare_revenue_data(results, revenue_map[query_name])


            elif kwargs.get('query_name') in ['current_month_revenue', 'last_month_revenue']:
                response_data = {
                    "label": results[0][0],
                    "revenue": results[0][1]
                }             

            elif kwargs.get('query_name')in ['last_3_months_revenue', 'last_6_months_revenue', 'current_quarter_revenue', 'year_to_current_date_revenue']:
                response_data = prepare_revenue_series(results)
            print('==>',response_data)

            return Response(response_data, status=status.HTTP_200_OK)
        
        except ReportDefinition.DoesNotExist:
            return Response({"error": "Report not found."}, status=status.HTTP_404_NOT_FOUND)


class DatabaseView(APIView):
    '''this class is used for fetch data from a specific table, fetch all tables name, table structure, '''
    def get(self, request, table_name=None):
        # Fetch structure of a specific table
        if table_name:
            database_name = settings.DATABASES['default']['NAME']
            try:
                with connection.cursor() as cursor:
                    # Fetch column names
                    cursor.execute(f"SELECT * FROM {table_name}")
                    columns = [col[0] for col in cursor.description]
                    data = cursor.fetchall()  # Not used in the response
                    
                    # Fetch related table columns
                    query = f"""
                        SELECT COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
                        FROM information_schema.KEY_COLUMN_USAGE
                        WHERE TABLE_SCHEMA = '{database_name}'
                        AND TABLE_NAME = '{table_name}'
                        AND REFERENCED_TABLE_NAME IS NOT NULL;
                    """
                    cursor.execute(query)
                    relations = [
                        f"{table_name}.{row[0]} = {row[1]}.{row[2]}"
                        for row in cursor.fetchall()
                    ]

                    return Response({"Relation": relations, "columns": columns}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch all table names
        with connection.cursor() as cursor:
            # Access the database name
            database_name = settings.DATABASES['default']['NAME']
            fetch_Table_name_query = f"SELECT table_name FROM information_schema.tables where table_schema = '{database_name}'"
            cursor.execute(fetch_Table_name_query)
            tables = [row[0] for row in cursor.fetchall()]
            return Response({"tables" : tables}, status=status.HTTP_200_OK)


class ExecuteQueryView(APIView):
    '''This class is used for executes the query'''
    def post(self, request):
        query = request.data.get('query', None)
        if not query:
            return Response({"error": "Query is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                columns = [col[0] for col in cursor.description]
                results = cursor.fetchall()
                data = [dict(zip(columns, row)) for row in results]
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ReportDefinitionView(APIView):
    '''This class is used for save custom query'''
    def post(self, request):
        serializer = ReportDefinitionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response("Query Saved Successfully!", status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ProcessQueryResultsView(APIView):
    '''This class is used for processing query results from ExecuteQueryView'''
    
    def post(self, request):
        query = request.data.get('query', None)
        if not query:
            return Response({"error": "Query is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                columns = [col[0] for col in cursor.description]
                results = cursor.fetchall()
                data = [dict(zip(columns, row)) for row in results]

            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
