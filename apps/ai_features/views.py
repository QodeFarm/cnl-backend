from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from config.utils_methods import build_response
from apps.ai_features.utils import parse_date_params
from apps.ai_features.services.low_stock_service import get_low_stock_products
from apps.ai_features.services.stock_forecast_service import get_at_risk_stock_forecast
from apps.ai_features.services.debt_defaulter_service import get_debt_defaulters
from apps.ai_features.services.inactive_customer_service import get_inactive_customers
from apps.ai_features.services.dead_stock_service import get_dead_stock
from apps.ai_features.services.best_vendor_service import get_best_vendors
from apps.ai_features.services.work_order_suggestion_service import get_work_order_suggestions, create_work_order
from apps.ai_features.services.auto_purchase_order_service import get_reorder_suggestions, create_purchase_order
from apps.ai_features.services.demand_forecast_service import get_demand_forecast
from apps.ai_features.services.churn_risk_service import get_churn_risk
from apps.ai_features.services.cash_flow_forecast_service import get_cash_flow_forecast
from apps.ai_features.services.expense_anomaly_service import get_expense_anomalies
from apps.ai_features.services.price_variance_service import get_price_variance
from apps.ai_features.services.raw_material_forecast_service import get_raw_material_forecast
from apps.ai_features.services.profit_margin_service import get_profit_margin_analysis
from apps.ai_features.services.money_bleeding_service import get_money_bleeding_summary
from apps.ai_features.services.seasonality_heatmap_service import get_seasonality_heatmap
from apps.ai_features.services.what_if_simulator_service import get_what_if_simulation
from apps.ai_features.serializers import (
    LowStockProductSerializer, StockForecastAlertSerializer,
    DebtDefaulterSerializer, InactiveCustomerSerializer,
    DeadStockSerializer, BestVendorSerializer,
    WorkOrderSuggestionSerializer, WorkOrderCreatedSerializer,
    ReorderSuggestionSerializer, PurchaseOrderCreatedSerializer,
    DemandForecastSerializer, ChurnRiskSerializer,
    CashFlowForecastSerializer, ExpenseAnomalySerializer,
    PriceVarianceSerializer, RawMaterialForecastSerializer,
    ProfitMarginSerializer, MoneyBleedingCategorySerializer,
    SeasonalityProductSerializer,
    WhatIfMaterialSerializer,
)
import logging

logger = logging.getLogger(__name__)


class LowStockAlertView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            queryset = get_low_stock_products()
            serializer = LowStockProductSerializer(queryset, many=True)
            data = serializer.data
            critical = sum(1 for p in data if p['severity'] == 'critical')
            high = sum(1 for p in data if p['severity'] == 'high')
            medium = sum(1 for p in data if p['severity'] == 'medium')
            response = build_response(
                len(data),
                "Success",
                data,
                status.HTTP_200_OK
            )
            response.data['summary'] = {
                'critical': critical,
                'high': high,
                'medium': medium,
            }
            return response
        except Exception as e:
            logger.exception(f"Low stock alert error: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)


class StockForecastAlertView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            period_days = int(request.query_params.get('period_days', 180))
            from_date, to_date = parse_date_params(request)
            at_risk, summary, period_info = get_at_risk_stock_forecast(period_days, from_date=from_date, to_date=to_date)
            serializer = StockForecastAlertSerializer(at_risk, many=True)
            response = build_response(
                len(serializer.data),
                "Success",
                serializer.data,
                status.HTTP_200_OK
            )
            response.data['summary'] = summary
            response.data['period_info'] = period_info
            return response
        except Exception as e:
            logger.exception(f"Stock forecast alert error: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)


class DebtDefaulterView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            from_date, to_date = parse_date_params(request)
            defaulters = get_debt_defaulters(from_date=from_date, to_date=to_date)
            serializer = DebtDefaulterSerializer(defaulters, many=True)
            data = serializer.data
            critical = sum(1 for d in data if d['risk_level'] == 'CRITICAL')
            warning = sum(1 for d in data if d['risk_level'] == 'WARNING')
            mild = sum(1 for d in data if d['risk_level'] == 'MILD')
            total_overdue = sum(d['total_overdue_amount'] for d in data)
            response = build_response(
                len(data),
                "Success",
                data,
                status.HTTP_200_OK
            )
            response.data['summary'] = {
                'critical': critical,
                'warning': warning,
                'mild': mild,
                'total_overdue_amount': round(total_overdue, 2),
            }
            return response
        except Exception as e:
            logger.exception(f"Debt defaulter alert error: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)


class InactiveCustomerView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            inactive_days = int(request.query_params.get('inactive_days', 180))
            from_date, to_date = parse_date_params(request)
            customers = get_inactive_customers(inactive_days, from_date=from_date, to_date=to_date)
            serializer = InactiveCustomerSerializer(customers, many=True)
            data = serializer.data
            lost = sum(1 for c in data if c['risk_level'] == 'LOST')
            critical = sum(1 for c in data if c['risk_level'] == 'CRITICAL')
            warning = sum(1 for c in data if c['risk_level'] == 'WARNING')
            at_risk = sum(1 for c in data if c['risk_level'] == 'AT_RISK')
            response = build_response(
                len(data),
                "Success",
                data,
                status.HTTP_200_OK
            )
            response.data['summary'] = {
                'lost': lost,
                'critical': critical,
                'warning': warning,
                'at_risk': at_risk,
            }
            return response
        except Exception as e:
            logger.exception(f"Inactive customer alert error: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeadStockView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            dead_days = int(request.query_params.get('dead_days', 90))
            from_date, to_date = parse_date_params(request)
            dead_stock = get_dead_stock(dead_days, from_date=from_date, to_date=to_date)
            serializer = DeadStockSerializer(dead_stock, many=True)
            data = serializer.data
            total_dead_value = sum(d['dead_stock_value'] for d in data)
            response = build_response(
                len(data),
                "Success",
                data,
                status.HTTP_200_OK
            )
            response.data['summary'] = {
                'total_dead_products': len(data),
                'total_dead_stock_value': round(total_dead_value, 2),
            }
            return response
        except Exception as e:
            logger.exception(f"Dead stock alert error: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)


class BestVendorView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            from_date, to_date = parse_date_params(request)
            results = get_best_vendors(from_date=from_date, to_date=to_date)
            serializer = BestVendorSerializer(results, many=True)
            data = serializer.data
            total_products = len(data)
            total_vendors = len(set(
                v['vendor_id']
                for item in data
                for v in item['vendors']
            ))
            response = build_response(
                total_products,
                "Success",
                data,
                status.HTTP_200_OK
            )
            response.data['summary'] = {
                'total_products_analyzed': total_products,
                'total_vendors_scored': total_vendors,
            }
            return response
        except Exception as e:
            logger.exception(f"Best vendor alert error: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)


class WorkOrderSuggestionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            suggestions = get_work_order_suggestions()
            serializer = WorkOrderSuggestionSerializer(suggestions, many=True)
            data = serializer.data
            producible = sum(1 for s in data if s['can_produce'])
            blocked = sum(1 for s in data if not s['can_produce'])
            response = build_response(
                len(data),
                "Success",
                data,
                status.HTTP_200_OK
            )
            response.data['summary'] = {
                'total_suggestions': len(data),
                'ready_to_produce': producible,
                'blocked_by_materials': blocked,
            }
            return response
        except Exception as e:
            logger.exception(f"Work order suggestion error: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, *args, **kwargs):
        try:
            items = request.data.get('items', [])
            if not items:
                return build_response(0, "No items provided", [], status.HTTP_400_BAD_REQUEST)

            created_orders = []
            errors = []
            with transaction.atomic():
                for item in items:
                    product_id = item.get('product_id')
                    quantity = item.get('quantity')
                    if not product_id or not quantity:
                        errors.append({'product_id': product_id, 'error': 'product_id and quantity are required'})
                        continue
                    try:
                        wo = create_work_order(product_id, int(quantity))
                        created_orders.append(wo)
                    except (ValueError, Exception) as ex:
                        errors.append({'product_id': product_id, 'error': str(ex)})

            serializer = WorkOrderCreatedSerializer(created_orders, many=True)
            response = build_response(
                len(created_orders),
                f"Created {len(created_orders)} work order(s)",
                serializer.data,
                status.HTTP_201_CREATED
            )
            if errors:
                response.data['errors'] = errors
            return response
        except Exception as e:
            logger.exception(f"Work order creation error: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)


class AutoPurchaseOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            suggestions = get_reorder_suggestions()
            serializer = ReorderSuggestionSerializer(suggestions, many=True)
            data = serializer.data
            total_estimated = sum(s['estimated_cost'] for s in data)
            response = build_response(
                len(data),
                "Success",
                data,
                status.HTTP_200_OK
            )
            response.data['summary'] = {
                'total_products_to_reorder': len(data),
                'total_estimated_cost': round(total_estimated, 2),
            }
            return response
        except Exception as e:
            logger.exception(f"Reorder suggestion error: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, *args, **kwargs):
        try:
            items = request.data.get('items', [])
            if not items:
                return build_response(0, "No items provided", [], status.HTTP_400_BAD_REQUEST)

            # Validate each item has required fields
            for item in items:
                if not item.get('product_id') or not item.get('vendor_id'):
                    return build_response(
                        0, "Each item requires product_id and vendor_id",
                        [], status.HTTP_400_BAD_REQUEST
                    )
                if not item.get('quantity') or not item.get('rate'):
                    return build_response(
                        0, "Each item requires quantity and rate",
                        [], status.HTTP_400_BAD_REQUEST
                    )

            created_orders = create_purchase_order(items)
            serializer = PurchaseOrderCreatedSerializer(created_orders, many=True)
            response = build_response(
                len(created_orders),
                f"Created {len(created_orders)} purchase order(s)",
                serializer.data,
                status.HTTP_201_CREATED
            )
            return response
        except ValueError as ve:
            return build_response(0, str(ve), [], status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Auto purchase order error: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)


class DemandForecastView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            period_days = int(request.query_params.get('period_days', 365))
            forecast_days = int(request.query_params.get('forecast_days', 90))
            from_date, to_date = parse_date_params(request)
            forecasts, summary = get_demand_forecast(period_days, forecast_days, from_date=from_date, to_date=to_date)
            serializer = DemandForecastSerializer(forecasts, many=True)
            response = build_response(
                len(serializer.data),
                "Success",
                serializer.data,
                status.HTTP_200_OK
            )
            response.data['summary'] = summary
            response.data['params'] = {
                'period_days': period_days,
                'forecast_days': forecast_days,
            }
            return response
        except Exception as e:
            logger.exception(f"Demand forecast error: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChurnRiskView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            period_days = int(request.query_params.get('period_days', 365))
            from_date, to_date = parse_date_params(request)
            customers, summary = get_churn_risk(period_days, from_date=from_date, to_date=to_date)
            serializer = ChurnRiskSerializer(customers, many=True)
            response = build_response(
                len(serializer.data),
                "Success",
                serializer.data,
                status.HTTP_200_OK
            )
            response.data['summary'] = summary
            response.data['params'] = {'period_days': period_days}
            return response
        except Exception as e:
            logger.exception(f"Churn risk error: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)


class CashFlowForecastView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            forecast_days = int(request.query_params.get('forecast_days', 90))
            from_date, to_date = parse_date_params(request)
            weekly_data, summary = get_cash_flow_forecast(forecast_days, from_date=from_date, to_date=to_date)
            serializer = CashFlowForecastSerializer(weekly_data, many=True)
            response = build_response(
                len(serializer.data),
                "Success",
                serializer.data,
                status.HTTP_200_OK
            )
            response.data['summary'] = summary
            return response
        except Exception as e:
            logger.exception(f"Cash flow forecast error: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExpenseAnomalyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            period_days = int(request.query_params.get('period_days', 365))
            threshold = float(request.query_params.get('threshold', 2.0))
            from_date, to_date = parse_date_params(request)
            anomalies, summary = get_expense_anomalies(period_days, threshold, from_date=from_date, to_date=to_date)
            serializer = ExpenseAnomalySerializer(anomalies, many=True)
            response = build_response(
                len(serializer.data),
                "Success",
                serializer.data,
                status.HTTP_200_OK
            )
            response.data['summary'] = summary
            response.data['params'] = {
                'period_days': period_days,
                'threshold': threshold,
            }
            return response
        except Exception as e:
            logger.exception(f"Expense anomaly error: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)


class PriceVarianceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            period_days = int(request.query_params.get('period_days', 365))
            from_date, to_date = parse_date_params(request)
            results, summary = get_price_variance(period_days, from_date=from_date, to_date=to_date)
            serializer = PriceVarianceSerializer(results, many=True)
            response = build_response(
                len(serializer.data),
                "Success",
                serializer.data,
                status.HTTP_200_OK
            )
            response.data['summary'] = summary
            response.data['params'] = {'period_days': period_days}
            return response
        except Exception as e:
            logger.exception(f"Price variance error: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)


class RawMaterialForecastView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            period_days = int(request.query_params.get('period_days', 365))
            from_date, to_date = parse_date_params(request)
            results, summary = get_raw_material_forecast(period_days, from_date=from_date, to_date=to_date)
            serializer = RawMaterialForecastSerializer(results, many=True)
            response = build_response(
                len(serializer.data),
                "Success",
                serializer.data,
                status.HTTP_200_OK
            )
            response.data['summary'] = summary
            response.data['params'] = {'period_days': period_days}
            return response
        except Exception as e:
            logger.exception(f"Raw material forecast error: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProfitMarginView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            period_days = int(request.query_params.get('period_days', 365))
            from_date, to_date = parse_date_params(request)
            results, summary = get_profit_margin_analysis(period_days, from_date=from_date, to_date=to_date)
            serializer = ProfitMarginSerializer(results, many=True)
            response = build_response(
                len(serializer.data),
                "Success",
                serializer.data,
                status.HTTP_200_OK
            )
            response.data['summary'] = summary
            response.data['params'] = {'period_days': period_days}
            return response
        except Exception as e:
            logger.exception(f"Profit margin analysis error: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)


class MoneyBleedingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            period_days = int(request.query_params.get('period_days', 365))
            from_date, to_date = parse_date_params(request)
            categories, summary = get_money_bleeding_summary(period_days, from_date=from_date, to_date=to_date)
            serializer = MoneyBleedingCategorySerializer(categories, many=True)
            response = build_response(
                len(serializer.data),
                "Success",
                serializer.data,
                status.HTTP_200_OK
            )
            response.data['summary'] = summary
            response.data['params'] = {'period_days': period_days}
            return response
        except Exception as e:
            logger.exception(f"Money bleeding summary error: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)


class SeasonalityHeatmapView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            period_months = int(request.query_params.get('period_months', 24))
            from_date, to_date = parse_date_params(request)
            results, summary = get_seasonality_heatmap(period_months, from_date=from_date, to_date=to_date)
            serializer = SeasonalityProductSerializer(results, many=True)
            response = build_response(
                len(serializer.data),
                "Success",
                serializer.data,
                status.HTTP_200_OK
            )
            response.data['summary'] = summary
            response.data['params'] = {'period_months': period_months}
            return response
        except Exception as e:
            logger.exception(f"Seasonality heatmap error: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)


class WhatIfSimulatorView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            growth_pct = int(request.query_params.get('growth_pct', 20))
            forecast_months = int(request.query_params.get('forecast_months', 3))
            period_days = int(request.query_params.get('period_days', 365))
            from_date, to_date = parse_date_params(request)
            results, summary = get_what_if_simulation(growth_pct, forecast_months, period_days, from_date=from_date, to_date=to_date)
            serializer = WhatIfMaterialSerializer(results, many=True)
            response = build_response(
                len(serializer.data),
                "Success",
                serializer.data,
                status.HTTP_200_OK
            )
            response.data['summary'] = summary
            response.data['params'] = {
                'growth_pct': growth_pct,
                'forecast_months': forecast_months,
                'period_days': period_days,
            }
            return response
        except Exception as e:
            logger.exception(f"What-If simulator error: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
