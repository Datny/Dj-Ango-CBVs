from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from . models import Hall, Video
from . forms import VideoForm, SearchForm



def add_video(request, pk):
    form = VideoForm()
    search_form = SearchForm()
    if request.method == "POST":
        filled_form = VideoForm(request.POST)
        if filled_form.is_valid():
            video = Video()
            video.title = filled_form.cleaned_data['title']
            video.url = filled_form.cleaned_data['url']
            video.youtube_id = filled_form.cleaned_data['youtube_id']
            video.hall = Hall.objects.get(pk=pk)
            video.save()

    return render(request, 'core/add_video.html', {"form": form, 'search_form': search_form})




# Create your views here.
def home(request):
    return render(request,"core/home.html")

def dashboard(request):
    return render(request,"core/dashboard.html")

class DetailHall(generic.DetailView):
    model = Hall
    template_name = "core/detail_hall.html"


class UpdateHall(generic.UpdateView):
    model = Hall
    template_name = "core/update_hall.html"
    fields = ['title']
    success_url = reverse_lazy('dashboard')

class DeleteHall(generic.DeleteView):
    model = Hall
    success_url = reverse_lazy("dashboard")
    template_name = 'core/delete_hall.html'


    def delete(self, request, *args, **kwargs):
       self.object = self.get_object()
       if self.object.user == request.user:
          self.object.delete()
          return redirect(self.get_success_url())
       else:
          return redirect('login')


class CreateHall(generic.CreateView):
    model = Hall
    fields = ['title']
    template_name = 'core/create_hall.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.user = self.request.user
        super().form_valid(form)
        return redirect('home')


class SignUp(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('home')
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        view = super().form_valid(form)
        username, password = form.cleaned_data.get('username'), form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        login(self.request, user)
        return view
