"""
View handlers for HTML serving
"""

from django.template import RequestContext, loader
from django.http import (
    HttpResponse,
)

from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect

from .forms import *


@login_required
def index(request):
    """
    Returns a basic HTML snippet rendering of a notification count
    """

    template = loader.get_template('index.html')

    context = RequestContext(request, {'user': request.user})
    return HttpResponse(template.render(context))


@csrf_protect
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password1'],
            email=form.cleaned_data['email']
            )
            return HttpResponseRedirect('/register/success/')
    else:
        form = RegistrationForm()
        variables = RequestContext(
            request, {
                'form': form
            }
        )

    return render_to_response(
        'registration/register.html',
        variables,
    )

def register_success(request):
    return render_to_response(
        'registration/success.html',
    )

def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/')
