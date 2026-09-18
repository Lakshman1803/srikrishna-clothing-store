from .models import ShopSettings


def shop_settings(request):
    return {"shop_settings": ShopSettings.get_solo()}
