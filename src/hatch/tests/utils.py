from ..models import AppConfig

def create_app_config():
    AppConfig.objects.all().delete()
    AppConfig.objects.create(
        title='',
        subtitle='',
        description='',
        twitter_handle='',
        share_title='',
        url='',
        vision='vision',
        vision_plural='visions',
        visionaries_label='',
        ally='ally',
        ally_plural='allies',
        allies_label='',
        city='',
    )
