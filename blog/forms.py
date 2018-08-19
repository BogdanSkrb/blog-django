from django import forms

from django.forms import (
    ModelForm, Textarea, TextInput, EmailField,
    EmailInput, SelectMultiple, CharField,
    PasswordInput, ClearableFileInput,
    )

from django.utils.text import slugify

# sending mail
from django.core.mail import send_mail, BadHeaderError
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import Category, Post, Profile

from django.core.exceptions import ValidationError

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', )


class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ('avatar', 'bio', )


class SignUpForm(UserCreationForm):
    email = EmailField(label='Email',widget=EmailInput)
    password1 = CharField(label='Password', widget=PasswordInput)
    password2 = CharField(label='Confirm password', widget=PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        qs = User.objects.filter(username=username)
        if qs.exists():
            raise ValidationError("Username already in use!")
        return username

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.first_name = self.cleaned_data.get('username', '').capitalize()
        instance.email = self.cleaned_data.get('email', '')
        if commit:
            instance.save()
        return instance


class AddPostForm(ModelForm):
    class Meta:
        model = Post
        exclude = ('slug', 'author', )
        widgets = {
            'title': TextInput(
                attrs={
                    'class': 'form-control',
                    'required': True,
                    'placeholder': 'Type your title here..', }, ),
            'content': Textarea(
                attrs={
                    'class': 'form-control',
                    'required': True,
                    'placeholder': 'Type your post here..', }, ),
            'category': SelectMultiple(
                attrs={
                    'class': 'form-control',
                    'required': True, }, ),
        }

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        slug = cleaned_data.get('slug')

        if not slug and title:
            cleaned_data['slug'] = slugify(title)

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.slug = slugify(self.cleaned_data.get('title', ''))

        if commit:
            instance.save()
            self.save_m2m()
        return instance


class ContactForm(forms.Form):
    name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    subject = forms.CharField(required=True)
    message = forms.CharField(required=True)

    widgets = {
            'name': TextInput(
                attrs={
                    'class': 'form-control',
                    'required': True, }, ),
            'email': EmailInput(
                attrs={
                    'class': 'form-control',
                    'required': True, }, ),
            'subject': TextInput(
                attrs={
                    'class': 'form-control',
                    'required': True, }, ),
            'message': Textarea(
                attrs={
                    'class': 'form-control',
                    'required': True,
                    'rows': 20 }, ),
        }

    def send_email(self):
        name = self.cleaned_data['name']
        email = self.cleaned_data['email']
        subject = self.cleaned_data['subject']
        message = self.cleaned_data['message']

        print(self.cleaned_data)
        try:
            send_mail(subject, message, name,
                ['name@domain.com', ])
        except BadHeaderError:
            return HttpResponse('Invalid header found.')