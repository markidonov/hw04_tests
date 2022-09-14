from django.forms import ModelForm
from django.forms import forms
from .models import Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group']
        labels = {'text': 'Текст поста', 'group': 'Группа'}
        help_texts = {'text': 'Обязательно заполните это поле',
                      'group': 'Группа, к которой будет отнесён пост'}

    def clean_text(self):
        data = self.cleaned_data['text']
        if data == '':
            raise forms.ValidationError('заполните поле текст!')
        if len(data) <= 10:
            raise forms.ValidationError('объем поста слишком мал')
        return data
