from .models import Cart

class CartMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            request.user.cart, created = Cart.objects.get_or_create(user=request.user)
        response = self.get_response(request)
        return response
