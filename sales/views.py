from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Cart, CartItem, Order
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .forms import ProductForm
from django.http import JsonResponse

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
@csrf_exempt
def checkout(request):
    cart = Cart.objects.get(user=request.user)
    items = cart.items.all()
    total_price = sum(item.get_total_price() for item in items)
    
    if request.method == 'POST':
        address = request.POST.get('address')
        city = request.POST.get('city')
        postal_code = request.POST.get('postal_code')
        country = request.POST.get('country')
        
        # Stripe ödeme işlemi
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(total_price * 100),  # Stripe ödemeleri kuruş cinsindendir
                currency='usd',
                payment_method_types=['card']
            )
            order = Order.objects.create(
                user=request.user,
                cart=cart,
                total_amount=total_price,
                address=address,
                city=city,
                postal_code=postal_code,
                country=country,
                stripe_payment_id=intent.id
            )
            return render(request, 'sales/checkout.html', {
                'client_secret': intent.client_secret,
                'total_price': total_price
            })
        except stripe.error.StripeError as e:
            return render(request, 'sales/checkout.html', {'error': str(e)})
    
    return render(request, 'sales/checkout.html', {'total_price': total_price})


@login_required
def product_list(request):
    products = Product.objects.all()
    return render(request, 'sales/product_list.html', {'products': products})

@login_required
def add_product(request):
    # Sadece manager kullanıcılar bu görünümü kullanabilir
    if not request.user.is_manager():
        messages.error(request, "You are not authorized to add products.")
        return redirect('product_list')  # Yetkisi olmayanları ürün listesine yönlendir

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Product added successfully.")
            return redirect('product_list')
    else:
        form = ProductForm()

    return render(request, 'sales/add_product.html', {'form': form})

@login_required
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'sales/product_detail.html', {'product': product})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not item_created:
        cart_item.quantity += 1
    cart_item.save()

    # Sepet toplam öğe sayısını JSON yanıt olarak döndür
    cart_items_count = cart.get_total_items()
    return JsonResponse({'message': f"{product.name} added to cart.", 'cart_items_count': cart_items_count})

@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()
    total_price = sum(item.get_total_price() for item in items)
    return render(request, 'sales/cart_detail.html', {'cart': cart, 'items': items, 'total_price': total_price})

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect('cart_detail')