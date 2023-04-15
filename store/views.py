from django.shortcuts import render
from django.http import JsonResponse
import json
import datetime

from .models import *
from .utils import cookieCart, cartData, guestOrder


def store(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'store/store.html', context)

def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)
#-----------------------------------------------------------------------------
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
@csrf_exempt
def searchOrdered(request):
    items = []
    cartItems = None
    context = None
    order = None
    total = 0
    try:
        data = json.loads(request.body)
        orderid = data['form']['order']
        order_item = OrderItem.objects.get(id = orderid)
        items = order_item.order.orderitem_set.all()
        order = Order.objects.get(id=orderid)
        # perform search logic
        for item in items:
            produce = item.product
            quantity = item.quantity
            get_total = item.get_total
            print ("produce: ", produce, quantity, get_total)
        #
    except Exception as ex:
        print ("error: ", ex)
    #context = {'items': items,'order': order}
    items = [ {'product': { 'name': 'Product 1', 'price': 10.0, 'imageURL': 'https://example.com/image.jpg' }, 'quantity': 2},
                {'product': { 'name': 'Product 2', 'price': 20.0, 'imageURL': 'https://example.com/image.jpg' }, 'quantity': 1} ]
    total = sum([item['product']['price'] * item['quantity'] for item in items])
    context = {'items': items, 'cart_items': len(items), 'cart_total': total}
    #print ("context: ", context)
    return render(request, 'store/ordered.html', context)
#-------------------------------------------------------------------------------
def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)

def updateItem(request):
    data = json.loads(request.body)
    print ("data: ", data)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('Product:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )

    return JsonResponse('Payment submitted..', safe=False)