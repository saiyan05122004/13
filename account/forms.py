from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Profile


class UserRegistrationForm(forms.Form):
	username = forms.CharField(label='Имя пользователя',widget=forms.TextInput(attrs={'class':'form-control'}))
	email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control'}))
	password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class':'form-control'}))
	password2 = forms.CharField(label='Потверждение пароля', widget=forms.PasswordInput(attrs={'class':'form-control'}))

	def clean_email(self):
		email = self.cleaned_data['email']
		user = User.objects.filter(email=email).exists()
		if user:
			raise ValidationError('этот адрес электронной почты уже существует')
		return email

	def clean(self):
		cd = super().clean()
		p1 = cd.get('password1')
		p2 = cd.get('password2')

		if p1 and p2 and p1 != p2:
			raise ValidationError('пароли должны совпадать')


class UserLoginForm(forms.Form):
	username = forms.CharField(label='Имя пользователя',widget=forms.TextInput(attrs={'class':'form-control'}))
	password = forms.CharField(label='Пароль',widget=forms.PasswordInput(attrs={'class':'form-control'}))


class EditUserForm(forms.ModelForm):
	email = forms.EmailField()

	class Meta:
		model = Profile
		fields = ('age', 'bio')

from django import forms
from .models import Message

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'conent': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Введите сообщение...'}),
        }

