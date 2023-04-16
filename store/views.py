from django.shortcuts import render
from django.http import JsonResponse
import json
import datetime
from django.db.models.signals import pre_save
from .models import *
from .utils import cookieCart, cartData, guestOrder
#create a function that will update the quantity of the product when an order item is created
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
        context = {'items': {}, 'cart_items': 0, 'cart_total': 0}
        total = 0
        try:
            data = json.loads(request.body)
            orderid = data['form']['order']
            shippingAddress = ShippingAddress.objects.get(order=orderid)
            client = Client.objects.get(order =orderid)

            orderid = Order.objects.get(id =orderid)
            
            print("orderid: ",client.name, client.email, shippingAddress)
            shipping = {'customer': {'name': client.name, 'email': client.email}, 
                        'shippingAddress': {'adress': shippingAddress.address, 'city': shippingAddress.city, 'state': shippingAddress.state,
                                            'zipcode': shippingAddress.zipcode, 'date_added': shippingAddress.date_added.strftime('%F')}}
            items = OrderItem.objects.filter(order=orderid)
            # perform search logic
            for item in items:
                produce = item.product.name
                quantity = item.quantity
                price = item.get_total
                imageURL = item.product.imageURL
                j_item = {'product': {'name': produce, 'price': price, 'imageURL': imageURL}, 'quantity': quantity}
                jitems.append(j_item)
            total = sum([item['product']['price'] * item['quantity'] for item in jitems])
            nItems = len(jitems)
            context = {'items': jitems, 'cart_items': nItems, 'cart_total': total, 'shipping': shipping}
            #print("context: ", context)
            return JsonResponse(context) # send JSON response
        except json.decoder.JSONDecodeError:
            render(request, 'store/ordered.html')
        except Order.DoesNotExist:
            print("context is empty")
            return render(request, 'store/ordered.html',context)
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

        Client.objects.create(
            customer=customer,
            order=order,
            name=data['client']['name'],
            email=data['client']['email'],
        )
    
    return JsonResponse('Payment submitted..', safe=False)