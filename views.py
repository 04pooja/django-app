from django.shortcuts import render
from django.http import HttpResponse
from .models import Product,Contact,Orders,OrderUpdate
from math import ceil
import logging
import json
from PayTm import Checksum




from django.views.decorators.csrf import csrf_exempt
MERCHANT_KEY='kbzk1DSbJiV_O3p5';

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
    return render(request,'blog/contact.html',)

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
                    response = json.dumps([updates,order[0].items_json],default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{}')
            
        except Exception as e:
            return HttpResponse('{}')         
    return render(request,'blog/tracker.html')

def productview(request,myid):
    product=Product.objects.filter(id=myid)
    return render(request,'blog/prodview.html',{'product':product[0]})

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
        #return render(request,'blog/checkout.html',{'id':id})
        param_dict={ 
        'MID':'WorldP64425807474247',
        'ORDER_ID':order.order_id,
        'TXN_AMOUNT':'1',
        'CUST_ID':email,
        'INDUSTRY_TYPE_ID':'Retail',
        'WEBSITE':'WEBSTAGING',
        'CHANNEL_ID':'WEB',
        'CALLBACK_URL':'http://127.0.0.1:8000/blog/handlerequest/',
        }
        param_dict['CHECKSUMHASH']=checksum.generate_checksum(param_dict,MERCHANT_KEY)
        return render(request,'blog/paytm.html',{'param_dict': param_dict})
    return render(request, 'blog/checkout.html')


@csrf_exempt
def handlerequest(request):
    return HttpResponse('done')
    pass

    #paytm will send you post request here



# Create your views here.
