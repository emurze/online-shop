from django.conf import settings
from django.core.cache import cache
from django.core.handlers.wsgi import WSGIRequest
from django.db import ProgrammingError
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.coupons.forms import CouponForm
from apps.coupons.models import Coupon


@require_POST
def coupon_apply_view(request: WSGIRequest) -> HttpResponse:
    form = CouponForm(data=request.POST)

    if form.is_valid():
        cd = form.cleaned_data
        now = timezone.now()
        session_key = request.session.session_key

        try:
            coupon = Coupon.objects.get(
                code__iexact=cd['code'],
                valid_from__lte=now,
                valid_to__gte=now,
                active=True,
            )
            cache.set(
                f'{settings.SESSION_COUPON_ID}_{session_key}', coupon.id,
                settings.COUPON_ID_CACHE_EXPIRATION,
            )
        except Coupon.DoesNotExist:
            cache.set(
                f'{settings.SESSION_COUPON_ID}_{session_key}', None,
                settings.COUPON_ID_CACHE_EXPIRATION,
            )

    return redirect('cart:detail')

