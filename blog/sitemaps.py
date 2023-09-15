from django.contrib.sitemaps import Sitemap
from .models import Post

class PostSiteMap(Sitemap):
    changefreq = 'weekly' # Частота изменения страниц постов
    priority = 0.9        # Релевантность страниц постов на сайте (макс. значение = 1)

    # Вовзращает набор QuerySet, подлежащих включению в эту карту сайта
    def items(self):
        return Post.published.all()
    
    # Получает каждый возвращаемый items() объект и возвращает время последнего изменения объекта
    def lastmod(self, obj):
        return obj.updated