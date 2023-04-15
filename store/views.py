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
def search_ordered(request):
    if request.method == 'POST':
        jitems = []
        nItems = 0 
        context = {'items': None, 'cart_items': 0, 'cart_total': 0}
        total = 0
        try:
            data = json.loads(request.body)
            orderid = data['form']['order']
            orderid = Order.objects.get(id =orderid)
            #order_item = OrderItem.objects.get(order=orderid)
            items = OrderItem.objects.filter(order=orderid)
            #items = order_item.order.orderitem_set.all()
            # perform search logic
            for item in items:
                produce = item.product.name
                quantity = item.quantity
                price = item.get_total
                j_item = {'product': {'name': produce, 'price': price}, 'quantity': quantity}
                jitems.append(j_item)
            total = sum([item['product']['price'] * item['quantity'] for item in jitems])
            nItems = len(jitems)
            context = {'items': jitems, 'cart_items': nItems, 'cart_total': total}
            print("context: ", context)
            return JsonResponse(context) # send JSON response
        except:
            render(request, 'store/ordered.html', context)
    return render(request, 'store/ordered.html')
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