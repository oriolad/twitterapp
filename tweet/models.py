from django import forms
from django.db import models

class RegisterForm(forms.Form):
	username = forms.CharField(label="Username:", max_length=100, required=True)
	email = forms.EmailField(label="Email:", required=True)
	password = forms.CharField(label="Password:",widget=forms.PasswordInput, required=True)

class LoginForm(forms.Form):
	username = forms.CharField(label="Username:", required=True)
	password = forms.CharField(widget=forms.PasswordInput, required=True)
	
class Tweet(models.Model):
	message = models.CharField(max_length=150)
	username = models.CharField(max_length=100)
	created = models.DateTimeField(auto_now_add=True)
	published = models.BooleanField(default=True)

	def __unicode__(self):
		return self.username

class userFollowing(models.Model):
	username = models.CharField(max_length=100)
	userFollowed = models.CharField(max_length=100)

	class Meta:
		unique_together = ["username", "userFollowed"]

	def __unicode__(self):
		return self.username

