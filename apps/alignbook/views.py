import uuid
from django.conf import settings
import os
from uuid import uuid4
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
import json


from datetime import datetime
from .serializers import PhoneNumberSerializer
from reportlab.lib.pagesizes import letter # type: ignore
from reportlab.pdfgen import canvas # type: ignore
from django.http import FileResponse, HttpResponse
from reportlab.lib import colors # type: ignore


from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer# type: ignore
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle # type: ignore


class VoucherView(APIView):
    def post(self, request):
        voucher_value = request.data.get('voucher_value')

        if not voucher_value.strip():
            return Response({'error': 'Voucher value is required'}, status=status.HTTP_400_BAD_REQUEST)

        url = "https://service.alignbooks.com/ABReportService.svc/GetReportData"
        payload = {
                    "report_type":4444,
                        "filter_data":{
                            "period_from":{
                                "name":"Date_From",
                                "applicable":True,
                                "caption":"Period",
                                "master_list_type":0,
                                "multi_select":True,
                                "value":"2024-05-24 00:11:00"
                            },
                            "period_to":{
                                "name":"Date_To",
                                "applicable":True,
                                "caption":"Period",
                                "master_list_type":0,
                                "multi_select":True,
                                "value":"2024-05-24 00:11:00"
                            },
                            "Pending":{
                                "name":"Combo_Pending",
                                "applicable":False,
                                "caption":"",
                                "master_list_type":0,
                                "multi_select":True,
                                "value":"2"
                            },
                            "txt_misc_1":{
                                "name":"Text_VoucherNo",
                                "applicable":True,
                                "caption":"",
                                "master_list_type":0,
                                "multi_select":False,
                                "value":voucher_value
                            },
                            "location":{
                                "name":"Text_VoucherNo",
                                "applicable":False,
                                "caption":"",
                                "master_list_type":0,
                                "multi_select":True,
                                "value":""
                            }
                        }
                    }
        headers =  {"username": "narayananbkr@gmail.com" ,
                     "apikey": "db43745e-9890-11ee-b041-005056a52680" ,
                     "company_id": "2a686e75-2e22-4147-8c61-1c0ebcb2f517" ,
                     "enterprise_id": "e4063c5d-79c1-49de-aef1-7fcbcd0a9eb2" ,
                     "user_id": "4861b274-0ed1-4632-a34b-1a2ec16c45f0" ,
                     "Content-Type": "application/json"} 

        try:
                api_response = requests.post(url, data=json.dumps(payload), headers=headers)
                api_response.raise_for_status()
        except requests.exceptions.RequestException as e:
                return Response({'error': str(e)}, status=status.HTTP_502_BAD_GATEWAY)

        response_data = api_response.json()
        json_data_table = None
        party = "default"
        delivery_date = "default"
        invoice_no = None
        extracted_values = []
        if response_data:
            if response_data["JsonDataTable"]:
                json_data_table = json.loads(response_data["JsonDataTable"])
                if json_data_table[0]["Party"] is not None:
                     party = json_data_table[0]["Party"]
                if json_data_table[0]["delivery_date"] is not None:
                     delivery_date = json_data_table[0]["delivery_date"]

                if json_data_table[0]["invoice_no"] is None:
                    invoice_no = "Processing"                         
                else:
                    invoice_no = "Ready to dispatch"
                
                extracted_values.append({
                'party': party,
                'delivery_date':delivery_date,  
                'invoice_no' : invoice_no                 
                })

        return Response({"response_data" : extracted_values}, status=status.HTTP_200_OK)        
            
#==============================================================================================================

class FetchOutstandingLCView(APIView):
    def post(self, request):
        serializer = PhoneNumberSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']

            # Calling ShortList_Customer API 
            api_url = "https://service.alignbooks.com/ABDataService.svc/ShortList_Customer" 

            headers = {"username": "narayananbkr@gmail.com" ,
                     "apikey": "db43745e-9890-11ee-b041-005056a52680" ,
                     "company_id": "2a686e75-2e22-4147-8c61-1c0ebcb2f517" ,
                     "enterprise_id": "e4063c5d-79c1-49de-aef1-7fcbcd0a9eb2" ,
                     "user_id": "4861b274-0ed1-4632-a34b-1a2ec16c45f0" ,
                     "Content-Type": "application/json"} 

            body = {"new_id": ""}

            # Send a POST request to the API
            response_1 = requests.post(api_url, headers=headers, json=body)

            if response_1.status_code == 200:
                response_data = response_1.json()
                json_data_table = response_data.get("JsonDataTable")

                if json_data_table:
                    data = json.loads(json_data_table)
                    for item in data:
                        if item["phone"] == phone_number:
                            user_id = item["id"]
                            break
                    else:
                        return Response({"error": "Phone number not found"}, status=status.HTTP_404_NOT_FOUND)  

                    # Calling fetch-outstanding-lc API
                    second_api_url = "https://service.alignbooks.com/ABReportService.svc/GetReportData"
                    second_body = {
                                        "report_type": 4036,
                                        "filter_data": {
                                            "date_time_at_client": "2024-05-27 10:14:54",
                                            "voucher_no": {
                                            "name": "Text_VoucherNo",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "cmb_misc_2": {
                                            "name": "Combo_Misc2",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "abcrm_contact": {
                                            "name": "Text_ABCRM_Contact",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "txt_list_1": {
                                            "name": "Text_List1",
                                            "applicable": True,
                                            "caption": "Route Map",
                                            "master_list_type": 199,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "party_category": {
                                            "name": "Text_PartyCategory",
                                            "applicable": True,
                                            "caption": "Party Category",
                                            "master_list_type": 23,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "print_on_different_page": {
                                            "name": "None",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "period_from": {
                                            "name": "Date_From",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "period_to": {
                                            "name": "Date_To",
                                            "applicable": True,
                                            "caption": "To Date",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": datetime.now().strftime("%Y-%m-%d"),
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "location": {
                                            "name": "Text_Location",
                                            "applicable": True,
                                            "caption": "Branch",
                                            "master_list_type": 39,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "counter": {
                                            "name": "Text_Counter",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "warehouse": {
                                            "name": "Text_Warehouse",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "to_location": {
                                            "name": "Text_ToLocation",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "to_warehouse": {
                                            "name": "Text_ToWarehouse",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "party": {
                                            "name": "Text_Party",
                                            "applicable": True,
                                            "caption": "Customer",
                                            "master_list_type": 41,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": user_id, 
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "sub_party": {
                                            "name": "Text_SubParty",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "ledger": {
                                            "name": "Text_Ledger",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "gstin": {
                                            "name": "Text_GSTIN",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "sub_ledger": {
                                            "name": "Text_SubLedger",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "item_group": {
                                            "name": "Text_ItemGroup",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "item": {
                                            "name": "Text_Item",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "sub_item": {
                                            "name": "Text_SubItem",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "salesman": {
                                            "name": "Text_Salesman",
                                            "applicable": True,
                                            "caption": "Salesman",
                                            "master_list_type": 36,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "trans_salesman": {
                                            "name": "Text_TransSalesman",
                                            "applicable": True,
                                            "caption": "Transaction Salesman",
                                            "master_list_type": 36,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "agent": {
                                            "name": "Text_Agent",
                                            "applicable": False,
                                            "caption": "Agent",
                                            "master_list_type": 17,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "trans_agent": {
                                            "name": "Text_TransAgent",
                                            "applicable": False,
                                            "caption": "Transaction Agent",
                                            "master_list_type": 17,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "territory": {
                                            "name": "Text_Territory",
                                            "applicable": True,
                                            "caption": "Territory",
                                            "master_list_type": 9,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "document_categories": {
                                            "name": "Text_DocumentCategory",
                                            "applicable": False,
                                            "caption": "Document Categories",
                                            "master_list_type": 20,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "ledger_attribute1": {
                                            "name": "Text_LedgerAttribute1",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "ledger_attribute2": {
                                            "name": "Text_LedgerAttribute2",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "ledger_attribute3": {
                                            "name": "Text_LedgerAttribute3",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "ledger_attribute4": {
                                            "name": "Text_LedgerAttribute4",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "ledger_attribute5": {
                                            "name": "Text_LedgerAttribute5",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "item_attribute1": {
                                            "name": "Text_ItemAttribute1",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "item_attribute2": {
                                            "name": "Text_ItemAttribute2",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "item_attribute3": {
                                            "name": "Text_ItemAttribute3",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "item_attribute4": {
                                            "name": "Text_ItemAttribute4",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "item_attribute5": {
                                            "name": "Text_ItemAttribute5",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "fixed_asset_attribute1": {
                                            "name": "Text_FixedAssetAttribute1",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "fixed_asset_attribute2": {
                                            "name": "Text_FixedAssetAttribute2",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "fixed_asset_attribute3": {
                                            "name": "Text_FixedAssetAttribute3",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "fixed_asset_attribute4": {
                                            "name": "Text_FixedAssetAttribute4",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "fixed_asset_attribute5": {
                                            "name": "Text_FixedAssetAttribute5",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "item_master_attribute1": {
                                            "name": "Text_ItemMasterAttribute1",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "item_master_attribute2": {
                                            "name": "Text_ItemMasterAttribute2",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "item_master_attribute3": {
                                            "name": "Text_ItemMasterAttribute3",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "item_master_attribute4": {
                                            "name": "Text_ItemMasterAttribute4",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "item_master_attribute5": {
                                            "name": "Text_ItemMasterAttribute5",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "timesheet_attribute1": {
                                            "name": "Text_TimesheetAttribute1",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "timesheet_attribute2": {
                                            "name": "Text_TimesheetAttribute2",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "timesheet_attribute3": {
                                            "name": "Text_TimesheetAttribute3",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "timesheet_attribute4": {
                                            "name": "Text_TimesheetAttribute4",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "timesheet_attribute5": {
                                            "name": "Text_TimesheetAttribute5",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "sub_item_master_attribute1": {
                                            "name": "Text_SubItemMasterAttribute1",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "sub_item_master_attribute2": {
                                            "name": "Text_SubItemMasterAttribute2",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "sub_item_master_attribute3": {
                                            "name": "Text_SubItemMasterAttribute3",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "sub_item_master_attribute4": {
                                            "name": "Text_SubItemMasterAttribute4",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "sub_item_master_attribute5": {
                                            "name": "Text_SubItemMasterAttribute5",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "taxcode": {
                                            "name": "Text_Taxcode",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "company": {
                                            "name": "Text_Company",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "party_ledger": {
                                            "name": "Text_PartyGL",
                                            "applicable": True,
                                            "caption": "Party GL",
                                            "master_list_type": 96,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "item_type": {
                                            "name": "CheckedCombo_ItemType",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 8002,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "salary_wages": {
                                            "name": "CheckedCombo_SalaryWages",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 8006,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "stock_location": {
                                            "name": "Combo_StockLocation",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "document_status": {
                                            "name": "CheckedCombo_DocumentStatus",
                                            "applicable": True,
                                            "caption": "Document Status",
                                            "master_list_type": 8000,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "4,0,2,3",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "approval_status": {
                                            "name": "CheckedCombo_ApprovalStatus",
                                            "applicable": True,
                                            "caption": "Approval Status",
                                            "master_list_type": 8001,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "1",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "gst_type": {
                                            "name": "CheckedCombo_GSTType",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "skip_zero": {
                                            "name": "Check_SkipZero",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "chk_misc_1": {
                                            "name": "Check_Misc1",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "chk_misc_2": {
                                            "name": "Check_Misc2",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "txt_misc_1": {
                                            "name": "Text_Misc1",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "cmb_misc_1": {
                                            "name": "Combo_Misc1",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "contra_gl": {
                                            "name": "Text_ContraGL",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "contra_party": {
                                            "name": "Text_ContraParty",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "user": {
                                            "name": "Text_User",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "due_date": {
                                            "name": "Date_DueDate",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "Pending": {
                                            "name": "Combo_Pending",
                                            "applicable": True,
                                            "caption": "Pending",
                                            "master_list_type": 8016,
                                            "multi_select": False,
                                            "sequence": 0,
                                            "value": "0",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "ledger_group": {
                                            "name": "Text_LedgerGroup",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "depreciation_rule": {
                                            "name": "Combo_DepreciationRule",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 8017,
                                            "multi_select": False,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "valuation_method": {
                                            "name": "Combo_ValuationMethod",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 8018,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "cb_ledger": {
                                            "name": "Text_CBLedger",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "currency": {
                                            "name": "Text_Currency",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "contra_cb_gl": {
                                            "name": "Text_ContraCBLedger",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "tds_section": {
                                            "name": "Text_TDSSection",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "item_category": {
                                            "name": "Text_ItemCategory",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "asset_no": {
                                            "name": "Text_AssetNo",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "employee": {
                                            "name": "Text_Employee",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "department": {
                                            "name": "Text_Department",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "designation": {
                                            "name": "Text_Designation",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "hsn_code": {
                                            "name": "Text_HSNCode",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "month": {
                                            "name": "Combo_Month",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 8007,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "year": {
                                            "name": "Combo_Year",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 8008,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType": 0
                                            },
                                            "vtype": {
                                            "name": "Combo_VType",
                                            "applicable": False,
                                            "caption": "",
                                            "master_list_type": 0,
                                            "multi_select": True,
                                            "sequence": 0,
                                            "value": "",
                                            "parentName": "",
                                            "parentFieldName": "",
                                            "vType":0
                                            }
                                        }
                                        }

                    response_2 = requests.post(second_api_url, headers=headers, json=second_body)

                    if response_2.status_code == 200:
                        response_data_2 = response_2.json()
                        json_data_table_2 = response_data_2.get("JsonDataTable")

                        if json_data_table_2:
                            #string ==> json
                            data_2 = json.loads(json_data_table_2)

                            if isinstance(data_2, list) and len(data_2) > 0:
                                 party_name = data_2[0].get("party_name", "Unknown")
                                 
                                # Define the data for the table
                                 table_data = [
                                    ["IDX","Date", "Voucher", "Debit", "Credit", "Balance"]
                                ]
                                 for idx, record in enumerate(data_2[-25:][::-1], start=1):
                                    outstanding_lc = record.get("outstanding_lc", 0)
                                    debit = outstanding_lc if outstanding_lc > 0 else 0
                                    credit = -outstanding_lc if outstanding_lc < 0 else 0
                                    row = [
                                        idx,
                                        datetime.strptime(record.get("bill_date", ""), "%Y-%m-%dT%H:%M:%S").strftime("%d/%m/%Y") if record.get("bill_date") else "",
                                        record.get("bill_no", ""),
                                        debit,
                                        credit,
                                        record.get("outstanding_lc_running", ""),                                       
                                    ]
                                    table_data.append(row)

                                # Generate PDF with table
                                 pdf_filename = "Account_ledger_" +party_name.replace(' ' ,'_')+"_"+uuid.uuid4().hex[:6]+".pdf"
                                 pdf_path = os.path.join(settings.MEDIA_ROOT, pdf_filename)
 
                                 doc = SimpleDocTemplate(pdf_path, pagesize=letter)
                                 elements = []
 
                                 # Add heading
                                 styles = getSampleStyleSheet()
                                 bold_style = ParagraphStyle(name='Bold', parent=styles['Normal'], fontName='Helvetica-Bold')
                                 heading = Paragraph(f"Rudhra Industries", styles['Title'])
                                 additional_text = Paragraph(f"Account Ledger: {party_name}", bold_style)  
                                 
                                 # Create a table to hold the heading and additional text side by side
                                 header_table = Table([[heading], [additional_text]])
                                 header_table.setStyle(TableStyle([
                                     ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                     ('LEFTPADDING', (0, 0), (-1, -1), 50),  # Adjust horizontal position
                                     ('RIGHTPADDING', (0, 0), (-1, -1), 40),  # Adjust horizontal position
                                    
                                 ]))
                                 
                                 elements.append(header_table)
                                 elements.append(Spacer(1, 12))
                                 
                                 # Create the table with styling
                                 main_table = Table(table_data, colWidths=[30, 60, 70, 60, 65, 70])
                                 style = TableStyle([
                                     ('BACKGROUND', (0, 0), (-1, 0), colors.grey), # Header background color
                                     ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke), # Header text color
                                     ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center align all cells
                                     ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), 
                                     ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                     ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                     ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                 ])
                                 main_table.setStyle(style)
 
                                 elements.append(main_table)
                                 doc.build(elements)
 
                                 pdf_url = request.build_absolute_uri(f"{settings.MEDIA_URL}{pdf_filename}")
                                 
                                 return Response({"pdf_url": pdf_url}, status=status.HTTP_200_OK)
                            else:
                                return Response({"error": "Invalid data format in JsonDataTable field"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                        else:
                            return Response({"error": "JsonDataTable field is empty in the fetch-outstanding-lc API response"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    else:
                        return Response({"error": f"Failed to call fetch-outstanding-lc API. Status code: {response_2.status_code}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    return Response({"error": "Phone number not found"}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({"error": "JsonDataTable field is empty in the ShortList_Customer API response"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"error": f"Failed to call ShortList_Customer API. Status code: {response_1.status_code}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)