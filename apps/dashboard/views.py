from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .utils import query, execute_query

class DynamicQueryAPIView(APIView):
    """Fetch data based on dynamic endpoints and execute SQL queries."""

    def get(self, request, query_name):
        #print('++++>>>', query_name)
        if query_name not in query:
            return Response(
                {"error": f"No query found for {query_name}."},
                status=status.HTTP_404_NOT_FOUND
            )

        sql_query = query[query_name]
        #print('++++>>>', sql_query)
        results = execute_query(sql_query)

        if "error" in results:
            return Response(results, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(results, status=status.HTTP_200_OK)

