from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from . models import Hall, Video
from . forms import VideoForm, SearchForm
from django.http import Http404, JsonResponse
import urllib
from django.forms.utils import ErrorList
import requests as pyt_request
from .ignored import YOUTUBE_API_KEY


def video_search(request):
    search_form = SearchForm(request.GET)
    if search_form.is_valid():
        encoded_search_term = urllib.parse.quote(search_form.cleaned_data['search_term'])
        response = pyt_request.get(f'https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=5&q={encoded_search_term}&key={YOUTUBE_API_KEY}')
        return JsonResponse(response.json())
    return JsonResponse({'error': 'Cant validate incoming data'})

def add_video(request, pk):
    form = VideoForm()
    search_form = SearchForm()
    hall = Hall.objects.get(pk=pk)
    if not hall.user == request.user:
        raise Http404
    if request.method == "POST":
        form = VideoForm(request.POST)
        if form.is_valid():
            video = Video()
            video.url = form.cleaned_data['url']
            parsed_url = urllib.parse.urlparse(video.url)
            video_id = urllib.parse.parse_qs(parsed_url.query).get('v')
            if video_id:
                video.youtube_id = video_id[0]
                response = pyt_request.get(f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id[0]}&key={YOUTUBE_API_KEY}")
                json_response = response.json()
                video.title = json_response['items'][0]['snippet']['title']
                video.hall = hall
                video.save()
                return redirect('detail_hall', pk)
            else:
                errors = form._errors.setdefault('url', ErrorList())
                errors.append('Need to be a Correct YouTube url')

    return render(request, 'core/add_video.html', {"form": form, 'search_form': search_form, 'hall': hall})


# Create your views here.
def home(request):
    return render(request,"core/home.html")

def dashboard(request):
    halls = Hall.objects.filter(user= request.user)
    return render(request, "core/dashboard.html", {'hallz': halls})

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

class DeleteVideo(generic.DeleteView):
    model = Video
    success_url = reverse_lazy("dashboard")
    template_name = 'core/delete_video.html'


    # def delete(self, request, *args, **kwargs):
    #    self.object = self.get_object()
    #    if self.object.user == request.user:
    #       self.object.delete()
    #       return redirect(self.get_success_url())
    #    else:
    #       return redirect('login')

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
