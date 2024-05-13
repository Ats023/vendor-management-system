from django.shortcuts import render
from django.core.serializers import serialize
from django.http import HttpResponse, Http404, JsonResponse
import json
from django.db.models import Avg
from datetime import datetime
from .models import Vendor, PurchaseOrder, HistoricalPerformance
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

def index(request):
    return HttpResponse('Vendor Management System with Performance Metrics')

@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def vendors(request):
    """
    Handles POST and GET requests to '/api/vendors'

    POST: parses the json string in body of request, 
          performs validation on required fields, 
          creates new vendor instance if it passes the requirements 
          else returns error.
    GET: retrieves all vendor objects and returns as json response.
    """
    if request.method == 'POST':
        vendor_details = json.loads(request.body)
        required_fields = ['name', 'contact_details', 'address', 'vendor_code', 'on_time_delivery_rate', 'quality_rating_avg', 'average_response_time', 'fulfillment_rate']
        missing_fields = [field for field in required_fields if field not in vendor_details]
        if missing_fields:
            return JsonResponse({'error':f'missing fields: {", ".join(missing_fields)}'}, status=400)
        try:
            vendor = Vendor.objects.create(
                name = vendor_details['name'],
                contact_details = vendor_details.get('contact_details'),
                address = vendor_details.get('address'),
                vendor_code = vendor_details['vendor_code'],
                on_time_delivery_rate = vendor_details.get('on_time_delivery_rate'),
                quality_rating_avg = vendor_details.get('quality_rating_avg'),
                average_response_time = vendor_details.get('average_response_time'),
                fulfillment_rate = vendor_details.get('fulfillment_rate'),
            )
            vendor.save()
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
        return JsonResponse({'message': 'vendor created'}, status=201)
    
    elif request.method == 'GET':
        vendors = Vendor.objects.all()
        vendor_list = []
        for vendor in vendors:
            vendor_data = {
                'vendor_code': vendor.vendor_code,
                'name': vendor.name,
                'contact_details': vendor.contact_details,
                'address': vendor.address,
                'on_time_delivery_rate': vendor.on_time_delivery_rate,
                'quality_rating_avg': vendor.quality_rating_avg,
                'average_response_time': vendor.average_response_time,
                'fulfillment_rate': vendor.fulfillment_rate,
            }
            vendor_list.append(vendor_data)
        return JsonResponse(vendor_list, safe=False, status=200)

@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def vendor_data(request, vendor_id):
    """
    Handles GET, PUT, DELETE requests to '/api/vendors/{vendor_id}'

    GET: retrieves vendor using vendor id, 
         if found returns vendor data as json
         else returns error.
    PUT: parses json string in body of request, 
         assigns changes to existing vendor and saves changes.
    DELETE: removes vendor from database.
    """
    try:
        vendor = Vendor.objects.get(pk=vendor_id)
    except:
        return JsonResponse({'error':'invalid vendor id'}, status=404)
    
    if request.method=='GET':
        vendor_json = {
            'vendor_code': vendor.vendor_code,
            'name': vendor.name,
            'contact_details': vendor.contact_details,
            'address': vendor.address,
            'on_time_delivery_rate': vendor.on_time_delivery_rate,
            'quality_rating_avg': vendor.quality_rating_avg,
            'average_response_time': vendor.average_response_time,
            'fulfillment_rate': vendor.fulfillment_rate,
        }
        return JsonResponse(vendor_json, safe=False, status=200)
    
    elif request.method=='PUT':
        vendor_details = json.loads(request.body)
        vendor.name = vendor_details.get('name', vendor.name)
        vendor.contact_details = vendor_details.get('contact_details', vendor.contact_details)
        vendor.address = vendor_details.get('address', vendor.address)
        vendor.vendor_code = vendor_details.get('vendor_code', vendor.vendor_code)
        vendor.on_time_delivery_rate = vendor_details.get('on_time_delivery_rate', vendor.on_time_delivery_rate)
        vendor.quality_rating_avg = vendor_details.get('quality_rating_avg', vendor.quality_rating_avg)
        vendor.average_response_time = vendor_details.get('average_response_time', vendor.average_response_time)
        vendor.fulfillment_rate = vendor_details.get('fulfillment_rate', vendor.fulfillment_rate)
        vendor.save()
        return JsonResponse({'message': 'vendor updated'}, status=200)
    
    elif request.method == 'DELETE':
        vendor.delete()
        return JsonResponse({'message': 'vendor deleted'}, status=204)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def vendor_performance(request, vendor_id):
    """
    Handles GET request to '/api/vendors/{vendor_id}/performace'

    Returns performance metrics of vendor if the vendor is found else returns error message. 
    """
    try:
        vendor = Vendor.objects.get(pk=vendor_id)
    except:
        return JsonResponse({'error':'invalid vendor id'}, status=404)
    
    if request.method == 'GET':
        vendor_json = {
            'vendor_code': vendor.vendor_code,
            'on_time_delivery_rate': vendor.on_time_delivery_rate,
            'quality_rating_avg': vendor.quality_rating_avg,
            'average_response_time': vendor.average_response_time,
            'fulfillment_rate': vendor.fulfillment_rate,
        }
        return JsonResponse(vendor_json, safe=False, status=200)

@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def purchase_orders(request):
    """
    Handles GET and POST requests to '/api/purchase_orders'

    GET: if vendor is provided in query string, e.g
         '/api/purchase_orders?vendor_id={vendor_id}'
         retrieves purchase orders filtered by given vendor id,
         else retrieves all purchase orders,
         returns list as json object.
    POST: parses json string in request body, 
          performs data validation on required fields, 
          creates instance of purchase order if it passes all requirements, 
          else returns error.
    """
    if request.method == 'GET':
        vendor_id = request.GET.get('vendor_id')
        if vendor_id:
            purchase_orders = PurchaseOrder.objects.filter(vendor=Vendor.objects.get(pk=vendor_id))
        else:
            purchase_orders = PurchaseOrder.objects.all()
        
        purchase_orders_data = [
            {
                'po_number': po.po_number,
                'vendor': po.vendor.pk,
                'order_date': po.order_date.strftime('%Y-%m-%d %H:%M:%S'),
                'delivery_date': po.delivery_date.strftime('%Y-%m-%d %H:%M:%S'),
                'items': po.items,
                'quantity': po.quantity,
                'status': po.status,
                'quality_rating': po.quality_rating,
                'issue_date': po.issue_date.strftime('%Y-%m-%d %H:%M:%S'),
                'acknowledgement_date': po.acknowledgement_date.strftime('%Y-%m-%d %H:%M:%S') if po.acknowledgement_date else None
            }
            for po in purchase_orders
        ]
        return JsonResponse(purchase_orders_data, safe=False, status=200)
    
    elif request.method == 'POST':
        po_details = json.loads(request.body)
        required_fields = ['po_number', 'vendor', 'order_date', 'delivery_date', 'items', 'quantity', 'status', 'issue_date']
        missing_fields = [field for field in required_fields if field not in    po_details]
        if missing_fields:
            return JsonResponse({'error':f'Missing fields: {", ".join(missing_fields)}'}, status=400)
        try:
            po = PurchaseOrder.objects.create(
                po_number = po_details['po_number'],
                vendor = Vendor.objects.get(pk=po_details['vendor']),
                order_date = po_details['order_date'],
                delivery_date = po_details['delivery_date'],
                items = po_details['items'],
                quantity = po_details['quantity'],
                status = po_details['status'],
                quality_rating = po_details.get('quality_rating'),
                issue_date = po_details['issue_date'],
                acknowledgement_date = po_details.get('acknowledgement_date')
            )
            po.save()
            return JsonResponse({'message':'purchase order created successfully'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def purchase_order_data(request, po_id):
    """ 
    Handles GET, PUT, DELETE requests to '/api/purchase_orders/{po_id}'

    GET: retrieves purchase order with given id.
    PUT: parses json string in request body,
         saves changes in existing purchase order.
    DELETE: removes purchase order instance from database.
    """
    try:
        po = PurchaseOrder.objects.get(pk=po_id)
    except:
        return JsonResponse({'error':'invalid purchase order id'}, status=404)
    
    if request.method == 'GET':
        po_json = {
            'po_number': po.po_number,
            'vendor': po.vendor.pk,
            'order_date': po.order_date.strftime('%Y-%m-%d %H:%M:%S'),
            'delivery_date': po.delivery_date.strftime('%Y-%m-%d %H:%M:%S'),
            'items': po.items,
            'quantity': po.quantity,
            'status': po.status,
            'quality_rating': po.quality_rating,
            'issue_date': po.issue_date.strftime('%Y-%m-%d %H:%M:%S'),
            'acknowledgement_date': po.acknowledgement_date.strftime('%Y-%m-%d %H:%M:%S') if po.acknowledgement_date else None
        }
        return JsonResponse(po_json, safe=False, status=200)
    
    elif request.method == 'PUT':
        po_details = json.loads(request.body)
        prev_status = po.status

        po.po_number = po_details.get('po_number', po.po_number)
        po.delivery_date = po_details.get('delivery_date', po.delivery_date)
        po.order_date = po_details.get('order_date', po.order_date)
        po.items = po_details.get('items', po.items)
        po.quantity = po_details.get('quantity', po.quantity)
        po.status = po_details.get('status', po.status)
        po.quality_rating = po_details.get('quality_rating', None)
        po.issue_date = po_details.get('issue_date', po.issue_date)
        po.acknowledgement_date = po_details.get('acknowledgement_date', None)
        po.save()

        if prev_status != 'completed' and po.status == 'completed':
            quality_rating_calculation(po.vendor)
            fulfillment_rate_calculation(po.vendor)

        create_historical_record(po.vendor)

        return JsonResponse({'message': 'purchase order updated'}, status=200)
    
    elif request.method == 'DELETE':
        vendor = po.vendor
        po.delete()
        calculate_average_response_time(vendor)
        fulfillment_rate_calculation(vendor)
        quality_rating_calculation(vendor)
        create_historical_record(vendor)
        return JsonResponse({'message': 'purchase order deleted'}, status=204)
    
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def acknowledge_purchase_order(request, po_id):
    """
    Updates acknowledgement date of purchase order and triggers calculation of average response time.
    """
    try:
        purchase_order = PurchaseOrder.objects.get(pk=po_id)
    except PurchaseOrder.DoesNotExist:
        return JsonResponse({'error': 'purchase order not found'}, status=404)

    if purchase_order.acknowledgement_date==None:
        purchase_order.acknowledgement_date = datetime.now()
        purchase_order.save()
        vendor = purchase_order.vendor
        calculate_average_response_time(vendor)
        create_historical_record(vendor)
        return JsonResponse({'message': 'purchase order acknowledged'}, status=200)
    else:
        return JsonResponse({'message':'purchase order already acknowledged'}, status=200)

def calculate_average_response_time(vendor):
    """
    Calculates average response time of the vendor
    """
    purchase_orders = PurchaseOrder.objects.filter(vendor=vendor, acknowledgement_date__isnull=False)
    total_response_time = sum((po.acknowledgement_date - po.issue_date).total_seconds() for po in purchase_orders)
    average_response_time = total_response_time/len(purchase_orders) if len(purchase_orders)>0 else 0
    vendor.average_response_time = average_response_time
    vendor.save()
    
def quality_rating_calculation(vendor):
    """
    Calculates average quality rating of vendor
    """
    completed_purchase_orders = PurchaseOrder.objects.filter(vendor=vendor, status='completed')
    average_quality_rating = completed_purchase_orders.aggregate(Avg('quality_rating'))['quality_rating__avg']
    vendor.quality_rating_avg = average_quality_rating if average_quality_rating!=None else 0
    vendor.save()

def fulfillment_rate_calculation(vendor):
    """
    Calculates fulfillment rate of vendor
    """
    completed_po_count = PurchaseOrder.objects.filter(vendor=vendor, status='completed').count()
    total_po_count = PurchaseOrder.objects.filter(vendor=vendor).count()
    fulfillment_rate = completed_po_count / total_po_count if total_po_count!=0 else 0
    vendor.fulfillment_rate = fulfillment_rate
    vendor.save()

def create_historical_record(vendor):
    """
    Creates a historical performance instance for vendor with current date
    """
    new_record = HistoricalPerformance.objects.create(
        vendor = vendor,
        date = datetime.now(),
        on_time_delivery_rate = vendor.on_time_delivery_rate,
        quality_rating_avg = vendor.quality_rating_avg,
        average_response_time = vendor.average_response_time,
        fulfillment_rate = vendor.fulfillment_rate
    )
    new_record.save()
