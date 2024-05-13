from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Vendor, PurchaseOrder, HistoricalPerformance
from datetime import date, datetime
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
import json

class VendorAPITests(TestCase):
    """
    Tests vendor profile management api endpoints
    """
    def setUp(self):
        self.client = APIClient()
        # Create a test user and generate token
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token = Token.objects.create(user=self.user)
        # Create two dummy vendors
        Vendor.objects.create(
            name='Test Vendor 1',
            contact_details='Contact details 1',
            address='Address 1',
            vendor_code='TEST001',
            on_time_delivery_rate=0.95,
            quality_rating_avg=4.5,
            average_response_time=2.5,
            fulfillment_rate=0.98
        )
        Vendor.objects.create(
            name='Test Vendor 2',
            contact_details='Contact details 1',
            address='Address 2',
            vendor_code='TEST002',
            on_time_delivery_rate=0.95,
            quality_rating_avg=4.5,
            average_response_time=2.5,
            fulfillment_rate=0.98
        )
    
    def test_unauthenticated_request(self):
        # Make GET request to the API endpoint without authentication
        response = self.client.get('/api/vendors/')
        # Check if the response status code is 401 (unauthorized)
        self.assertEqual(response.status_code, 401)
    
    def test_get_vendors_list(self):
        """
        Tests GET request to '/api/vendors'
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.get(reverse('vendors'))
        #check response status
        self.assertEqual(response.status_code, 200) 
        #check number of vendors returned
        self.assertEqual(len(response.json()),2) 

    def test_create_vendor(self):
        """
        Tests POST request to 'api/vendors'
        """
        data = {
            'name': 'Test Vendor 3',
            'contact_details': 'Test Contact Details',
            'address': 'Test Address',
            'vendor_code': 'TEST003',
            'on_time_delivery_rate': 0.95,
            'quality_rating_avg': 4.5,
            'average_response_time': 2.5,
            'fulfillment_rate': 0.98
        }
        data = json.dumps(data)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.post(reverse('vendors'), data, content_type='application/json')
        #check response status
        self.assertEqual(response.status_code, 201) 
        #check if new vendor is present in test database
        self.assertTrue(Vendor.objects.filter(vendor_code='TEST003').exists())
    
    def test_retrieve_vendor(self):
        """
        Tests GET request to '/api/vendors/{vendor_id}'
        """
        vendor_id = Vendor.objects.first().vendor_code
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.get(reverse('vendor_data', args=[vendor_id]))
        #check response status
        self.assertEqual(response.status_code, 200)
        #check if 'vendor_code' matches requested vendor id
        self.assertEqual(response.json()['vendor_code'], vendor_id)
        #check if all attributes of vendor model is returned
        self.assertEqual(len(response.json()),8)

    def test_update_vendor(self):
        """
        Tests PUT request to '/api/vendors/{vendor_id}
        """
        vendor_id = Vendor.objects.first().vendor_code
        data = {'name': 'Updated Vendor Name'}
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.put(reverse('vendor_data', args=[vendor_id]), data=json.dumps(data), content_type='application/json')
        #check response status
        self.assertEqual(response.status_code, 200)
        #check if vendor name is changed
        self.assertEqual(Vendor.objects.get(vendor_code=vendor_id).name, 'Updated Vendor Name')
        #check if other vendor attributes are same
        self.assertEqual(Vendor.objects.get(vendor_code=vendor_id).address, 'Address 1')
        self.assertEqual(Vendor.objects.get(vendor_code=vendor_id).contact_details, 'Contact details 1')
    
    def test_delete_vendor(self):
        """
        Tests DELETE request to '/api/vendors/{vendor_id}'
        """
        vendor_id = Vendor.objects.first().vendor_code
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.delete(reverse('vendor_data', args=[vendor_id]))
        #check response status
        self.assertEqual(response.status_code, 204)
        #check if vendor still exists in test database
        self.assertFalse(Vendor.objects.filter(vendor_code=vendor_id).exists())


class PurchaseOrderAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token = Token.objects.create(user=self.user)
        #Create a vendor object with id 'TEST001'
        Vendor.objects.create(
            name='Test Vendor 1',
            contact_details='Contact details 1',
            address='Address 1',
            vendor_code='TEST001',
            on_time_delivery_rate=0.95,
            quality_rating_avg=4.5,
            average_response_time=2.5,
            fulfillment_rate=0.98
        )
        #Create purchase order object with foreign key referencing 'TEST001'
        PurchaseOrder.objects.create(
            po_number='PO001',
            vendor=Vendor.objects.get(pk='TEST001'),
            order_date=datetime.now(),
            delivery_date=datetime.now(),
            items={
                'dummy item':'desc'
            },
            quantity=1,
            status='pending',
            quality_rating=2.3,
            issue_date=datetime.now()
        )
    
    def test_get_po_list(self):
        """
        Tests GET request to '/api/purchase_orders'
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.get(reverse('purchase_orders'))
        #check response status
        self.assertEqual(response.status_code, 200)
        #check number of purchase orders returned
        self.assertEqual(len(response.json()),1)

    def test_create_purchase_order(self):
        """
        Tests POST request to '/api/purchase_orders'
        """
        data = {
            'po_number': 'PO123',
            'vendor': 'TEST001',  
            'order_date': '2024-05-06',
            'delivery_date': '2024-05-10',
            'items': {'item':'desc'},
            'quantity': 10,
            'status': 'pending',
            'quality_rating': 4.5,
            'issue_date': '2024-05-06T12:00:00Z',
        }
        data = json.dumps(data)
        url = reverse('purchase_orders')  
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.post(url, data, content_type='application/json')
        # print(f'\nstatus received: {response.status_code}\n')
        # print(response.json())
        #check response status
        self.assertEqual(response.status_code, 201)
        #check if new purchase order is present in test dtatabase
        self.assertTrue(PurchaseOrder.objects.filter(po_number='PO123').exists())
    
    def test_retrieve_po(self):
        """
        Tests GET request to '/api/purchase_orders/{po_id}'
        """
        po_id = PurchaseOrder.objects.first().po_number
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.get(reverse('purchase_order_data', args=[po_id]))
        #check response status
        self.assertEqual(response.status_code, 200)
        #check if retrieved purchase order matches required id
        self.assertEqual(response.json()['po_number'], po_id)
        #check if all attributes of purchase order model are returned
        self.assertEqual(len(response.json()),10)

    def test_update_po(self):
        """
        Tests PUT request to '/api/purchase_orders/{po_id}'
        """
        po_id = PurchaseOrder.objects.first().po_number
        data = {'status': 'completed'}
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.put(reverse('purchase_order_data', args=[po_id]), data=json.dumps(data), content_type='application/json')
        #check status code
        self.assertEqual(response.status_code, 200)
        #check modified field
        self.assertEqual(PurchaseOrder.objects.get(pk=po_id).status, 'completed')
        #check if other attributes are same
        self.assertEqual(PurchaseOrder.objects.get(pk=po_id).quantity, 1)
        #check if historical record is created
        self.assertEqual(len(HistoricalPerformance.objects.all()), 1)
    
    def test_acknowledge_po(self):
        """
        Tests GET request to '/api/purchase_orders/{po_id}/acknowledge'
        """
        po_id = PurchaseOrder.objects.first().po_number
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.get(reverse('acknowledge_purchase_order', args=[po_id]))
        #check response status
        self.assertEqual(response.status_code, 200)
        #check that acknowledgement date is no longer null
        self.assertNotEqual(PurchaseOrder.objects.get(pk=po_id), None)
        #check if historical record is created
        self.assertEqual(len(HistoricalPerformance.objects.all()),1)
        #check if vendor of historical performance object matches po vendor
        vendor = PurchaseOrder.objects.first().vendor
        self.assertEqual(HistoricalPerformance.objects.first().vendor, vendor)
    
    def test_delete_po(self):
        """
        Tests DELETE request to '/api/purchase_orders/{po_id}'
        """
        po_id = PurchaseOrder.objects.first().po_number
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.delete(reverse('purchase_order_data', args=[po_id]))
        #check response status        
        self.assertEqual(response.status_code, 204)
        #check if purchase order no longer exists in test database
        self.assertFalse(PurchaseOrder.objects.filter(pk=po_id).exists())
        #check if historical record has been created
        self.assertEqual(len(HistoricalPerformance.objects.all()),1)


    
        