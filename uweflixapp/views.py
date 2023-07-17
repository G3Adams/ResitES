from unicodedata import name
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from uweflixapp.models import CreditCard, User,Film,Club,StudentJoinRequests,DiscountRequests,DiscountRequests,Cancelations,Ticket,AcceptedCancelations
from django.contrib.auth import authenticate, login,logout
from .forms import AddClubForm,LoginForm,AddFilmForm,ModifyClubForm,AddStudentClubRepForm,ModifyStudentClubRepForm,StudentJoinRequestForm,DiscountRequestForm,selfModifyUserForm,CancellationForm,BuyCreditForm,CancellationsLoggedInForm,ViewDailyTransactionsForm,MonthReportForm,YearlyReportForm
import random
import datetime
from django.contrib import messages
from datetime import date, timedelta

from uweflixapp.models import Club

from uweflixapp.models import User
from uweflixapp.models import Film
from uweflixapp.models import Screen
from uweflixapp.models import ShowTime
from uweflixapp.models import ShowTimeChild

from django.contrib.auth import authenticate, login
from .forms import AddClubForm
from .forms import LoginForm
from django.contrib.auth import logout
from .forms import AddFilmForm
from .forms import AddScreenForm
from .forms import AddShowTimeForm
from .forms import checkOutForm

import calendar
from django.db.models import Q



def index(request):
    return render(request, 'index.html')

def logoutRequest(request):
    logout(request)
    return HttpResponseRedirect("/")
    
    
#Function redirects user to user account home page depending on who is logged in.
def loginRedirectBtn(request):
    if(request.user.is_anonymous == True):
        return render(request, 'login.html')
    elif(request.user.is_CinemaManager == True):
        return HttpResponseRedirect("/cinemaManager") 
    elif(request.user.is_AccountsManager == True):
        return HttpResponseRedirect("/accountManager") 
    elif(request.user.is_clubRep == True or request.user.is_Student == True):
        return HttpResponseRedirect("/selfModifyAccount") 
    else:
        return HttpResponseRedirect("/loginPage") 


#Function handles loging users in.
def loginPage(request):
    if (request.method == 'POST'):
        print("is post")
        form = LoginForm(request.POST)
        print(form.errors)
        if(form.is_valid()):# If the form is valid then.
            username = form.cleaned_data['userName'] #get username from form.
            password = form.cleaned_data['password'] #get password from form.
            print("form Valid")
            user = authenticate(request, username=username, password=password) # Authenticate username and password.
            if user is not None:
                login(request, user) # Log User in
                print("valid user")
                request.session.set_expiry(1200)#Session will expire after 20 minutes of inactivity.
                return HttpResponseRedirect("/")# Take user to home page
            else:
                # Return an 'invalid login' error message.
                print("invalid user")
                messages.error(request, 'Login Credentials Invalid')
                return HttpResponseRedirect("/login") 
        else:
            print("form not Valid")
    else:
        form = LoginForm()
    return render(request, 'Login.html',{'form':form})


# Function handles cinema manager page.
def cinemaManager(request):
    if(request.user.is_anonymous == True): # Checks to see if user is logged in, within current session.
        return render(request, 'login.html')
    if (request.user.is_CinemaManager == True): # Checks to see if cinema manager is logged in.
        clubs = Club.objects.all() # gets all clubs
        users = User.objects.select_related('club') # gets all users
        clubRepList = []
        for club in clubs: # for each club
            for user in users:# for each user in database
                    if(user.is_clubRep == True): # check to see if user is club rep
                        #DO NOT MERGE IF STATEMENT: Has to be like this as club(ForeignKey) can be equal to none in model, 
                        #otherwise get error "'NoneType' object has no attribute 'name'"
                        if(club.name == user.club.name): #If they are a club rep
                            clubRepList.append(user.firstName) # append club rep to club rep list
                            break
        accountRequests = StudentJoinRequests.objects.all() #get all student join requests
        discountRequests = DiscountRequests.objects.all() # gets all discount requests
        cancelationRequests = Cancelations.objects.all()
        clubPair = zip(clubs, clubRepList) # pairs clubs and clubreplist
        content={
            'clubPair':clubPair,
            'accountRequests':accountRequests,
            'discountRequests':discountRequests,
            'cancelationRequests':cancelationRequests
        }
        return render(request, 'cinemaManager.html', content)
    else:
        return render(request, 'login.html')


#Function create uneique random username.
def createUniqueNum(num):
    array = [str(num * random.randint(2,1000))]
    while len(array) < 9:
        array.insert(0,"0")
    return "".join(array)


# Function used to accept user sign up request
def acceptUserRequest(request,request_id=False):
    if(request.user.is_anonymous == True): # Checks to see if user is logged in, within current session.
        return render(request, 'login.html')
    if (request.user.is_CinemaManager == True): # Checks to see if cinema manager is logged in.
        userRequest = StudentJoinRequests.objects.get(id=request_id) # Gets student request to accept.
        club = Club.objects.get(name=userRequest.club) # gets club user wants to join.
        recordCount = User.objects.all().count() # get ammount of users.
        
        if(userRequest.is_clubRep == True):# if the user wants to be a club rep, make them a club rep.
           User.objects.createClubRep(userRequest.firstName, userRequest.lastName,club, createUniqueNum(recordCount),userRequest.password,None,0,userRequest.birthDay)
        elif(userRequest.is_Student == True):# if the user wants to be a student, make them a student.
           User.objects.createStudent(userRequest.firstName, userRequest.lastName,club, createUniqueNum(recordCount),userRequest.password,None,0,userRequest.birthDay)
        userRequest.delete()# Delete the sign up request after user account is created.
        return HttpResponseRedirect("/cinemaManager") 
    else:
        return render(request, 'login.html')


# Function used to deny user sign up request
def denyUserRequest(request,request_id=False):
    if(request.user.is_anonymous == True):# Checks to see if user is logged in, within current session.
        return render(request, 'login.html')
    if (request.user.is_CinemaManager == True):# Checks to see if cinema manager is logged in.
        userRequest = StudentJoinRequests.objects.get(id=request_id) # Gets student request to deny.
        userRequest.delete()# Delete the sign up request
        return HttpResponseRedirect("/cinemaManager") 


# Function use to handle the student request form.
def studentRequestForm(request):
    if (request.method == 'POST'):
        print("is post")
        form = StudentJoinRequestForm(request.POST)
        print(form.errors)
        if(form.is_valid()): # if form is valid
            print("form Valid")
            
            # get the type of use the user wants to be
            userType = form.cleaned_data['userType'] 
            userStudent = False
            userClubRep = False
            if(userType == "student"):
                userStudent = True
            elif(userType == "clubrep"):
                userClubRep = True
            
            # Format user birthday.
            birthDateFormat = "{year}-{month}-{day}"
            birthDateIn = birthDateFormat.format(day=form.cleaned_data['birthDay'],month=form.cleaned_data['birthMonth'],year=form.cleaned_data['birthYear'])
            # Add student sign up request to database.
            requests = StudentJoinRequests(firstName=form.cleaned_data['firstName'],lastName=form.cleaned_data['lastName'],birthDay=birthDateIn,club=form.cleaned_data['club'],password=form.cleaned_data['password'],is_clubRep=userClubRep,is_Student=userStudent)
            requests.save()
            return HttpResponseRedirect("/")
        else:
            print("form not Valid")
            return HttpResponseRedirect("/") 
    else:
        clubs = Club.objects.all()
        return render(request, 'studentJoinRequest.html',{'clubs':clubs})


#Function allows user to cancel tickets.
def cancellationRequestAdd(request):
    if (request.method == 'POST'):# If the request method is post (User is going to submit something)
        print("is post")
        form = CancellationForm(request.POST)
        print(form.errors)
        if(form.is_valid()): # ensures form is valid
            print("form Valid")
            tickets = Ticket.objects.all()
            print("BEANS")
            print(tickets)
            ticketIdIn = form.cleaned_data['ticketId']
            
            if(Ticket.objects.filter(ticketId=ticketIdIn).exists() == True):
                ticket = Ticket.objects.get(ticketId=ticketIdIn)
                if(request.user.is_anonymous == True and ticket.userName == "Guest"):# If a guest is trying to cancel
                    if(ticket.firstName == form.cleaned_data['firstName'] and ticket.lastName == form.cleaned_data['lastName']):
                        now = date.today()
                        if(ticket.showingDate <= now):
                            messages.error(request, "Ticket Already Expired")
                            return HttpResponseRedirect("/cancellation")
                        else:
                            Cancelations(ticketId=ticketIdIn,firstName=form.cleaned_data['firstName'],lastName=form.cleaned_data['lastName'] , requestReason=form.cleaned_data['requestReason']).save()
                            print("Request Made")
                            return HttpResponseRedirect("/")
                    else:
                        print("No ticket with that name")
                        messages.error(request, 'No ticket with that name')
                        return HttpResponseRedirect("/cancellation") 

                elif(request.user.is_anonymous == True and ticket.userName != "Guest"):# If a guest is trying to cancel a regestered users ticket
                    print("This ticket Does not bellong to you")
                    messages.error(request, 'This ticket Does not bellong to you')
                    return HttpResponseRedirect("/cancellation") 
                else:# If a Registered user is trying to cancel
                    if(request.user.userName == ticket.userName):
                        now = date.today()
                        if(ticket.showingDate <= now):
                            messages.error(request, "Ticket Already Expired")
                            return HttpResponseRedirect("/cancellation")
                        else:
                            Cancelations(ticketId=ticketIdIn,userMakingRequest=request.user.userName,firstName=form.cleaned_data['firstName'],lastName=form.cleaned_data['lastName'] , requestReason=form.cleaned_data['requestReason']).save()
                            print("Request Made LOGGED IN USER")
                            return HttpResponseRedirect("/")
                    else:
                        print("Wrong Account logged in")
                        messages.error(request, 'Wrong Account logged in')
                        return HttpResponseRedirect("/cancellation") 
            else:
                print("No Ticket WITH THAT ID")
                messages.error(request, 'No Ticket WITH THAT ID')
                return HttpResponseRedirect("/cancellation") 

        else:
            print("form not Valid")
            return HttpResponseRedirect("/cancellation") 
    else:
        return render(request, 'cancellation.html')

#Function allows cinema manager to accept or deny cancelation requests.
def acceptOrDenyCancel(request, cancel_id=False):
    cancellation = Cancelations.objects.get(id=cancel_id)
    if(request.method == "POST"):# If the request method is post (User is going to submit something)
        print("is post")
        theTicket = Ticket.objects.get(ticketId=cancellation.ticketId)
        if(request.POST['action']=='submit'):# if the user submits the form
            if(theTicket.userName != "Guest"): # If the user is not a guest then refund
                user = User.objects.get(userName=theTicket.userName)
                price = theTicket.price * 1 - (user.discountRate/100)
                user.credit = user.credit + price
                user.save()
            AcceptedCancelations(ticketId=theTicket.ticketId,price=theTicket.price,purchaseDate=theTicket.purchaseDate,firstName=theTicket.firstName,lastName=theTicket.lastName,requestReason=cancellation.requestReason).save()
            theTicket.delete()
            cancellation.delete()
            return HttpResponseRedirect("/cinemaManager")
            
        elif(request.POST['action']=='delete'):# if the user deleted the club
            
            theTicket.cancelInProgress = "Request Rejected"
            theTicket.save()

            cancellation.delete()
            return HttpResponseRedirect("/cinemaManager")
    else:
        # (Code bellow) If the method is not post (if they have not submitted or deleted anything),
        # Load all of the data to be modified into the form.
        content={
            'cancelId':cancellation.id,
            'ticketId':cancellation.ticketId,
            'firstName':cancellation.firstName,
            'lastName':cancellation.lastName,
            'userMakingRequest':cancellation.userMakingRequest,
            'requestReason':cancellation.requestReason
        }
        return render(request, 'acceptOrDenyCancel.html', content)


# Function used to handle discount request form.
def discountRequestForm(request):
    if(request.user.is_anonymous == True):# checks to see if the user is anonymous
        return render(request, 'login.html')
    if (request.user.is_clubRep == True or request.user.is_Student == True):  # Ensures user is logged in as either club rep or student
        if (request.method == 'POST'):# If the request method is post (User is going to submit something)
            print("is post")
            form = DiscountRequestForm(request.POST)
            print(form.errors)
            if(form.is_valid()): # ensures form is valid
                print("form Valid")
                # Clean form data and add discount request to database.
                discountRequested = form.cleaned_data['discount']
                discountRequestModel = DiscountRequests(userName=request.user.userName,firstName=request.user.firstName,lastName=request.user.lastName,discountRate=discountRequested)
                discountRequestModel.save()
                # Return user to home page
                return HttpResponseRedirect("/")
            else:
                print("form not Valid")
                return HttpResponseRedirect("/discountRequest") 
        else:
            return render(request, 'discountRequestForm.html')
    else:
        return render(request, 'login.html')


# Function handles accepting user discount request
def acceptDiscountRequest(request,discount_id=False):
    if(request.user.is_anonymous == True):# checks to see if the user is anonymous
        return render(request, 'login.html')
    if (request.user.is_CinemaManager == True):# Ensures user is logged in as a cinemaManager
        # Next few lines change the users discount value and delete the request from the database.
        discountRequest = DiscountRequests.objects.get(id=discount_id)
        user = User.objects.get(userName=discountRequest.userName)
        user.discountRate = discountRequest.discountRate
        user.save()
        discountRequest.delete()
        return HttpResponseRedirect("/cinemaManager") 
    else:
        return render(request, 'login.html')


# Function handles denying user discount request
def declineDiscountRequest(request,discount_id=False):
    if(request.user.is_anonymous == True):# checks to see if the user is anonymous
        return render(request, 'login.html')
    if (request.user.is_CinemaManager == True):# Ensures user is logged in as a cinemaManager
        discountRequest = DiscountRequests.objects.get(id=discount_id) # gets discount request
        discountRequest.delete() # deletes discount request
        return HttpResponseRedirect("/cinemaManager") 
    else:
        return render(request, 'login.html')


# Function handles the account manager page.
def accountManager(request):
    if(request.user.is_anonymous == True):# checks to see if the user is anonymous
        return render(request, 'login.html')
    if (request.user.is_AccountsManager == True):# Ensures user is logged in as a Accounts manager.
        clubs = Club.objects.all()# Gets all clubs 
        users = User.objects.select_related('club') # gets all users
        clubRepList = []
        for club in clubs:# for each club
            for user in users:# for each user
                    if(user.is_clubRep == True): # check to see if club rep
                        #DO NOT MERGE IF STATEMENT: Has to be like this as club(ForeignKey) can be equal to none in model, 
                        #otherwise get error "'NoneType' object has no attribute 'name'"
                        # If club rep is part of the club append to club rep list
                        if(club.name == user.club.name):
                            clubRepList.append(user.firstName)
                            break
        clubPair = zip(clubs, clubRepList)
        content={
            'clubPair':clubPair
        }
        return render(request, 'accountManager.html', content)
    else:
        return render(request, 'login.html')


# Function facilitates the addition of clubs to database.
def addClubPost(request):
    if(request.user.is_anonymous == False): # Checks to see if user is anonymous
        if(request.user.is_CinemaManager == True or request.user.is_AccountsManager == True): # Ensures user is logged in as either a cinema manager or accounts manager.
            if (request.method == 'POST'):# If the request method is post (User is going to submit something)
                print("is post")
                form = AddClubForm(request.POST)
                print(form.errors)
                if(form.is_valid()): # If form is valid
                    print("form Valid")
                    clubNameInput = form.cleaned_data['club_name'] # get club name from form
                    # Create club
                    club = Club(name=clubNameInput,buildingName=form.cleaned_data['inputStreetNo'], street=form.cleaned_data['inputStreet'],city=form.cleaned_data['inputCity'],state=form.cleaned_data['inputState'],postCode=form.cleaned_data['inputPostcode'],contactNumber=form.cleaned_data['inputNum'])
                    club.save() # save club to database
                    #format date of birth
                    birthDateFormat = "{year}-{month}-{day}"
                    birthDate = birthDateFormat.format(day=form.cleaned_data['birthDay'],month=form.cleaned_data['birthMonth'],year=form.cleaned_data['birthYear'])
                    # Get user ammount
                    recordCount = User.objects.all().count()
                    # Create club rep user for club
                    User.objects.createClubRep(form.cleaned_data['inputFirstName'], form.cleaned_data['inputLastName'],club, createUniqueNum(recordCount),form.cleaned_data['inputPassword'],None,0,birthDate)
                    if(request.user.is_CinemaManager == True):
                        return HttpResponseRedirect("/cinemaManager")
                    elif(request.user.is_AccountsManager == True):
                        return HttpResponseRedirect("/accountManager")
                else:
                    print("form not Valid")     
            else:
                form = AddClubForm()
            return render(request, 'addClub.html', {'form':form}) 
        else:
            return render(request, 'login.html')
    else:
        return render(request, 'login.html')


# Function used to facilitates the modification of clubs.
def modifyClubPost(request,club_id=False):
    if(request.user.is_anonymous == False): # Ensures the user is not anonymous
        if(request.user.is_AccountsManager == True):# Ensures the user is a accounts manager
            if(request.method == "POST"):# If the request method is post (User is going to submit something)
                print("is post")
                if(request.POST['action']=='submit'):# if the user submits the form
                    form = ModifyClubForm(request.POST)
                    print(form.errors)
                    if(form.is_valid()): # if the form is valid
                        # Code bellow pulls modifyed data from form and updates the club in database.
                        club = Club.objects.get(id=club_id)
                        club.name = form.cleaned_data['club_name']
                        club.buildingName=form.cleaned_data['inputStreetNo']
                        club.street=form.cleaned_data['inputStreet']
                        club.city=form.cleaned_data['inputCity']
                        club.state=form.cleaned_data['inputState']
                        club.postCode=form.cleaned_data['inputPostcode']
                        club.contactNumber=form.cleaned_data['inputNum']
                        club.save()
                        print("Valid")
                        return HttpResponseRedirect("/accountManager")
                    else:
                        print("Form not valid")
                elif(request.POST['action']=='delete'):# if the user deleted the club
                    print("is delete")
                    club = Club.objects.get(id=club_id)
                
                    #The bellow section of code deletes all users(club reps and students) associated with the club
                    users = User.objects.select_related('club')
                    for user in users:
                        if(user.is_clubRep == True or user.is_Student == True):
                            #DO NOT MERGE IF STATEMENT: Has to be like this as club(ForeignKey) can be equal to none in User model, 
                            #otherwise get error "'NoneType' object has no attribute 'name'" because of user.club.name
                            if(club.name == user.club.name):
                                User.objects.get(id=user.id).delete()
                    club.delete()
                    return HttpResponseRedirect("/accountManager")
                
            else:
                # (Code bellow) If the method is not post (if they have not submitted or deleted anything),
                # Load all of the data to be modified into the form.
                club = Club.objects.get(id=club_id)
                users = User.objects.all()

                clubReps = []
                students = []

                for user in users:
                        if(user.is_clubRep == True):
                            if(club.name == user.club.name):
                                clubReps.append(user)
                        if(user.is_Student == True):
                            if(club.name == user.club.name): 
                                students.append(user)

                return render(request,'ModifyClub.html',{
                  'clubId':club_id,
                  'clubName':club.name,
                  'buildingName':club.buildingName,
                  'street':club.street,
                  'city':club.city,
                  'state':club.state,
                  'postCode':club.postCode,
                  'contactNumber':club.contactNumber,
                  'clubReps':clubReps,
                  'students':students
                })
        else:
            return render(request, 'login.html')
    else:
        return render(request, 'login.html')


#Function facilitates the addition of students and club reps to the database.
def addStudentClubRepPost(request,club_id=False):
    if(request.user.is_anonymous == False): # Ensures the user is not anonymous.
        if(request.user.is_AccountsManager == True): # Ensures the accounts manager is logged in.
            if (request.method == 'POST'):# If the request method is post (User is going to submit something)
                print("is post")
                form = AddStudentClubRepForm(request.POST)
                print(form.errors)
                if(form.is_valid()): # if the form is valid.
                    print("form Valid")
                    club = Club.objects.get(id=club_id) # get the club to add student/club rep to
                    recordCount = User.objects.all().count() # get the ammount of users currently in database.
                    # Format birthday
                    birthDateFormat = "{year}-{month}-{day}"
                    birthDate = birthDateFormat.format(day=form.cleaned_data['birthDay'],month=form.cleaned_data['birthMonth'],year=form.cleaned_data['birthYear'])
                    # Format expiry date of card
                    expDateFormat = "{year}-{month}-{day}"
                    expDate = expDateFormat.format(day="01",month=form.cleaned_data['month'],year=form.cleaned_data['year'])
                    # Create credit card.
                    creditCard = CreditCard(nameOnCard=form.cleaned_data['nameOnCard'],cardNumber=form.cleaned_data['cardNumber'],expiryDate=expDate)
                    creditCard.save() # Save credit card
                    # Depending on user type selected, create that type of user with the details provided in the form.
                    
                    if(form.data['discountRate'] == ""):
                        print("No dc rate set")
                        discountRate = 0
                    else:
                        print("dc rate set")
                        discountRate = form.cleaned_data['discountRate']

                    if(form.cleaned_data['userType'] == "clubrep"):
                        User.objects.createClubRep(form.cleaned_data['firstName'], form.cleaned_data['lastName'],club, createUniqueNum(recordCount),form.cleaned_data['password'],creditCard,discountRate,birthDate)
                    if(form.cleaned_data['userType'] == "student"):
                        User.objects.createStudent(form.cleaned_data['firstName'], form.cleaned_data['lastName'],club, createUniqueNum(recordCount),form.cleaned_data['password'],creditCard,discountRate,birthDate)
                    
                    # (Code bellow) Once user has been created and added to club take the user back to the modify club page.
                    club = Club.objects.get(id=club_id) # get club that the user was modifying last.
                    users = User.objects.all() # get all users.

                    clubReps = []
                    students = []
                    
                    # Bellow handles the data to be shown on the modify club page.
                    for user in users:
                        if(user.is_clubRep == True):
                            if(club.name == user.club.name):
                                clubReps.append(user)
                        if(user.is_Student == True):
                            if(club.name == user.club.name): 
                                students.append(user)
                    return render(request,'ModifyClub.html',{
                        'clubId':club_id,
                        'clubName':club.name,
                        'buildingName':club.buildingName,
                        'street':club.street,
                        'city':club.city,
                        'state':club.state,
                        'postCode':club.postCode,
                        'contactNumber':club.contactNumber,
                        'clubReps':clubReps,
                        'students':students
                    })
                else:
                    print("form not Valid")     
            else:
                form = AddStudentClubRepForm()
            return render(request, 'addStudentClubRepForm.html', 
            {'clubId':club_id,}
            ) 
        else:
            return render(request, 'login.html')
    else:
        return render(request, 'login.html')


# Function allows users to buy credit
def buyCredit(request):
    if(request.user.is_anonymous == False): # Ensures the user is not anonymous.
        if(request.user.is_clubRep == True or request.user.is_Student == True): # Ensures the accounts manager is logged in.
            userId = request.user.id
            user = User.objects.get(id=userId) # Get the user to be modified.
            if (request.method == 'POST'):# If the request method is post (User is going to submit something)
                print("is post")
                form = BuyCreditForm(request.POST)
                print(form.errors)
                if(form.is_valid()): # if the form is valid.
                    if(user.creditCard != None):
                        user.credit = int(form.cleaned_data['creditAmmount'])
                        user.save()
                        return HttpResponseRedirect("/selfModifyAccount")
                    else:
                        messages.error(request, 'No credit card info associated with your account')
                        return HttpResponseRedirect("/buyCredit")
                else:
                    messages.error(request, 'Form Invalid')
                    return HttpResponseRedirect("/buyCredit")
            else: 
                return render(request, 'buyCredit.html')                    
        else:
            return render(request, 'login.html')
    else:
        return render(request, 'login.html')


# Function shows student there account page.
def generateUserAccountPage(request,user):
    month = ""
    year = ""
    nameOnCard = ""
    cardNumber= ""

    if user.creditCard is None:
        print("noCard")
    else:
        nameOnCard = user.creditCard.nameOnCard
        cardNumber = user.creditCard.cardNumber
        expDate = user.creditCard.expiryDate
        month = expDate.month
        year = expDate.year
    allTickets = Ticket.objects.all()
    
    theUsersTickets = []
    for ticket in allTickets:
        if(ticket.userName == user.userName):
            now = date.today()
            if(ticket.showingDate > now):
                theUsersTickets.append(ticket)

    return render(request,'SandCRSelfModify.html',{
        'credits':user.credit,
        'discountRate':user.discountRate,
        'userName':user.userName,
        'firstName':user.firstName,
        'lastName':user.lastName,
        'birthDay':user.birthDate.day,
        'birthMonth':user.birthDate.month,
        'birthYear':user.birthDate.year,
        'nameOnCard':nameOnCard,
        'cardNumber':cardNumber,
        'month':month,
        'year':year,
        'usersTickets':theUsersTickets       
    })

# Generates yearly Financial report.
def yearlyReport(request):
    if(request.user.is_anonymous == True):# checks to see if the user is anonymous
        return render(request, 'login.html')
    if (request.user.is_AccountsManager == True):# Ensures user is logged in as a Accounts manager.
        if (request.method == 'POST'):# If the request method is post (User is going to submit something)
            form = YearlyReportForm(request.POST)
            print(form.errors)
            year = form.cleaned_data['year2']
            tickets = Ticket.objects.all()
            
            ticketsProfit = 0.0
            ticketsSold = 0
            GuestBought = 0
            RegisteredBought = 0

            for ticket in tickets:
                if(str(year) == str(ticket.purchaseDate.year)):
                    ticketsProfit = ticketsProfit + ticket.price
                    ticketsSold = ticketsSold + 1
                    if(ticket.userName == "Guest"):
                        GuestBought = GuestBought + 1
                    else:
                        RegisteredBought = RegisteredBought + 1


            cancelationAmmount = 0
            cancelationTotalLoss = 0.0
            acptCancelations = AcceptedCancelations.objects.all()

            for cancel in acptCancelations:
                if(str(year) == str(cancel.purchaseDate.year)):
                    cancelationAmmount = cancelationAmmount + 1
                    cancelationTotalLoss = cancelationTotalLoss + cancel.price

            content={
                'type':"Year",
                'date': year,
                'ticketsProfit':ticketsProfit,
                'ticketsSold':ticketsSold,
                'GuestBought':GuestBought,
                'RegisteredBought':RegisteredBought,
                'cancelationAmmount':cancelationAmmount,
                'cancelationTotalLoss':cancelationTotalLoss
            }
            return render(request, 'monthlyYearlyReport.html',content)
        else:
            return HttpResponseRedirect("/accountManager")
    else:
        return render(request, 'login.html')
# By Benjamin Ell-Jones
# Generates monthly Financial report.
def monthlyYearlyReport(request):
    if(request.user.is_anonymous == True):# checks to see if the user is anonymous
        return render(request, 'login.html')
    if (request.user.is_AccountsManager == True):# Ensures user is logged in as a Accounts manager.
        if (request.method == 'POST'):# If the request method is post (User is going to submit something)
            form = MonthReportForm(request.POST)
            print(form.errors)
            month = form.cleaned_data['month']
            year = form.cleaned_data['year1']
            tickets = Ticket.objects.all()
            
            splitMonth = [x for x in month]
            if(splitMonth[0] == "0"):
                month = splitMonth[1]

            print("Month" + month)

            ticketsProfit = 0.0
            ticketsSold = 0
            GuestBought = 0
            RegisteredBought = 0

            for ticket in tickets:
                if(str(month) == str(ticket.purchaseDate.month)  and str(year) == str(ticket.purchaseDate.year)):
                    ticketsProfit = ticketsProfit + ticket.price
                    ticketsSold = ticketsSold + 1
                    if(ticket.userName == "Guest"):
                        GuestBought = GuestBought + 1
                    else:
                        RegisteredBought = RegisteredBought + 1


            cancelationAmmount = 0
            cancelationTotalLoss = 0.0
            acptCancelations = AcceptedCancelations.objects.all()

            for cancel in acptCancelations:
                if(str(month) == str(cancel.purchaseDate.month)  and str(year) == str(cancel.purchaseDate.year)):
                    cancelationAmmount = cancelationAmmount + 1
                    cancelationTotalLoss = cancelationTotalLoss + cancel.price

            content={
                'type':"Monthly",
                'date':month+"-"+year,
                'ticketsProfit':ticketsProfit,
                'ticketsSold':ticketsSold,
                'GuestBought':GuestBought,
                'RegisteredBought':RegisteredBought,
                'cancelationAmmount':cancelationAmmount,
                'cancelationTotalLoss':cancelationTotalLoss
            }
            return render(request, 'monthlyYearlyReport.html',content)
        else:
            return HttpResponseRedirect("/accountManager")
    else:
        return render(request, 'login.html')
    
# By Benjamin Ell-Jones
# Allows account manager to view daily transactions.
def viewDailyTransactions(request):
    if(request.user.is_anonymous == True):# checks to see if the user is anonymous
        return render(request, 'login.html')
    if (request.user.is_AccountsManager == True):# Ensures user is logged in as a Accounts manager.
        if (request.method == 'POST'):# If the request method is post (User is going to submit something)
            form = ViewDailyTransactionsForm(request.POST)
            print(form.errors)
            dayMonthYear = form.cleaned_data['dayMonthYear']
            tickets = Ticket.objects.all()

            ticketsToShow = []
            
            for ticket in tickets:
                if(dayMonthYear.day == ticket.purchaseDate.day  and dayMonthYear.month == ticket.purchaseDate.month  and dayMonthYear.year == ticket.purchaseDate.year):
                    ticketsToShow.append(ticket)

            content={
                'ticketDate':dayMonthYear,
                'tickets':ticketsToShow
            }
            return render(request, 'dailyTransactions.html',content)
        else:
            return HttpResponseRedirect("/accountManager")
    else:
        return render(request, 'login.html')

#Created By Benjamin Ell-Jones
# Function allows a user to modify there own data.
def selfModifyUser(request):
    if(request.user.is_anonymous == False): # Ensures the user is not anonymous.
        if(request.user.is_clubRep == True or request.user.is_Student == True): # Ensures the accounts manager is logged in.
            userId = request.user.id
            user = User.objects.get(id=userId) # Get the user to be modified.
            if (request.method == 'POST'):# If the request method is post (User is going to submit something)
                print("is post")
                form = selfModifyUserForm(request.POST)
                print(form.errors)
                if(form.is_valid()): # if the form is valid.
                    user.firstName= form.cleaned_data['firstName']
                    user.lastName=form.cleaned_data['lastName']
                    print("Form Valid")
                    # Format birthday
                    birthDateFormat = "{year}-{month}-{day}"
                    birthDate = birthDateFormat.format(day=form.cleaned_data['birthDay'],month=form.cleaned_data['birthMonth'],year=form.cleaned_data['birthYear'])
                    user.birthDate = birthDate # Update birthday

                    if(form.data['password'] != ""):# If changes to password has been made, update in database.
                        print("password Changed")
                        messages.error(request, 'Password Changed')
                        user.set_password(str(form.cleaned_data['password']))
                    else:
                        print("Password Not Changed")

                    # If user has made no changes to credit card, do nothing
                    if (form.cleaned_data['nameOnCard'] == "" or form.cleaned_data['cardNumber'] == "" or form.cleaned_data['month'] == "" or form.cleaned_data['year'] == ""):
                        print("no Card Added")
                    # If user has made updates to card, and there is no card assigned to the user, create new card.
                    elif(user.creditCard is None and form.cleaned_data['nameOnCard'] != "" and form.cleaned_data['cardNumber'] != "" and form.cleaned_data['month'] != "" and form.cleaned_data['year'] != ""):
                        
                        expDateFormat = "{year}-{month}-{day}"
                        expDate = expDateFormat.format(day="01",month=form.cleaned_data['month'],year=form.cleaned_data['year'])
                        creditCard = CreditCard(nameOnCard=form.cleaned_data['nameOnCard'],cardNumber=form.cleaned_data['cardNumber'],expiryDate=expDate)
                        creditCard.save()
                        user.creditCard=creditCard
                    # Else simply update the card in the database.
                    else:
                        user.creditCard.nameOnCard=form.cleaned_data['nameOnCard']
                        user.creditCard.cardNumber=form.cleaned_data['cardNumber']
                        expDateFormat = "{year}-{month}-{day}"
                        expDate = expDateFormat.format(day="01",month=form.cleaned_data['month'],year=form.cleaned_data['year'])
                        print("EXP DATE" + expDate)
                        user.creditCard.expiryDate=expDate
                        user.creditCard.save()
                    user.save() # Updates user in database
                    return HttpResponseRedirect("/selfModifyAccount")
                else:
                    print("Form Invalid")
                    messages.error(request, 'Form Invalid')
                    return HttpResponseRedirect("/selfModifyAccount")
            else:                
                return generateUserAccountPage(request,user)
        else:
            return render(request, 'login.html')
    else:
        return render(request, 'login.html')
    
def cancelTicketLoggedIn(request,ticket_id=False):
    ticket = Ticket.objects.get(id=ticket_id)
    if(request.user.is_anonymous == False): # Ensures the user is not anonymous.
        if(request.user.is_clubRep == True or request.user.is_Student == True): # Ensures the accounts manager is logged in.
            if (request.method == 'POST'):# If the request method is post (User is going to submit something)
                print("is post")
                form = CancellationsLoggedInForm(request.POST)
                print(form.errors)
                if(form.is_valid()): # if the form is valid.
                    newCancel = Cancelations(ticketId=ticket.ticketId,firstName=request.user.firstName,lastName=request.user.lastName,userMakingRequest=request.user.userName,requestReason=form.cleaned_data['requestReason'])
                    newCancel.save()
                    ticket.cancelInProgress = "yes"
                    ticket.save()
                    return generateUserAccountPage(request,request.user)
                else:
                    messages.error(request, 'Form Error')
                    return render(request,'cancellationLoggedIn.html',{'ticket_id':ticket_id})
            else:
                return render(request,'cancellationLoggedIn.html',{'ticket_id':ticket_id,'ticketName':ticket.ticketId})
        else:
            return HttpResponseRedirect("/login")
    else:
        return HttpResponseRedirect("/login")




# This function handles modifying a user.
def modifyUserPost(request,user_id=False,club_id=False): 
    if(request.user.is_anonymous == False): # Ensures the user is not anonymous
        if(request.user.is_AccountsManager == True):# Ensures the user is logged in as an accounts manager
            if(request.method == "POST"):# If the request method is post (User is going to submit something)
                print("is post")
                if(request.POST['action']=='submit'):# If the form is submited.
                    form = ModifyStudentClubRepForm(request.POST)
                    print(form.errors)
                    if(form.is_valid()):# If the form is valid
                        user = User.objects.get(id=user_id) # Get the user to be modified.
                        # Clean data from form and update the user in database.
                        user.firstName= form.cleaned_data['firstName']
                        user.lastName=form.cleaned_data['lastName']
                        user.credit=form.cleaned_data['credit']
                        user.discountRate=form.cleaned_data['discountRate']
                        # Format birthday
                        birthDateFormat = "{year}-{month}-{day}"
                        birthDate = birthDateFormat.format(day=form.cleaned_data['birthDay'],month=form.cleaned_data['birthMonth'],year=form.cleaned_data['birthYear'])
                        user.birthDate = birthDate # Update birthday

                        # Set user type to the one provided in the submited form
                        if(form.cleaned_data['userType'] == "clubrep"):
                            user.is_clubRep = True
                            user.is_Student = False
                        elif(form.cleaned_data['userType'] == "student"):
                            user.is_Student = True
                            user.is_clubRep = False

                        # (Code bellow) Handles updating users card if the user has made changes to it.

                        # If user has made no changes to credit card, do nothing
                        if (form.cleaned_data['nameOnCard'] == "" or form.cleaned_data['cardNumber'] == "" or form.cleaned_data['month'] == "" or form.cleaned_data['year'] == ""):
                            print("no Card Added")
                        # If user has made updates to card, and there is no card assigned to the user, create new card.
                        elif(user.creditCard is None and form.cleaned_data['nameOnCard'] != "" and form.cleaned_data['cardNumber'] != "" and form.cleaned_data['month'] != "" and form.cleaned_data['year'] != ""):
                            
                            expDateFormat = "{year}-{month}-{day}"
                            expDate = expDateFormat.format(day="01",month=form.cleaned_data['month'],year=form.cleaned_data['year'])
                            creditCard = CreditCard(nameOnCard=form.cleaned_data['nameOnCard'],cardNumber=form.cleaned_data['cardNumber'],expiryDate=expDate)
                            creditCard.save()
                            user.creditCard=creditCard

                        # Else simply update the card in the database.
                        else:
                            user.creditCard.nameOnCard=form.cleaned_data['nameOnCard']
                            user.creditCard.cardNumber=form.cleaned_data['cardNumber']
                            expDateFormat = "{year}-{month}-{day}"
                            expDate = expDateFormat.format(day="01",month=form.cleaned_data['month'],year=form.cleaned_data['year'])
                            user.creditCard.expiryDate=expDate
                            user.creditCard.save()
                        user.save() # Updates user in database
                        
                        # (Code bellow) is used to return the user to the club they were modifying before
                        # they clicked the user to modify
                        club = Club.objects.get(id=club_id)
                        users = User.objects.all()
                        clubReps = []
                        students = []
                        
                        for user in users:
                            if(user.is_clubRep == True):
                                if(club.name == user.club.name):
                                    clubReps.append(user)
                            if(user.is_Student == True):
                                if(club.name == user.club.name): 
                                    students.append(user)
                        return render(request,'ModifyClub.html',{
                            'clubId':club_id,
                            'userId':user_id,
                            'clubName':club.name,
                            'buildingName':club.buildingName,
                            'street':club.street,
                            'city':club.city,
                            'state':club.state,
                            'postCode':club.postCode,
                            'contactNumber':club.contactNumber,
                            'clubReps':clubReps,
                            'students':students
                        })
                    else:
                        print("Form not valid")

                elif(request.POST['action']=='delete'): # if the user deletes a user then:
                    # Deletes the user from the data base.
                    user = User.objects.get(id=user_id)
                    user.delete()
                    club = Club.objects.get(id=club_id)
                    users = User.objects.all()
                    clubReps = []
                    students = []
                    
                    # (Code bellow) is used to return the user to the club they were modifying before
                    # they clicked the user to modify
                    for user in users:
                        if(user.is_clubRep == True):
                            if(club.name == user.club.name):
                                clubReps.append(user)
                        if(user.is_Student == True):
                            if(club.name == user.club.name): 
                                students.append(user)

                    return render(request,'ModifyClub.html',{
                        'clubId':club_id,
                        'userId':user_id,
                        'clubName':club.name,
                        'buildingName':club.buildingName,
                        'street':club.street,
                        'city':club.city,
                        'state':club.state,
                        'postCode':club.postCode,
                        'contactNumber':club.contactNumber,
                        'clubReps':clubReps,
                        'students':students
                    })  
            else:
                # if the user has not submited a form or deleted a club then:
                # (Code bellow) pulls user from database and displays in the form to allow user to modify it.
                user = User.objects.get(id=user_id)
                userType = ""
                if(user.is_clubRep == True):
                    userType = "clubrep"
                elif(user.is_Student == True):
                    userType = "student"
                
                
                month = ""
                year = ""
                nameOnCard = ""
                cardNumber= ""

                if user.creditCard is None:
                    print("noCard")
                else:
                    nameOnCard = user.creditCard.nameOnCard
                    cardNumber = user.creditCard.cardNumber
                    expDate = user.creditCard.expiryDate
                    month = expDate.month
                    year = expDate.year

                return render(request,'modifyStudentClubRepForm.html',{
                  'clubId':club_id,
                  'userId':user_id,
                  'firstName':user.firstName,
                  'lastName':user.lastName,
                  'birthDay':user.birthDate.day,
                  'birthMonth':user.birthDate.month,
                  'birthYear':user.birthDate.year,
                  'userType':userType,
                  'credit':user.credit,
                  'discountRate':user.discountRate,
                  'nameOnCard':nameOnCard,
                  'cardNumber':cardNumber,
                  'month':month,
                  'year':year,
                })
        else:
            return render(request, 'login.html')
    else:
        return render(request, 'login.html')

# Created By Kuay Tang Zheng, Edit by Benjamin Ell-Jones -> Added security preventing non-cinemaManager access
# Function handles the films page.
def films(request):
    if(request.user.is_anonymous == False):# Ensures the user is not anonymous
        if(request.user.is_CinemaManager == True): # Ensures the user is logged in as a cinema manager
            films = Film.objects.all() # Gets all films
            # Code bellow displays all film on films.html page.
            context={
                'films':films
            }
            return render(request,'films.html',context)
        else:
            return render(request, 'login.html')
    else:
        return render(request, 'login.html')

# Created By Kuay Tang Zheng
# Function used to obtain film details.
def filmDetails(request,film_id=False,showing=1):
    numToDay = list(calendar.day_name)
    numToMonth = list(calendar.month_name)
    film = Film.objects.get(id=film_id)
    showTime = ShowTime.objects.filter(filmId=film_id)
    showDateTime = {}
    dicDateTime = {}
    days = []
    years = []
    showTimeId = []
    for item in showTime.iterator():
        if(showing):
            currentDate = date.today()
        else:
            currentDate = item.showDate
        while(item.endDate != currentDate):
            if str(currentDate.day)+"-"+str(numToMonth[currentDate.month]) in showDateTime:
                temp_dict = {}
                temp_dict[item.screenId.id] = str(item.screeningTime)[0:5]
                showDateTime[str(currentDate.day)+"-"+str(numToMonth[currentDate.month])].append(temp_dict)
            else:
                days.append(numToDay[currentDate.weekday()])
                years.append(currentDate.year)
                showDateTime[str(currentDate.day)+"-"+str(numToMonth[currentDate.month])] = [] 
                temp_dict = {}
                temp_dict[item.screenId.id] = str(item.screeningTime)[0:5]
                showDateTime[str(currentDate.day)+"-"+str(numToMonth[currentDate.month])].append(temp_dict)
            currentDate += timedelta(days=1)
    zippedShowtime = zip(showDateTime,days,years)
    context={
        'film':film,
        'showTime':showDateTime,
        'days':days,
        'years':years,
        'zippedShowTime':zippedShowtime
    }
    return render(request,'filmDetails.html',context)

# Created By Kuay Tang Zheng, Edit by Benjamin Ell-Jones -> Added security preventing non-cinemaManager access
# Function handles adding films to database.
def addFilmPost(request,film_id=False):
    if(request.user.is_anonymous == False):# Ensures the user is not anonymous
        if(request.user.is_CinemaManager == True):# Ensures the user is logged in as a cinema manager
            if(request.method == "POST"):# If the request method is post (User is going to submit something)
                print("is post")
                form = AddFilmForm(request.POST)
                print(form.errors)
                if(form.is_valid()): # If the form is valid then:
                    # format the duration of the film
                    duration = "{hour}:{minute}:{second}"
                    time_object = datetime.datetime.strptime(duration.format(hour = form.cleaned_data['inputHour'],minute=form.cleaned_data['inputMinute'],second=form.cleaned_data['inputSecond']), '%H:%M:%S').time()
                    inputDuration = duration.format(hour=form.cleaned_data['inputHour'],minute=form.cleaned_data['inputMinute'],second=form.cleaned_data['inputSecond'])
                    print(request.FILES.get('inputImg',False))
                    # Pull details of film from form and clean them.
                    title = form.cleaned_data['inputTitle']
                    ageRating = form.cleaned_data['inputAgeRating']
                    desc = form.cleaned_data['inputAgeRating']
                    duration=time_object
                    # Create film
                    if request.FILES.get('inputImg',False):
                        image = request.FILES['inputImg']
                        obj = Film.objects.create(title=title,ageRating=ageRating,duration=time_object,desc=desc,image=image)
                    else:
                        obj = Film.objects.create(title=title,ageRating=ageRating,duration=time_object,desc=desc,image=None)
                    # film = Film(title=form.cleaned_data['inputTitle'],ageRating=form.cleaned_data['inputAgeRating'],duration=time_object,desc=form.cleaned_data['inputDesc'],image=form.cleaned_data.get('inputImg')).save()
                    print(obj)
                    print("form Valid")
                    return HttpResponseRedirect("/films")
                else:
                    print("form not valid")
                    return HttpResponseRedirect("/films")
            else:
                print("form not valid")
        else:
            form = AddFilmForm()
            return render(request,'addFilm.html')
    else:
        return render(request, 'login.html')
    return render(request, 'addFilm.html')

# Created By Kuay Tang Zheng
# Function used to take user to home page.
def newHome(request): 
    startDate = date(2022, 4, 30).isoformat()
    endDate = date(2022, 5, 30).isoformat()
    tier1_film = Film.objects
    if Film.objects.filter(teirOneAdvert=True).exists():
        tier1_film = Film.objects.get(teirOneAdvert=True)
    else:
        tier1_film = False
    films = Film.objects.all() # gets all films 
    startdate = date.today() # gets todays date
    print(startdate)
    endDate = date.today() + timedelta(days=1) # gets end date
    # Gets show times of films to display
    currentShowTimes = ShowTime.objects.filter(showDate__lte=startdate,endDate__gte=endDate)
    needTodelete = ShowTime.objects.filter(endDate__lte=startDate) #need to delete
    needTodelete.all().delete()
    futureShowTimes =  ShowTime.objects.filter(showDate__gte=endDate)
    user = request.user.is_anonymous
    print(user)
    context={
        'films':films,
        'currentShowTimes' : currentShowTimes,
        'futureShowTimes' : futureShowTimes,
        'userIsAnonymous' : user,
        'tierOneFilm': tier1_film
    }
    return render(request, 'newHome.html',context)

# Created By Kuay Tang Zheng
# Function handles screen management page.
def screenManagement(request): 
    screens = Screen.objects.all()
    context={
        'screens':screens
    }
    return render(request,'screenManagement.html',context)

# Created By Kuay Tang Zheng
# Function handles modifying screens and adding show times.
def modifyScreenPost(request,screen_id=False):
    if(request.user.is_anonymous == False and request.user.is_CinemaManager == True): # Ensures user is anonymous and is a cinema manager
        if(request.method == "POST"):# If the request method is post (User is going to submit something)
            print("is post")
            if(request.POST['action']=='delete'): # If screen is deleted by user
                print('is delete')
                # delete screen
                screen = Screen.objects.get(id=screen_id)
                screen.delete()
                return HttpResponseRedirect("/screenManagement")
            elif(request.POST['action']=='submit'):# If screen is submited by user
                form = AddScreenForm(request.POST)
                screen = Screen.objects.get(id=screen_id) # get screen to modify
                print(form.errors)
                if(form.is_valid()):# if form is valid modify and save changes to screen to database.
                    screen.roomNo = form.cleaned_data['inputRoomNo']
                    screen.capacity = form.cleaned_data['inputCapacity']
                    screen.save()
                    print("form Valid")
                    return HttpResponseRedirect("/screenManagement")
                else:
                    print("form not valid")
                    return HttpResponseRedirect("/screenManagement")
            elif(request.POST['action']=='Add ShowTime'): # If user adds show time, add show time to database using data from form
                form = AddShowTimeForm(request.POST)
                startDate = form['inputStartDate'].value()
                # startDate = date(2022, 3, 30).isoformat()
                endDate = form['inputEndDate'].value()
                startTime = form['inputShowTime'].value() + ":00"
                film = Film.objects.get(id=form['inputFilm'].value())
                temp_startTime = startTime
                
                # calculate the endtime of the film
                startTime = datetime.datetime.strptime(startTime, '%H:%M:%S')
                startTime_hms = datetime.time(startTime.hour,startTime.minute,startTime.second)
                split_duration = film.duration.split(':')
                endTime = datetime.datetime(100,1,1,startTime.hour,startTime.minute,startTime.second)
                endTime = endTime+datetime.timedelta(hours=int(split_duration[0]))
                endTime = endTime+datetime.timedelta(minutes=int(split_duration[1]))
                endTime = endTime+datetime.timedelta(seconds=int(split_duration[2]))
                startTime = temp_startTime
                endTime_hms = datetime.time(endTime.hour,endTime.minute,endTime.second)
                endTime = endTime.strftime('%H:%M:%S')

                # GET THE SHOWTIME BETWEEN THE START DATE AND END DATE OF THE CURRENT SHOWTIME
                getAllScreenTime = ShowTime.objects.filter(screenId=screen_id).filter(endDate__gte=startDate,endDate__lte=endDate)

                # ITERATE THROUGH ALL THE SHOW TIME TO CHECK FOR TIME COLLSION
                for item in getAllScreenTime.iterator():
                    currentTime = item.screeningTime
                    currentTime = datetime.datetime(100,1,1,item.screeningTime.hour,item.screeningTime.minute,item.screeningTime.second)
                    split_duration = item.filmId.duration.split(':')
                    currentTime = currentTime+datetime.timedelta(hours=int(split_duration[0]))
                    currentTime = currentTime+datetime.timedelta(minutes=int(split_duration[1]))
                    currentTime = currentTime+datetime.timedelta(seconds=int(split_duration[2]))
                    film_startTime = datetime.time(item.screeningTime.hour,item.screeningTime.minute,item.screeningTime.second)
                    film_endTime = datetime.time(currentTime.hour,currentTime.minute,currentTime.second)

                    # CHECK IF THE SHOW START TIME COLLIDE WITH CURRENT SHOWTIME OBJECT
                    if(time_in_range(film_startTime,film_endTime,startTime_hms)):
                        messages.error(request, 'Time collision with other film')
                        print("TIME COLLISIONED")
                        return HttpResponseRedirect("/screenManagement/modify-screen/"+str(screen_id)+'/') 
                    
                    # CHECK IF THE SHOW END TIME COLLIDE WITH CURRENT SHOWTIME OBJECT
                    if(time_in_range(film_startTime,film_endTime,endTime_hms)):
                        print("TIME COLLISIONED")
                        messages.error(request, 'Time collision with other film')
                        return HttpResponseRedirect("/screenManagement/modify-screen/"+str(screen_id)+'/') 
                
                # SHOW TIME CAN BE CREATED
                screen = Screen.objects.get(id=screen_id)
                film = Film.objects.get(id=form['inputFilm'].value())
                print(form.errors)
                if(form.is_valid()):
                    startDate = form['inputStartDate'].value()
                    endDate = form['inputEndDate'].value()
                    ShowTime(filmId=film,showDate=form.cleaned_data['inputStartDate'],endDate=form.cleaned_data['inputEndDate'],screenId=screen,screeningTime=form.cleaned_data['inputShowTime'],price=form.cleaned_data['inputPrice']).save()
                    sTime = ShowTime.objects.last()
                    startDate = datetime.datetime.strptime(startDate, '%Y-%m-%d')
                    endDate = datetime.datetime.strptime(endDate, '%Y-%m-%d')
                    while startDate != endDate:
                        ShowTimeChild(showTime=sTime,date=startDate,TicketLeft=screen.capacity).save()
                        startDate += timedelta(days=1)
                        print("CALLED")
                    
                    return HttpResponseRedirect("/screenManagement/modify-screen/" + str(screen_id) + "/")
                return HttpResponseRedirect("/screenManagement/modify-screen/" + str(screen_id) + "/")
        else:
            # Show addScreen.html to user.
            films = Film.objects.all()
            form = AddScreenForm()
            screen = Screen.objects.filter(id=screen_id)
            showTimes = ShowTime.objects.filter(screenId=screen_id)
            return render(request,'addScreen.html',{
                'screen':screen[0],
                'films' : films,
                'showTimes' : showTimes
            })
    else:
        return render(request, 'login.html')    


def time_in_range(start,end,current):
    return start <= current <= end


# Created By Kuay Tang Zheng
# Function used to add screens to database.
def addScreenPost(request):
    if(request.user.is_anonymous == False): # Ensures user is not anonymous.
        if(request.user.is_CinemaManager == True): # Ensures user is logged in as a cinema manager
            if(request.method == "POST"):# If the request method is post (User is going to submit something)
                print("is post")
                form = AddScreenForm(request.POST)
                print(form.errors)
                if(form.is_valid()):# if form is valid add screen to database, using cleaned data from form.
                    Screen(roomNo=form.cleaned_data['inputRoomNo'],capacity=form.cleaned_data['inputCapacity']).save()
                    print("form Valid")
                    return HttpResponseRedirect("/screenManagement")
                else:
                    print("form not valid")
                    return HttpResponseRedirect("/screenManagement")
            else:
                form = AddFilmForm()
                return render(request,'addScreen.html')
        else:
            return render(request, 'login.html')
    else:
        return render(request, 'login.html')

 # Created By Kuay Tang Zheng
 # Benjamin Ell-Jones Added Advertisement Functionality
 #Function is used to modify film
def modifyFilmPost(request,film_id=False):
    if(request.user.is_anonymous == False):# Ensures user is not anonymous.
        if(request.user.is_CinemaManager == True):# Ensures user is logged in as a cinema manager
            if(request.method == "POST"):# If the request method is post (User is going to submit something)
                print("is post")
                if(request.POST['action']=='delete'):# If user wishes to deleted the film, delete film from database.
                    print("is delete")
                    film = Film.objects.get(id=film_id)
                    film.delete()
                    return HttpResponseRedirect("/films")
                elif(request.POST['action']=='submit'):# If user submits modified film data then:
                    form = AddFilmForm(request.POST)
                    print(form.errors)
                    if(form.is_valid()): # if the form is valid
                        # Format duration of film
                        duration = "{hour}:{minute}:{second}"
                        inputDuration = duration.format(hour=form.cleaned_data['inputHour'],minute=form.cleaned_data['inputMinute'],second=form.cleaned_data['inputSecond'])
                       
                        film = Film.objects.get(id=film_id) # Get film to modify.
                        # get modified image from form to update in database.
                        print(request.FILES.get('inputImg',False))
                        if request.FILES.get('inputImg',False):
                            film.image = request.FILES['inputImg']
                            print(film.image)

                        # Modify general info about film    
                        film.title = form.cleaned_data['inputTitle']
                        film.ageRating=form.cleaned_data['inputAgeRating']
                        advertisementTier = form.cleaned_data['advertisementTier']

                        #=======Advertisement code added by Benjamin Ell-Jones========
                        #(Code bellow) Ensures that there are not to many films that are being advertised at a given tier.
                        tier1Count = 0
                        tier2Count = 0

                        for filmCheck in Film.objects.all():
                            if(filmCheck.teirOneAdvert == True):
                                tier1Count = tier1Count + 1
                            if(filmCheck.teirTwoAdvert == True):
                                tier2Count = tier2Count + 1

                        
                        #set the max ammount of films in each tier here
                        maxTierOne = 1 # Maximum ammount of tier 1 films
                        maxTierTwo = 7 # Maximum ammount of tier 2 films

                        currentTier = ""

                        # Code checks what advertisement a film currently is.
                        if(film.teirOneAdvert == True):
                            currentTier = "tier1"
                        elif(film.teirTwoAdvert == True):
                            currentTier = "tier2"
                        else:
                            currentTier = "notA"

                        # If the user wants to set a new advertisement tier then:
                        if(currentTier != advertisementTier):
                            # Checks what advertisement tier the user wants to set the film as and if there are enough slots left for that given tier.
                            # If there are too many films in the advertisement tier then:
                            if(advertisementTier == "tier1" and tier1Count + 1 > maxTierOne or advertisementTier == "tier2" and tier2Count + 1 > maxTierTwo):
                                # Alert the user there are too many films in that advertisement tier.
                                split_duration = film.duration.split(':')
                                messages.error(request, 'Error Too Many Films In Tier')
                                return render(request,'addFilm.html',{
                                'film':film,
                                'advertisementTier':currentTier, 
                                'hour'  : split_duration[0],
                                'minute' : split_duration[1],
                                'second' : split_duration[2]
                                })
                            else:  
                                # If there are enough spaces in the advertisement tier then update film to new tier.  
                                if(advertisementTier == "notA"):
                                    film.teirOneAdvert = False
                                    film.teirTwoAdvert = False
                                elif(advertisementTier == "tier1"):
                                    film.teirOneAdvert = True
                                    film.teirTwoAdvert = False
                                elif(advertisementTier == "tier2"):
                                    film.teirOneAdvert = False
                                    film.teirTwoAdvert = True
                        #=============================================================
                        # Save film modified film to database.
                        film.duration=inputDuration
                        film.desc=form.cleaned_data['inputDesc']
                        film.save()
                        print("form Valid")
                        return HttpResponseRedirect("/films")
                    else:
                        print("form not valid")
                else:
                    print("form not valid")
            else:

                # (Code bellow) takes user to the addfilm page to modify their selected film.
                form = AddFilmForm()
                film = Film.objects.filter(id=film_id)

                if(film[0].teirOneAdvert == True):
                    advertisementTier = "tier1"
                elif(film[0].teirTwoAdvert == True):
                    advertisementTier = "tier2"
                else:
                    advertisementTier = "notA"
                split_duration = film[0].duration.split(':')
                return render(request,'addFilm.html',{
                  'film':film[0],
                  'advertisementTier':advertisementTier, 
                  'hour'  : split_duration[0],
                  'minute' : split_duration[1],
                  'second' : split_duration[2]
                })
        else:
            return render(request, 'login.html')
    else:
        return render(request, 'login.html')
        
# Created by Kuay Tang Zheng
def cinemaManagerHome(request): 
    if(request.user.is_anonymous == True):
        return render(request, 'login.html')
    if (request.user.is_CinemaManager == True):
        return render(request, 'cinemaManagerHome.html')
    else:
        return render(request, 'login.html')    

# Created by Kuay Tang Zheng
def addShowTimePost(request):
    return render(request,'addShowTime')

# Created by Kuay Tang Zheng
def buyTicket(request,film_id,screen_date,screen_month,showTime,screenId,year):
    # Make a datatime object with the give arguments
    ymd = '{year}-{month}-{screen_date}'.format(year=year,month=screen_month,screen_date=screen_date)

    # Get the showtime film object
    film = Film.objects.get(id=film_id)

    # get the specific Showtime child object
    showDate = datetime.datetime.strptime(ymd, '%Y-%B-%d')
    sTime = ShowTime.objects.get(filmId=film_id,showDate__lte=showDate,endDate__gte=showDate,screeningTime=showTime+":00")

    # TO LET THE HTML PAGE KNOW WHERE THE USER IS LOGIN OR NOT
    if(request.user.is_anonymous == True):
        return render(request,'buyTicketPage.html',{
            'film' : film,
            'date' : screen_date+screen_month,
            'user' : False,
            'showTime' : sTime,
            'showDate': ymd
        })
    else:
        return render(request,'buyTicketPage.html',{
            'film' : film,
            'date' : screen_date+screen_month,
            'user' : request.user,
            'showTime' : sTime,
            'showDate': ymd
        })


def checkOut(request,showTime_id):
    if request.method == "POST":
        form = checkOutForm(request.POST)
        showTime = ShowTime.objects.get(id=showTime_id)
        print(form.errors)
        if(form.is_valid):
            sDate = form.cleaned_data['inputShowDate']
            showDate = datetime.datetime.strptime(sDate, '%Y-%B-%d')
            # USE SHOW
            stChild = ShowTimeChild.objects.get(date=showDate,showTime=showTime)
            ticket_dict = {}
            ticket_dict["Guest"] = []
            ticketList = []
            ticketQty = form.cleaned_data["inputGuestQty"]
            ticketStudentQty = form.cleaned_data["inputStudentQty"]
            film = showTime.filmId.title
            price=showTime.price
            totalPrice = form.cleaned_data["inputTotalPrice"]
            showingRoom=showTime.screenId.roomNo
            showingDate = stChild.date
            startTime = showTime.screeningTime
            if request.user.is_anonymous:
                # Check the if the showtime can fulfil the quantity of the tickets
                if(int(ticketQty) > stChild.TicketLeft):
                    messages.error(request,'Not Enough Space')
                    messages.error(request,'Total Space Left : ' + str(stChild.TicketLeft))
                    next = request.POST.get('next',"/")
                    return HttpResponseRedirect(next)
                else:
                    # deduct the number of ticket left from the database ShowTimeChild object
                    stChild.TicketLeft -= int(ticketQty) + 2
                    stChild.save()

                firstName = form.cleaned_data["inputFirstName"]
                lastName = form.cleaned_data["inputLastName"]
                email = form.cleaned_data['inputEmail']
                phone = form.cleaned_data['inputPhone']

                # Generate the ticket objects 
                for i in range(int(ticketQty)):
                    generateTicketId = "T" + createUniqueNum(15)
                    checkObject = list(Ticket.objects.filter(ticketId=generateTicketId))
                    while checkObject:
                        checkObject = list(Ticket.objects.filter(ticketId=generateTicketId))
                    ticketId=generateTicketId
                    currenTicket = Ticket.objects.create(ticketId=ticketId,ticketType="Guest",purchaseDate=date.today(),film=film,price=price,showingRoom=showingRoom,showingDate=showingDate,startTime=startTime,firstName=firstName,lastName=lastName,email=email,phone=phone)
                    ticket_dict['Guest'].append(currenTicket.ticketId)
                    ticketList.append(currenTicket.ticketId)

                context={
                    "ticketList":ticketList,
                    "ticekt_dict": ticket_dict,
                    "ShowTimeChild":stChild
                }
                return render(request,'printTicketPage.html',context)
                # return HttpResponseRedirect("/printTicketsPage")
                
            elif request.user.is_Student or request.user.is_clubRep:

                if request.user.credit > float(totalPrice):
                    ticket_dict["Student"] = []
                    firstName = request.user.firstName
                    lastName = request.user.lastName
                    userName = request.user.userName
                    #GENERATIONG GUEST TICKET TYPES
                    totalQty = int(ticketQty) + int(ticketStudentQty)

                    # CHECK IF THE SHOW TIME CAPACITY IS ENOUGH FOR THE AMOUNT OF TICKET USER WANT TO BUY
                    if(int(totalQty) > stChild.TicketLeft):
                        messages.error(request,'Not Enough Space')
                        messages.error(request,'Total Space Left : ' + str(stChild.TicketLeft))
                        next = request.POST.get('next',"/")
                        return HttpResponseRedirect(next)
                    else:
                        # deduct the number of ticket left from the database ShowTimeChild object and user credits
                        stChild.TicketLeft -= int(totalQty) + 2
                        request.user.credit -= float(totalPrice)
                        stChild.save()
                        request.user.save()

                    # Generate number of Guest Type tickets
                    for i in range(int(ticketQty)):
                        generateTicketId = "T" + createUniqueNum(15)
                        checkObject = list(Ticket.objects.filter(ticketId=generateTicketId))
                        while checkObject:
                            checkObject = list(Ticket.objects.filter(ticketId=generateTicketId))
                            generateTicketId = "T" + createUniqueNum(15)
                        ticketId=generateTicketId
                        currenTicket = Ticket.objects.create(ticketId=ticketId,ticketType="Guest",purchaseDate=date.today(),film=film,price=price,showingRoom=showingRoom,showingDate=showingDate,startTime=startTime,firstName=firstName,lastName=lastName,userName=userName)
                        ticket_dict['Guest'].append(currenTicket.ticketId)
                        ticketList.append(currenTicket.ticketId)

                    # Generate number of Student Type tickets
                    for i in range(int(ticketStudentQty)):
                        price = price * 1 - (request.user.discountRate/100)
                        generateTicketId = "T" + createUniqueNum(15)
                        checkObject = list(Ticket.objects.filter(ticketId=generateTicketId))
                        while checkObject:
                            checkObject = list(Ticket.objects.filter(ticketId=generateTicketId))
                            generateTicketId = "T" + createUniqueNum(15)
                        ticketId=generateTicketId
                        currenTicket = Ticket.objects.create(ticketId=ticketId,ticketType="Student",purchaseDate=date.today(),film=film,price=price,showingRoom=showingRoom,showingDate=showingDate,startTime=startTime,firstName=firstName,lastName=lastName,userName=userName)
                        ticket_dict['Student'].append(currenTicket.ticketId)
                        ticketList.append(currenTicket.ticketId)     
                                   
                    context={
                        "ticketList":ticketList,
                        "ticekt_dict":ticket_dict,
                        "ShowTimeChild":stChild
                    }
                    return render(request,'printTicketPage.html',context)
                else:
                    messages.error(request,'Not Enough Credits')
                    messages.error(request,'Please enter you payment details here or in the account manage page')
                    next = request.POST.get('next',"/")
                    return HttpResponseRedirect(next)
            elif request.user.is_CinemaManager:
                request.user.credit = 1000
                if request.user.credit > float(price):
                    ticket_dict["Student"] = []
                    firstName = request.user.firstName
                    lastName = request.user.lastName
                    userName = request.user.userName
                    #GENERATIONG GUEST TICKET TYPES
                    totalQty = int(ticketQty) + int(ticketStudentQty)

                    # Check the if the showtime can fulfil the quantity of the tickets
                    if(int(totalQty) > stChild.TicketLeft):
                        messages.error(request,'Not Enough Space')
                        messages.error(request,'Total Space Left : ' + str(stChild.TicketLeft))
                        next = request.POST.get('next',"/")
                        return HttpResponseRedirect(next)
                    else:
                        # de
                        stChild.TicketLeft -= int(totalQty)
                        stChild.save()
                    for i in range(int(ticketQty)):
                        generateTicketId = "T" + createUniqueNum(15)
                        checkObject = list(Ticket.objects.filter(ticketId=generateTicketId))
                        while checkObject:
                            print("LOPPING")
                            checkObject = list(Ticket.objects.filter(ticketId=generateTicketId))
                            generateTicketId = "T" + createUniqueNum(15)
                        ticketId=generateTicketId
                        currenTicket = Ticket.objects.create(ticketId=ticketId,ticketType="Guest",purchaseDate=date.today(),film=film,price=price,showingRoom=showingRoom,showingDate=showingDate,startTime=startTime,firstName=firstName,lastName=lastName)
                        ticket_dict['Guest'].append(currenTicket.ticketId)
                        ticketList.append(currenTicket.ticketId)
                    #GENERATING STUDENT TICKET TYPES
                    for i in range(int(ticketStudentQty)):
                        price = price * 1 - (request.user.discountRate/100)
                        generateTicketId = "T" + createUniqueNum(15)
                        checkObject = list(Ticket.objects.filter(ticketId=generateTicketId))
                        while checkObject:
                            print("LOPPING")
                            checkObject = list(Ticket.objects.filter(ticketId=generateTicketId))
                            generateTicketId = "T" + createUniqueNum(15)
                        ticketId=generateTicketId
                        currenTicket = Ticket.objects.create(ticketId=ticketId,ticketType="Student",purchaseDate=date.today(),film=film,price=price,showingRoom=showingRoom,showingDate=showingDate,startTime=startTime,firstName=firstName,lastName=lastName)
                        ticket_dict['Student'].append(currenTicket.ticketId)
                        ticketList.append(currenTicket.ticketId)     
                                   
                    context={
                        "ticketList":ticketList,
                        "ticekt_dict":ticket_dict,
                        "ShowTimeChild":stChild
                    }
                    return render(request,'printTicketPage.html',context)
                else:
                    messages.error(request,'Not Enough Credits')
                    messages.error(request,'Please enter you payment details here or in the account manage page')
                    next = request.POST.get('next',"/")
                    return HttpResponseRedirect(next)
            else:
                print("Error in checkout view")



