from django import forms
from .models import Post, Comment
from django.utils.text import slugify
from unidecode import unidecode

class PostCreateUpdateForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('body',)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.slug:
            base_slug = slugify(unidecode(instance.body[:30])) or 'default-slug'
            slug = base_slug
            num = 1
            while Post.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            instance.slug = slug
        if commit:
            instance.save()
        return instance

class CommentCreateForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)
        widgets = {
            'body': forms.Textarea(attrs={'class':'form-control'})
        }

class CommentReplyForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)

class PostSearchForm(forms.Form):
    search = forms.CharField(label='Найти пост', widget=forms.TextInput(attrs={'placeholder': 'Поиск'}))