def timezone(request):
    time_zone = 'UTC'
    if request.user.is_authenticated:
        time_zone = request.user.profile.time_zone

    return {
        "TIME_ZONE": time_zone
    }
