from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone

from .models import ShopSettings
from .forms import ShopSettingsForm


@login_required
@user_passes_test(lambda u: u.is_admin_role or u.is_superuser)
def edit_settings(request):
    settings_obj = ShopSettings.get_solo()
    if request.method == "POST":
        form = ShopSettingsForm(request.POST, request.FILES, instance=settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Shop settings updated.")
            return redirect("shopsettings:edit")
    else:
        form = ShopSettingsForm(instance=settings_obj)
    return render(request, "shopsettings/settings_form.html", {"form": form, "settings_obj": settings_obj})


@login_required
@user_passes_test(lambda u: u.is_admin_role or u.is_superuser)
def backup(request):
    """Simple JSON dump backup of the whole database via Django's dumpdata."""
    import io
    from django.core.management import call_command

    buf = io.StringIO()
    call_command("dumpdata", stdout=buf, indent=2,
                 exclude=["contenttypes", "auth.permission", "sessions.session", "admin.logentry"])
    content = buf.getvalue()

    settings_obj = ShopSettings.get_solo()
    settings_obj.last_backup_at = timezone.now()
    settings_obj.save(update_fields=["last_backup_at"])

    response = HttpResponse(content, content_type="application/json")
    response["Content-Disposition"] = f'attachment; filename="srikrishna_backup_{timezone.now():%Y%m%d_%H%M}.json"'
    return response
