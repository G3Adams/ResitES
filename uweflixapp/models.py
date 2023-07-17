from distutils.command.upload import upload
import email
from email.headerregistry import Address
from multiprocessing import Manager
from pyexpat import model
from sre_parse import State
from unicodedata import name
from django.db import models


from django.forms import CharField
from django.contrib.auth.base_user import BaseUserManager,AbstractBaseUser

#from uweflixapp.models import User
#User.objects.createCinemaManager("admin","admin","cineadmin","1234")
#User.objects.createAccountsManager("adminAcc","adminAcc","accadmin","1234")
#User.objects.all()

# from uweflixapp.models import Ticket
# Ticket(ticketId="432431312", ticketType="Guest",purchaseDate="2022-05-02", film="SpiderMan",price=10.0, showingRoom="B4A", showingDate="2022-12-10",startTime="12:30", endTime="1:30",firstName="dave",lastName="john" ).save()
# Ticket(ticketId="435346324", ticketType="Guest",purchaseDate="2022-05-02", film="Bob",price=20.0, showingRoom="B4A", showingDate="2022-12-10",startTime="12:30", endTime="1:30",firstName="dave",lastName="john" ).save()
# Ticket(ticketId="555555555", ticketType="Guest",purchaseDate="2022-05-02", film="SpiderMan",price=30.0, showingRoom="B4A", showingDate="2022-12-10",startTime="12:30", endTime="1:30",firstName="dave",lastName="john" ).save()
# Ticket(ticketId="324524676", ticketType="Guest",purchaseDate="2022-05-02", film="SpiderMan",price=40.0, showingRoom="B4A", showingDate="2022-01-01",startTime="12:30", endTime="1:30",firstName="dave",lastName="john" ).save()
# Ticket(ticketId="146764443", ticketType="Guest",purchaseDate="2022-05-02", film="SpiderMan",price=50.0, showingRoom="B4A", showingDate="2022-01-01",startTime="12:30", endTime="1:30",firstName="dave",lastName="john" ).save()

# Ticket(ticketId="333333333",userName="00000000964",purchaseDate="2022-05-02", ticketType="ClubRep", film="SpiderMan",price=10.0, showingRoom="B4A", showingDate="2022-12-10",startTime="12:30", endTime="1:30",firstName="Bobby",lastName="Jim" ).save()
# Ticket(ticketId="444444444",userName="00000000964",purchaseDate="2022-05-02", ticketType="ClubRep", film="SpiderMan",price=10.0, showingRoom="B4A", showingDate="2022-12-10",startTime="12:30", endTime="1:30",firstName="Bobby",lastName="Jim" ).save()
# Ticket(ticketId="555555555",userName="00000000964",purchaseDate="2022-05-02", ticketType="ClubRep", film="SpiderMan",price=10.0, showingRoom="B4A", showingDate="2022-12-10",startTime="12:30", endTime="1:30",firstName="Bobby",lastName="Jim" ).save()
# Ticket(ticketId="635345355",userName="00000000964",purchaseDate="2022-05-02", ticketType="ClubRep", film="SpiderMan",price=10.0, showingRoom="B4A", showingDate="2022-01-01",startTime="12:30", endTime="1:30",firstName="Bobby",lastName="Jim" ).save()
# Ticket(ticketId="665465342",userName="00000000964",purchaseDate="2022-05-02", ticketType="ClubRep", film="SpiderMan",price=10.0, showingRoom="B4A", showingDate="2022-01-01",startTime="12:30", endTime="1:30",firstName="Bobby",lastName="Jim" ).save()

# Create your models here.
class Screen(models.Model):
    roomNo = models.CharField(max_length=50)
    capacity = models.IntegerField()
    #Allows content to be printed out when database debugging
    def __str__(self):
        return "id: " + str(self.id) + " roomNo: " + str(self.roomNo) + " capacity: " + str(self.capacity)

class Ticket(models.Model):
    ticketId = models.CharField(max_length=100)
    ticketType = models.CharField(max_length=100)
    purchaseDate = models.DateField(default="1000-10-10")
    film = models.CharField(max_length=100)
    price = models.FloatField(default=0.0)
    
    showingRoom = models.CharField(max_length=100)
    showingDate = models.DateField(default="1000-10-10")
    startTime = models.TimeField()

    firstName = models.CharField(max_length=100)
    lastName = models.CharField(max_length=100)
    email = models.CharField(max_length=100,default='Not Guest')
    phone = models.CharField(max_length=100,default='Not Guest')
    userName = models.CharField(max_length=100, default="Guest")

    cancelInProgress = models.CharField(max_length=20,default="No")
    #Allows content to be printed out when database debugging
    def __str__(self):
        return "id: " + str(self.ticketId) + " ticketType: " + str(self.ticketType) + " price: " + str(self.price) + " film: " + str(self.film) + ' FirstName: ' + self.firstName + " LastName: " + self.lastName + " SHOWINGDATE: " + str(self.showingDate)

class Cinema(models.Model):
    name = models.CharField(max_length=100,primary_key = True)
    manager = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    #Allows content to be printed out when database debugging
    def __str__(self):
        return "name: " + str(self.name) + " manager: " + str(self.manager) + " address: " + str(self.address)

def filepath(request,filename):
    old_filename = filename
    

class Film(models.Model):
    image = models.ImageField(upload_to='film_images/', default='defaultFilm.jpg')
    title = models.CharField(max_length=100)
    ageRating = models.CharField(max_length=50)
    duration = models.CharField(max_length=75)
    teirOneAdvert = models.BooleanField(default=False)
    teirTwoAdvert = models.BooleanField(default=False)
    desc = models.CharField(max_length=200)
    def __str__(self):
        return "title: " + str(self.title) + " ageRating: " + str(self.ageRating) + " duration: " + str(self.duration) + " desc: " + str(self.desc)

class ShowTime(models.Model): 
    showDate = models.DateField()
    endDate = models.DateField()
    screenId = models.ForeignKey(Screen,null=True,blank=True,on_delete=models.CASCADE)
    filmId = models.ForeignKey(Film,null=True,blank=True,on_delete=models.CASCADE)
    screeningTime = models.TimeField(default=5)
    price = models.FloatField(default=5.55)

class ShowTimeChild(models.Model):
    showTime = models.ForeignKey(ShowTime,null=True,blank=True,on_delete=models.CASCADE)
    date = models.DateField()
    TicketLeft = models.IntegerField()

# class Ticket(models.Model):
#     ticketId = models.CharField(max_length=100)
#     ticketType = models.CharField(max_length=100)
#     purchaseDate = models.DateField(default="1000-10-10")
#     film = models.CharField(max_length=100)
#     price = models.IntegerField()
    
#     showingRoom = models.ForeignKey(ShowTime, on_delete=models.CASCADE,null=True,blank=True)
#     showingDate = models.DateField(default="1000-10-10")
#     startTime = models.TimeField()
#     endTime = models.TimeField()

#     firstName = models.CharField(max_length=100)
#     lastName = models.CharField(max_length=100)
#     userName = models.CharField(max_length=100, default="Guest")

#     cancelInProgress = models.CharField(max_length=20,default="No")
#     #Allows content to be printed out when database debugging
#     def __str__(self):
#         return "id: " + str(self.id) + " ticketType: " + str(self.ticketType) + " price: " + str(self.price) + " film: " + str(self.film)



class Club(models.Model):
    name = models.CharField(max_length=100)
    buildingName = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postCode = models.CharField(max_length=100)
    contactNumber = models.CharField(max_length=100)

    
    #Allows content to be printed out when database debugging
    def __str__(self):
        return "id: " + str(self.id) + " name: " + str(self.name) + " address: " + str(self.buildingName) + " email: " + str(self.street) + " phoneNumber: " + str(self.city)
  
class CreditCard(models.Model):
    nameOnCard = models.CharField(max_length=100,default="")
    cardNumber = models.CharField(max_length=100,default="")
    expiryDate = models.DateField(default="")

class StudentJoinRequests(models.Model):
    firstName= models.CharField(max_length=200)
    lastName= models.CharField(max_length=200)
    birthDay = models.DateField(default="")
    club = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    is_clubRep = models.BooleanField(default=False)
    is_Student = models.BooleanField(default=False)
    def __str__(self):
        return "firstName: " + str(self.firstName) + " lastName: " + str(self.lastName)+ " club: " + str(self.club)+ " password: " + str(self.password)+ " is_clubRep: " + str(self.is_clubRep)+ " is_Student: " + str(self.is_Student)

class DiscountRequests(models.Model):
    userName = models.CharField(max_length=200)
    firstName = models.CharField(max_length=200)
    lastName = models.CharField(max_length=200)
    discountRate = models.IntegerField(default=0)
    def __str__(self):
        return "userName: " + str(self.userName) + " firstName: " + str(self.firstName)+ " lastName: " + str(self.lastName)+ " discountRate: " + str(self.discountRate)

class Cancelations(models.Model):
    ticketId = models.CharField(max_length=100)
    firstName = models.CharField(max_length=100)
    lastName = models.CharField(max_length=100)
    userMakingRequest = models.CharField(max_length=100, default="Guest")
    requestReason = models.CharField(max_length=100, default="N/A")

class AcceptedCancelations(models.Model):
    ticketId = models.CharField(max_length=100)
    purchaseDate = models.DateField(default="1000-10-10")
    price = models.FloatField(default=0.0)
    firstName = models.CharField(max_length=100)
    lastName = models.CharField(max_length=100)
    requestReason = models.CharField(max_length=100, default="N/A")


class UserManager(BaseUserManager):
    def createClubRep(self,firstName,lastName,theClub,unequeNumber,password,inputCreditCard,inputDiscountRate,birthDateIn):
        user = self.model(
            firstName=firstName,
            lastName=lastName,
            userName=unequeNumber,
        )
        user.birthDate = birthDateIn
        user.discountRate = inputDiscountRate
        user.creditCard = inputCreditCard
        user.club=theClub
        user.is_clubRep = True
        user.set_password(password)
        user.save(using=self.db)
        return user
    
    def createStudent(self, firstName,lastName,theClub,userName,password,inputCreditCard,inputDiscountRate,birthDateIn):
        user = self.model(
            firstName=firstName,
            lastName=lastName,
            userName=userName,
        )
        user.birthDate = birthDateIn
        user.discountRate = inputDiscountRate
        user.creditCard = inputCreditCard
        user.club=theClub
        user.is_Student = True
        user.set_password(password)
        user.save(using=self.db)

    def createCinemaManager(self, firstName,lastName,userName, password):
        user = self.model(
            userName=userName,
            firstName=firstName,
            lastName=lastName,
        )
        user.is_superuser = True
        user.is_CinemaManager = True
        user.set_password(password)
        user.save(using=self.db)
        
    def createAccountsManager(self, firstName,lastName,userName,password):
        user = self.model(
            userName=userName,
            firstName=firstName,
            lastName=lastName,
        )
        user.is_AccountsManager = True
        user.set_password(password)
        user.save(using=self.db)
        

class User(AbstractBaseUser):
    REQUIRED_FIELDS = ["firstName","lastName"]
    USERNAME_FIELD = "userName"

    objects = UserManager()
    
    #basic template for all users, depending on user some of these fields may not be used
    firstName= models.CharField(max_length=200)
    lastName= models.CharField(max_length=200)
    club = models.ForeignKey(Club, on_delete=models.PROTECT,null=True,blank=True)
    userName= models.CharField(max_length=200,unique=True)
    birthDate = models.DateField(default="1000-10-10")
    #Credit and billing info
    discountRate = models.IntegerField(default=0)
    credit = models.FloatField(default=0.0)

    creditCard = models.ForeignKey(CreditCard, on_delete=models.CASCADE,null=True,blank=True)
    
    #Following lines are used for security, stopping unauthorised access to pages.
    is_superuser = None
    is_clubRep = models.BooleanField(default=False)
    is_Student = models.BooleanField(default=False)
    is_CinemaManager = models.BooleanField(default=False)
    is_AccountsManager = models.BooleanField(default=False)




