# myapp/views.py
import json
import requests
from .serializers import *
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

class TotalView(APIView):
    def post(self, request):
        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            last_cart_total_value = serializer.validated_data['last_cart_total_value']
            try:
                # Parse the JSON string
                data = json.loads(last_cart_total_value)
                total = data['Total']
                return Response({'Total': total}, status=status.HTTP_200_OK)
            except (json.JSONDecodeError, KeyError):
                return Response({'error': 'Invalid data format'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProcessOrderView(APIView):
    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            order_id = serializer.validated_data['order_id']
            cart_items = serializer.validated_data['last_cart_items']

            for item in cart_items:
                payload = {
                    "product_id": item['ProductRetailerId'],
                    "quantity": item['Quantity'],
                    "unit_price": item['Price'],
                    "order_id": order_id
                }
                try:
                    response = requests.post('https://apicore.cnlerp.com/api/v1/sales/order_items/', json=payload)
                    response.raise_for_status()  # Raises an HTTPError if the response was an HTTP error
                except requests.exceptions.RequestException as e:
                    return Response({"error": "Failed to send data", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({"status": "Success"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
