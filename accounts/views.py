from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import RegisterForm, URLForm, PaymentForm, BalanceForm
from django.contrib.auth import authenticate, logout
from .models import URL, Membership
from django.utils import timezone  
from datetime import timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

@csrf_exempt
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Registration successful. You can now log in.'})
        else:
            errors = dict(form.errors.items())
            return JsonResponse({'success': False, 'errors': errors})
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

@api_view(['POST'])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def custom_logout(request):
    logout(request)
    return JsonResponse({'success': True, 'message': 'Logout successful', 'redirect_url': '/'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def save_url(request):
    if request.method == 'POST':
        form = URLForm(request.POST)
        if form.is_valid():
            user_membership = Membership.objects.get_or_create(user=request.user)[0]
            max_urls_allowed = 0  
            if user_membership.level == 'basic':
                max_urls_allowed = 3
            elif user_membership.level == 'premium':
                max_urls_allowed = 6
            
            current_urls_count = URL.objects.filter(user=request.user).count()

            if current_urls_count < max_urls_allowed:
                url_instance = form.save(commit=False)
                url_instance.user = request.user
                url_instance.save()
                return JsonResponse({'success': True, 'message': 'URL saved successfully'})
            else:
                return JsonResponse({'success': False, 'message': f'You have reached the maximum limit of {max_urls_allowed} URLs allowed for your membership level.'})
        else:
            errors = dict(form.errors.items())
            return JsonResponse({'success': False, 'errors': errors})
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def url_list(request):
    urls = URL.objects.filter(user=request.user)
    url_list = [{'id': url.id, 'url': url.url, 'created_at': url.created_at} for url in urls]
    return JsonResponse({'success': True, 'urls': url_list})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def payment(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            user_membership = Membership.objects.get_or_create(user=request.user)[0]
            user_membership.level = 'premium'
            user_membership.expiration_date = timezone.now() + timedelta(days=30)
            user_membership.save()
            return JsonResponse({'success': True, 'message': 'Payment successful'})
        else:
            errors = dict(form.errors.items())
            return JsonResponse({'success': False, 'errors': errors})
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    membership = Membership.objects.get_or_create(user=request.user)[0]
    profile_data = {
        'username': request.user.username,
        'email': request.user.email,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'membership_level': membership.level,
        'expiration_date': membership.expiration_date,
        'balance': request.user.balance,
    }
    return JsonResponse({'success': True, 'profile': profile_data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def load_balance(request):
    if request.method == 'POST':
        form = BalanceForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            request.user.balance += amount
            request.user.save()
            return JsonResponse({'success': True, 'message': 'Bakiye yüklendi'})
        else:
            errors = dict(form.errors.items())
            return JsonResponse({'success': False, 'errors': errors})
    else:
        return JsonResponse({'error': 'Geçersiz istek methodu.'}, status=405)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def purchase_membership(request, membership_type):
    membership_prices = {
        'basic': 60,
        'premium': 100,
        'vip': 500,
    }
    
    user_membership, created = Membership.objects.get_or_create(
        user=request.user,
        defaults={'level': 'basic', 'expiration_date': timezone.now() + timedelta(days=365)}    
    )
    current_level = user_membership.level

    if membership_type not in membership_prices:
        return JsonResponse({'success': False, 'message': 'Invalid membership type'})

    current_price = membership_prices[current_level]
    new_price = membership_prices[membership_type]
    price_difference = new_price - current_price

    if request.user.balance >= price_difference:
        request.user.balance -= price_difference
        user_membership.level = membership_type
        user_membership.expiration_date = timezone.now() + timedelta(days=30)
        user_membership.save()
        request.user.save()
        return JsonResponse({'success': True, 'message': 'Membership upgraded', 'new_balance': request.user.balance})
    return JsonResponse({'success': False, 'message': 'Insufficient balance', 'required_balance': price_difference, 'current_balance': request.user.balance})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def delete_url(request, url_id):
    try:
        url_instance = URL.objects.get(id=url_id, user=request.user)
    except URL.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'URL not found'}, status=404)
    
    url_instance.delete()
    return JsonResponse({'success': True, 'message': 'URL deleted successfully'})

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def delete_url(request, url_id):
    try:
        url_instance = URL.objects.get(id=url_id, user=request.user)
    except URL.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'URL not found'}, status=404)
    
    url_instance.delete()
    return JsonResponse({'success': True, 'message': 'URL deleted successfully'})
