# Create your views here.
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import login as auth_login
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext 
import datetime, random, hashlib
from tweet.models import Tweet
from tweet.models import userFollowing


def userfound(request):
	#check if current user logged in and if they searched for anything
	if 'currentUser' in request.session and 'searchedUser' in request.session:
		currentUser = request.session['currentUser']
		searchedUser = request.session['searchedUser']		

		addFollowing, created = userFollowing.objects.get_or_create(username=currentUser, userFollowed=searchedUser)
		if created:
			return render(request, 'userfound.html', {'created':created, 'searchedUser': searchedUser}, context_instance=RequestContext(request))
		else:
			return render(request, 'userfound.html', {'created':created, 'searchedUser': searchedUser}, context_instance=RequestContext(request))
	#user logged in, did not search
	elif 'currentUser' in request.session and 'searchedUser' not in request.session:
		return render(request, 'usersearch.html', {'found': False, 'searchedUser': "NONE", 'foundUser': "NONE", 'result': "User not found."}, context_instance=RequestContext(request))
	#user not logged in
	else:
		return render(request, 'index.html', {'result': "You did not login yet."}, context_instance=RequestContext(request))
	
def twitter(request):
	if 'currentUser' in request.session:
		currentUser = request.session['currentUser']
		myTweets = Tweet.objects.filter(username=currentUser)
		theirTweetList = []

		getFollowedUsers = userFollowing.objects.filter(username=currentUser)
		for f in getFollowedUsers:
			followedTweets = Tweet.objects.filter(username=f.userFollowed)
			for t in followedTweets:
				theirTweetList.insert(0, t) 

		if 'searchUser' in request.POST:
			searchedUser = request.POST['searchUser']
			request.session['searchedUser'] = searchedUser
			return HttpResponseRedirect("/usersearch/")

		if 'incomingTweet' in request.POST:
			newTweet = request.POST['incomingTweet']
			#process tweet_post, then save in database
			if len(newTweet) <= 140 and len(newTweet) > 1:
				addTweet = Tweet(message=newTweet,username=currentUser)
				addTweet.save()
				#add new tweet
				return render(request, 'twitter.html', {'result': "", 'currentUser': currentUser, 'myTweets':myTweets, 'theirTweets': theirTweetList}, context_instance=RequestContext(request))
			else:
				return render(request, 'twitter.html', {'result': "Your tweet needs to be between 1 to 140 characters.", 'currentUser': currentUser, 'myTweets': myTweets, 'theirTweets': theirTweetList}, context_instance=RequestContext(request))
		else:
			return render(request, 'twitter.html', {'result': "", 'currentUser': currentUser, 'myTweets':myTweets, 'theirTweets': theirTweetList}, context_instance=RequestContext(request))
	else:
		return render(request, 'index.html', {'result': "You did not login yet."}, context_instance=RequestContext(request))

def usermanagement(request):
	if 'currentUser' in request.session:
		currentUser = request.session['currentUser']

		getFollowedUsers = userFollowing.objects.filter(username=currentUser)

		if 'unfollow' in request.POST:
			userSelected = request.POST['userSelected']
			u = userFollowing.objects.get(username=currentUser,userFollowed=userSelected)
			u.delete()
			return render(request, 'usermanagement.html', {'delete': True, 'usersFollowedList': getFollowedUsers}, context_instance=RequestContext(request))
		else:
			return render(request, 'usermanagement.html', {'delete': False, 'usersFollowedList': getFollowedUsers}, context_instance=RequestContext(request))
	else:
		return render(request, 'index.html', {'result': "You did not login yet."}, context_instance=RequestContext(request))

def index(request):
	#if there is a login request
	if 'loginForm' in request.POST:
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		if user is not None and user.is_active:
			#is the password correct, then login
			auth_login(request, user)
			request.session['currentUser'] = user
			#redirect to success page
			return HttpResponseRedirect("/twitter/")
		else:
			#error page
			return render(request, 'index.html', {'result': "Wrong username or password. Please try again."}, context_instance=RequestContext(request))
	#if there is a register request
	if 'registerForm' in request.POST:
		username = request.POST['username']
		email = request.POST['email']
		password = request.POST['password']
		if len(username) < 3:
			return render(request, 'index.html', {'result': "Your username must be greater than 3 characters."}, context_instance=RequestContext(request))
		elif len(password) < 3:
			return render(request, 'index.html', {'result': "Your password must be greater than 3 characters."}, context_instance=RequestContext(request))
		elif "@" not in email:
			return render(request, 'index.html', {'result': "Please enter a valid email address."}, context_instance=RequestContext(request))
		else:
			u = User.objects.create_user(username=username,email=email,password=password)
			u.save()
			user = authenticate(username=username, password=password)
			auth_login(request, user)
			request.session['currentUser'] = user
			#redirect to success page
			return HttpResponseRedirect("/twitter/")
	#else display all forms
	else:
		return render(request, 'index.html', {'result': ""}, context_instance=RequestContext(request))

def logout(request):
	auth_logout(request)
	request.session.items = []
	request.session.modified = True
	return HttpResponseRedirect("/")

def usersearch(request):
	if 'searchedUser' in request.session and 'currentUser' in request.session:
		searchedUser = request.session['searchedUser']
		currentUser = request.session['currentUser']
		foundUser = ""

		if searchedUser == currentUser.get_username():
			return render(request, 'usersearch.html', {'found': False, 'searchedUser': searchedUser, 'foundUser': "NONE", 'result': "You cannot add yourself."}, context_instance=RequestContext(request))

		try:
			foundUser = User.objects.get(username=searchedUser)
			found = True
		except User.DoesNotExist:
			found = False

		if found is True:
			if 'followForm' in request.POST:
				return HttpResponseRedirect("/userfound/")
			else:
				return render(request, 'usersearch.html', {'found': found, 'searchedUser': searchedUser, 'foundUser': foundUser, 'result': "User found."}, context_instance=RequestContext(request))                
		else:
			return render(request, 'usersearch.html', {'found': found, 'searchedUser': searchedUser, 'foundUser': foundUser, 'result': "User not found."}, context_instance=RequestContext(request))	
	elif 'searchedUser' not in request.session and 'currentUser' in request.session:
		#user has logged in but not searched for anything
		return render(request, 'usersearch.html', {'found': False, 'searchedUser': "NONE", 'foundUser': "NONE", 'result': "User not found."}, context_instance=RequestContext(request))
	else:
		#user not logged in
		return render(request, 'index.html', {'result': "You did not login yet."}, context_instance=RequestContext(request))