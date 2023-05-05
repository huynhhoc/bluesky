from django.test import TestCase
from django.contrib.auth.models import User
from .models import Customer, Product, Order, OrderItem
from .utils import cookieCart, cartData, guestOrder

class TestCart(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass'
        )
        self.customer = Customer.objects.create(
            user=self.user,
            name='Test User',
            email='testuser@example.com'
        )
        self.product = Product.objects.create(
            name='Test Product',
            price=10.0,
            digital=False
        )
        self.order = Order.objects.create(
            customer=self.customer,
            complete=False
        )
        self.order_item = OrderItem.objects.create(
            product=self.product,
            order=self.order,
            quantity=2
        )

def test_cookieCart(self):
    # Test with an empty cart
    request = self.client.get('/')
    cart_data = cookieCart(request)
    self.assertEqual(cart_data['cartItems'], 0)
    self.assertEqual(cart_data['order']['get_cart_items'], 0)
    self.assertEqual(cart_data['order']['get_cart_total'], 0)

    # Test with a non-empty cart
    cookies = {'cart': '{"' + str(self.product.id) + '": {"quantity": 2}}'}
    request = self.client.get('/', cookies=cookies)
    cart_data = cookieCart(request)
    self.assertEqual(cart_data['cartItems'], 2)
    self.assertEqual(cart_data['order']['get_cart_items'], 2)
    self.assertEqual(cart_data['order']['get_cart_total'], 20.0)

def test_guestOrder(self):
    data = {
        'form': {
            'name': 'Guest User',
            'email': 'guest@example.com'
        }
    }
    customer, order = guestOrder(self.client.get('/'), data)
    self.assertEqual(customer.name, 'Guest User')
    self.assertEqual(customer.email, 'guest@example.com')
    self.assertFalse(order.complete)
    self.assertEqual(order.orderitem_set.count(), 1)
    order_item = order.orderitem_set.first()
    self.assertEqual(order_item.product, self.product)
    self.assertEqual(order_item.quantity, 2)

def test_cartData_guest_user(self):
    request = self.client.get('/')
    cookies = self.client.cookies
    cookies['cart'] = '{"1": {"quantity": 2}}'
    request.COOKIES = cookies
    cart_data = cartData(request)
    self.assertEqual(cart_data['cartItems'], 2)
    self.assertEqual(cart_data['order']['get_cart_items'], 2)
    self.assertEqual(cart_data['order']['get_cart_total'], 20.0)
    self.assertEqual(cart_data['items'].count(), 1)

def test_cartData_authenticated_user(self):
    self.client.login(username='testuser', password='testpass')
    request = self.client.get('/')
    cart_data = cartData(request)
    self.assertEqual(cart_data['cartItems'], 2)
    self.assertEqual(cart_data['order']['get_cart_items'], 2)
    self.assertEqual(cart_data['order']['get_cart_total'], 20.0)
    self.assertEqual(cart_data['items'].count(), 1)