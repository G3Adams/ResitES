from unicodedata import name
from xml.etree.ElementInclude import include
from django.urls import URLPattern, path

from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
path('', views.newHome, name='newHome'),
path('login', views.loginPage, name='login'),
path('logout', views.logoutRequest, name='logout'),
path('cinemaManager', views.cinemaManager, name='cinemaManager'),
path('accountManager', views.accountManager, name='accountManager'),
path('addClubPost', views.addClubPost, name='addClubPost'),
path('addStudentClubRep/<int:club_id>/', views.addStudentClubRepPost, name='addStudentClubRep'),
path('club/modifyClub/<int:club_id>/',views.modifyClubPost,name='modifyClub'),
path('club/modifyUser/<int:user_id>/<int:club_id>/',views.modifyUserPost,name='modifyUser'),
path('films',views.films,name='films'),
path('screenManagement',views.screenManagement,name='screenManagement'),
path('addScreenPost',views.addScreenPost,name='addScreen'),
path('screenManagement/modify-screen/<int:screen_id>/',views.modifyScreenPost,name='modifyFilm'),
path('addFilmPost',views.addFilmPost,name='addFilm'),
path('cancellation', views.cancellationRequestAdd, name='cancellation'),
path('studentJoinRequest', views.studentRequestForm, name='studentJoinRequest'),
path('discountRequest', views.discountRequestForm, name='discountRequest'),
path('acceptDiscountRequest/<int:discount_id>/', views.acceptDiscountRequest, name='acceptDiscountRequest'),
path('declineDiscountRequest/<int:discount_id>/', views.declineDiscountRequest, name='declineDiscountRequest'),
path('acceptUserRequest/<int:request_id>/', views.acceptUserRequest, name='acceptUserRequest'),
path('declineUserRequest/<int:request_id>/', views.denyUserRequest, name='declineUserRequest'),
path('loginRedirectBtn',views.loginRedirectBtn,name='loginRedirectBtn'),
path('film/modify-film/<int:film_id>/',views.modifyFilmPost,name='modifyFilm'),
path('home/film-detail/<int:film_id>/<int:showing>',views.filmDetails,name="viewFilm"),
path('<int:film_id>/<screen_date>-<screen_month>/<str:showTime>/<int:screenId>/<int:year>',views.buyTicket,name="buyTicket"),
path('managerHome',views.cinemaManagerHome,name='cineManagerHome'),
path('selfModifyAccount',views.selfModifyUser,name='selfModifyAccount'),
path('buyCredit',views.buyCredit,name='buyCredit'),
path('acceptDenyCancelations/<int:cancel_id>/',views.acceptOrDenyCancel,name='acceptDenyCancelations'),
path('cancelTicketLoggedIn/<int:ticket_id>/',views.cancelTicketLoggedIn,name='cancelTicketLoggedIn'),
path('viewDailyTransactions',views.viewDailyTransactions,name='viewDailyTransactions'),
path('monthlyYearlyReport',views.monthlyYearlyReport,name='monthlyYearlyReport'),
path('yearlyReport',views.yearlyReport,name='yearlyReport'),
path('checkOut/<int:showTime_id>/',views.checkOut,name='checkOut')
]

if settings.DEBUG:
  urlpatterns += static(settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT)