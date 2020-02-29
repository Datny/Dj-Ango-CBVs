from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.forms import UserCreationForm
from . models import Hall
# Create your views here.
def home(request):
    return render(request,"core/home.html")

class CreateHall(generic.CreateView):
    model = Hall
    fields = ['title']
    template_name = 'core/create_hall.html'
    success_url = reverse_lazy('home')

class SignUp(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('home')
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        super(CreateHall, self).form_valid(form)
        return redirect('home')
