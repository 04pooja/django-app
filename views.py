from django.shortcuts import render, HttpResponse, redirect, \
    get_object_or_404, reverse
from django.http import HttpResponse
from .models import Product,Contact,Orders,OrderUpdate
from math import ceil
import logging
from decimal import Decimal
import json
from paypal.standard.forms import PayPalPaymentsForm
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse


from django.views.decorators.csrf import csrf_exempt


logger=logging.getLogger(__name__)


def index(request):
    #products=Product.objects.all()
    #print(products)
    #n=len(products)
    #nslides=n//4+ceil((n/4)-(n/4))
    allprods=[]
    catprods=Product.objects.values('category','id')
    cats={item['category'] for item in catprods}
    for cat in cats:
        prod=Product.objects.filter(category=cat)
        n=len(prod)
        nslides=n//4+ceil((n/4)-(n/4))
        allprods.append([prod,range(1,nslides),nslides])

   
    params={'allprods':allprods}
    return render(request,'blog/index.html',params)

def about(request):
    return render(request, 'blog/about.html')

def contact(request):
    if request.method=="POST":
        name=request.POST.get('name','')
        phone=request.POST.get('phone','')
        email=request.POST.get('email','')
        desc=request.POST.get('desc','')
        print(name,phone,email,desc)
        contact=Contact(name=name,phone=phone,email=email,desc=desc)
        contact.save()
        thank = True;
    return render(request,'blog/contact.html')

def tracker(request):
    if request.method == "POST":
        orderId = request.POST.get('orderId','')
        email = request.POST.get('email','')
        
        try:
            order = Orders.objects.filter(order_id=orderId,email=email)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text':item.update_desc,'time':item.timestamp})
                    response = json.dumps({"status":"success","updates":updates,"itemsJson":order[0].items_json},default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{"status":"noitem"}')
            
        except Exception as e:
            return HttpResponse('{"status":"erorr"}')         
    return render(request,'blog/tracker.html')

def productview(request,myid):
    product=Product.objects.filter(id=myid)
    return render(request,'blog/prodview.html',{'product':product[0]})

def searchmatch(query,item):
    ''' return true only if query matches the item'''
    if query in item.desc or query in item.product_name or query in item.category:
        return True
    else:
        return False


def search(request):
    query = request.GET.get('search')
    allprods=[]
    catprods=Product.objects.values('category','id')
    cats={item['category'] for item in catprods}
    for cat in cats:
        prodtemp=Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchmatch(query,item)]
        n=len(prod)
        nslides=n//4+ceil((n/4)-(n/4))
        if len(prod)!=0:
            allprods.append([prod,range(1,nslides),nslides])
        
    params={'allprods':allprods,"msg":""} 
    if len(allprods)==0 or len(query)<3:
        params={'msg':"please make sure entire query should be relevant"}

    return render(request,'blog/search.html',params)


def checkout(request):
    if request.method=="POST":
        items_json=request.POST.get('itemsjson','')
        name=request.POST.get('name','')
        email=request.POST.get('email','')
        amount=request.POST.get('amount','')
        phone=request.POST.get('phone','')
        address=request.POST.get('address1','') + " " + request.POST.get('address2','')
        state=request.POST.get('state','')
        city=request.POST.get('city','')
        zip_code=request.POST.get('zip','')
        order = Orders(items_json=items_json,name=name,email=email,amount=amount,phone=phone,address=address,
            state=state,city=city,zip_code=zip_code)
                       
        order.save()
        update = OrderUpdate(order_id=order.order_id, update_desc="order has been placed ")
        update.save()
        thank = True;
        id=order.order_id
        request.session['id'] = order.order_id
        return redirect('process_payment')

    return render(request,'blog/checkout.html')


def process_payment(request):
    id = request.session.get('id')
    order = get_object_or_404(Orders, order_id=id)
    host = request.get_host()
 
    paypal_dict = {
        'business': 'poojamaurya0401@gmail.com',
        'amount': '%.2f' % Decimal(order.total_cost()).quantize(
            Decimal('.01')),
        'item_name': 'Order {}'.format(order.order_id),
        'invoice': str(order.order_id),
        'currency_code': 'USD',
        'notify_url': 'http://{}{}'.format(host,
                                           reverse('paypal-ipn')),
        'return_url': 'http://{}{}'.format(host,
                                           reverse('payment_done')),
        'cancel_return': 'http://{}{}'.format(host,
                                              reverse('payment_cancelled')),
    }
 
    form = PayPalPaymentsForm(initial=paypal_dict)
    return render(request, 'blog/process_payment.html', {'order': order, 'form': form})   

@csrf_exempt
def payment_done(request):
    return render(request, 'blog/payment_done.html')
 
 
@csrf_exempt
def payment_cancelled(request):
    return render(request, 'blog/payment_cancelled.html')