from django.urls import path
from . import views
from .feeds import LatestPostsFeed

# Определяем именное пространство приложения
# Это позволяет упорядочивать URL-адреса по приложениям и при обращении к ним использовать имя
app_name = 'blog'

# с помощью path() определяются два разных шаблона
# Первый шаблон URL-адреса не принимает никаких аргументов и соотносится с представлением post-list
# Второй шаблон соотносится с представлением post_detail и принимает только один аргумент id, совпадающий с целым числом, заданным целым числом конвертора путей int
urlpatterns = [
    # Представления поста при помощи функций: 
    path('', views.post_list, name='post_list'),
    # Использование класса для отображения url
    # path('', views.PostListView.as_view(), name='post_list'),
    path('tag/<slug:tag_slug>/', views.post_list, name='post_list_by_tag'),
    # Для захвата значений из URL-адреса используются угловые скобки. Любое значение, указанное в шаблоне URL-адреса как <parameter>, записывается в качестве строкового литерала
    # Для конкретного сопоставления и возврата целого числа используются конверторы путей, например, <int:year>, <slug:post> и тд
    # url в строке теперь выглядит как год поста/месяц поста/день поста/слаг к посту
    path('<int:year>/<int:month>/<int:day>/<slug:post>', views.post_detail, name='post_detail'),
    path('<int:post_id>/share/', views.post_share, name='post_share'),
    # Представление для комментария к посту
    path('<int:post_id>/comment/', views.post_comment, name='post_comment'),
    path('feed/', LatestPostsFeed(), name='post_feed'),
    path('search/', views.post_search, name='post_search'),

]

# Создание файла urls.py для каждого приложения - лучший способ сделать приложения пригодными для реиспользования в других проектах