from django.contrib import admin
from .models import Post



@admin.register(Post) # У этого декоратора тот же функционал, что и у: admin.site.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'author', 'publish', 'status']

    # Блок отвечающий за создание фильтров для сортировка постов по статусу, дате создания, дате публикации и автору
    list_filter = ['status', 'created', 'publish', 'author']

    # Окошко для поиска
    search_fields = ['title', 'body']

    # Заполнение поля slug в соответствующем формате по содержанию поля title при добавлении поста
    prepopulated_fields = {'slug':('title', )}

    raw_id_fields = ['author']

    # Навигация по датам
    date_hierarchy = 'publish'

    # Посты упорядочены по столбцам "статус" и "дата публикации"
    ordering = ['status', 'publish']


