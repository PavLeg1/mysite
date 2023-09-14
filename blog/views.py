from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST


def post_list(request):
    post_list = Post.published.all()
    # Постраничная разбивка с 3 постами на страницу
    # Создаем экземпляр класса Paginator с числом объектов на странице (у нас это по три поста на странице)
    paginator = Paginator(post_list, 3)
    # Извлекаем HTTP GET-параметр page и сохраняем его в page_number
    page_number = request.GET.get('page', 1)
    
    try:
        # Возвращаем объект Page хранящийся в переменной posts
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # Если page не число - выдаем первую страницу
        posts = paginator.page(1) 
    except EmptyPage:
        # Если page_number вне диапазона - выдаем последнюю страницу
        posts = paginator.page(paginator.num_pages)

    # Передаем номер страницы и объект posts в шаблон
    return render(request,
                  'blog/post/list.html',
                  {'posts': posts})


def post_detail(request, year, month, day, post):
    # try:
    #     post = Post.published.get(id=id)
    # except Post.DoesNotExist:
    #     raise Http404("No post found.")
    # URL состоит из даты и слага
    post = get_object_or_404(Post,
                             status=Post.Status.PUBLISHED,
                             slug=post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    # Список активных комментариев к посту:
    # Добавлен набор запросов QuerySet чтобы извлекать все активные комментарии к посту
    comments = post.comments.filter(active=True)
    # Форма для комментирования пользователями
    form = CommentForm()

    return render(request,
                  'blog/post/detail.html',
                  {'post': post,
                   'comments': comments,
                   'form': form})

# Представление для отправки поста получая доступ к посту через его id используя функцию get_object_or_404()
def post_share(request, post_id):
    # Извлечь пост по id
    post = get_object_or_404(Post,
                             id=post_id,
                             status=Post.Status.PUBLISHED)
    
    # Еще не было отправлено
    sent = False
    
    
    if request.method == 'POST':
        # Форма была передана на обработку с данными из request.POST
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Поля формы успешно прошли валидацию
            cd = form.cleaned_data

            # Получаем путь до поста чтобы его отправить
            post_url = request.build_absolute_uri(post.get_absolute_url())
            
            # Тема письма
            subject = f"{cd['name']} recommends you to read {post.title}"
            
            # Текст письма с комментом (если есть) 
            message = f"Read {post.title} at {post_url}\n\n\
                {cd['name']} comments: {cd['comments']}"
            send_mail(subject, message, 'zxc@gmail.com', [cd['to']])

            # Письмо отправлено
            sent = True 
    else:
        # Отображение пустой формы если метод "GET"
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post,
                                                    'form': form,
                                                    'sent': sent})


class PostListView(ListView):
    queryset = Post.published.all() # Используется для того, чтобы иметь конкретно-прикладной набор запросов QuerySet, не извлекая все объекты
    context_object_name = 'posts'   # 'posts' используется для результатов запроса. Если в context_object_name ничего не указано, по умолчанию object_list 
    paginate_by = 3                 # В данном атрибуте задается постраничная разбивка результатов с возвратом трех объектов на страницу    
    template_name = 'blog/post/list.html' # Конкретно-прикладной шаблон используется для прорисовки страницы шаблоном template_name     


# Представление управляющее передачей поста на обработку через POST
# Декоратор @require_POST разрешает запросы через POST только для этого представления
# При запросах через другие методы --> ошибка 405
@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post,
                             id=post_id,
                             status=Post.Status.PUBLISHED)
    # Переменная для хранения комментария при его создании
    comment = None
    # Комментарий был отправлен
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # Создать объект класса Comment, не сохраняя его в базу данных (метод save())
        # save() недоступен для экземпляров Form, так как они не привязаны к конкретной модели 
        comment = form.save(commit=False)
        # Назначить пост комментария
        comment.post = post
        # Сохранить комментарий в БД
        comment.save()
    return render(request, 'blog/post/comment.html',
                  {'post': post,
                   'form': form,
                   'comment': comment})