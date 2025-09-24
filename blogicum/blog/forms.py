from django import forms
from django.contrib.auth.models import User

from .models import Post, Comments


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class CreatePost(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'text', 'pub_date', 'image', 'location', 'category')
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'})
        }


class CreateComments(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ('text',)
