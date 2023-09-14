from django import forms 
from .models import Comment


class EmailPostForm(forms.Form):
    # name - экземпляр класса CharField с макс. длинной=25 для имени отправителя поста    
    name = forms.CharField(max_length=25)

    # email - экземпляр класса EmailField (адрес почты отправителя)
    email = forms.EmailField()

    # to - экземпляр класса EmailField (адрес почты получателя)
    to = forms.EmailField()

    # comments - экземпляр класса CharField для комментариев к письму
    #required = False: поле можно оставить пустым (необязательное)
    # widget=forms.Textarea: отображается в типе "Многострочное текстовое поле"
    comments = forms.CharField(required=False,
                               widget=forms.Textarea)
    

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'email', 'body']