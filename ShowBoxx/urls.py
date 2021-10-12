"""ShowBoxx URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from myfunction import *

urlpatterns = [
    path('admin/', admin.site.urls),

    path('start',start),
    path('login',login),
    path('signin',signin),
    path('signup',signup),
    path('addUser',addUser),

    path('manageMovies',manageMovies),
    path('insertMovie',insertMovie),
    path('addMovie',addMovie),
    path('editMovie',editMovie),
    path('edittedMovie',edittedMovie),
    path('editEpisode',editEpisode),
    path('editedEpisode',editedEpisode),
    path('deleteVideo',deleteVideo),
    path('manageEpisodes',manageEpisodes),
    path('addEpisode',addEpisode),
    path('insertEpisode',insertEpisode),
    path('deleteEpisode',deleteEpisode),
    path('insertGenre',insertGenre),
    path('addGenre',addGenre),
    path('viewGenre',viewGenre),
    path('editGenre',editGenre),
    path('genreEditted',genreEditted),
    path('deleteGenre',deleteGenre),
    path('plans',plans),
    path('editplan',editplan),
    path('subscriptions',subscriptions),
    path('showUserInvoice',showUserInvoice),
    path('invoiceDetails',invoiceDetails),
    path('adminsDetails',adminsDeatils),
    path('addAdmin',addAdmin),
    path('adminAccount',adminAccount),
    path('editAdminDetails',editAdminDetails),
    path('changeStatus',changeStatus),
    path('viewUsers',viewUsers),
    path('changeUserStatus',changeUserStatus),
    path('changeAdminPassword',changeAdminPassword),
    path('forgotPassword',forgotPassword),
    path('generateOtp',generateOtp),
    path('enterOtp',enterOtp),
    path('newPassword',newPassword),
    path('resetPassword',resetPassword),


    path('userHome',userHome),
    path('userMovies',userMovies),
    path('userShows',userShows),
    path('coverPage',coverPage),
    path('playVid',playVid),
    path('addToWatchList',addToWatchList),
    path('removeFromWatchList',removeFromWatchList),
    path('watchList',watchList),
    path('videoSearch',videoSearch),
    path('changeUserPassword',changeUserPassword),
    path('userAccount',userAccount),
    path('editUserDetails',editUserDetails),

    path('logout',logout),
    path('subPage',subPage),
    path('payment',payment),
    path('addReview',addReview),
    path('deleteReview',deleteReview)
]
