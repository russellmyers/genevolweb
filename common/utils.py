from django.conf import settings

def google_analytics_id(request):
    try:
        analytics_id = settings.GOOGLE_ANALYTICS_MEASUREMENT_ID
    except:
        analytics_id = None

    return {'google_analytics_id': analytics_id}