from email.policy import default
from django import forms
from .models import Film

class AddClubForm(forms.Form):
    club_name = forms.CharField(label='club_name',max_length=100)
    inputStreetNo = forms.CharField(label='inputStreetNo',max_length=100)
    inputStreet = forms.CharField(label='inputStreet',max_length=100)
    inputCity = forms.CharField(label='inputCity',max_length=100)
    inputState = forms.CharField(label='inputState',max_length=100)
    inputPostcode = forms.CharField(label='inputPostcode',max_length=100)
    inputNum = forms.CharField(label='inputNum',max_length=100)
    
    inputFirstName = forms.CharField(label='inputNum',max_length=200)
    inputLastName = forms.CharField(label='inputNum',max_length=200)
    birthDay = forms.IntegerField(label='birthDay')
    birthMonth = forms.IntegerField(label='birthMonth')
    birthYear = forms.IntegerField(label='birthYear')
    inputPassword = forms.CharField(label='inputNum',max_length=200)

class ModifyClubForm(forms.Form):
    club_name = forms.CharField(label='club_name',max_length=100)
    inputStreetNo = forms.CharField(label='inputStreetNo',max_length=100)
    inputStreet = forms.CharField(label='inputStreet',max_length=100)
    inputCity = forms.CharField(label='inputCity',max_length=100)
    inputState = forms.CharField(label='inputState',max_length=100)
    inputPostcode = forms.CharField(label='inputPostcode',max_length=100)
    inputNum = forms.CharField(label='inputNum',max_length=100)

class AddStudentClubRepForm(forms.Form):
    firstName = forms.CharField(label='firstName',max_length=100)
    lastName = forms.CharField(label='lastName',max_length=100)
    birthDay = forms.IntegerField(label='birthDay')
    birthMonth = forms.IntegerField(label='birthMonth')
    birthYear = forms.IntegerField(label='birthYear')
    userType = forms.CharField(label='userType',max_length=100)
    password = forms.CharField(label='password',max_length=100)

    discountRate = forms.IntegerField(label='discountRate',required=False)
    credit= forms.IntegerField(label='credit',required=False)
    nameOnCard = forms.CharField(label='nameOnCard',max_length=100)
    cardNumber = forms.CharField(label='cardNumber',max_length=16)
    month = forms.CharField(label='month',min_length=1,max_length=2)
    year = forms.CharField(label='year',min_length=4,max_length=4)

class ModifyStudentClubRepForm(forms.Form):
    firstName = forms.CharField(label='firstName',max_length=100)
    lastName = forms.CharField(label='lastName',max_length=100)
    birthDay = forms.IntegerField(label='birthDay')
    birthMonth = forms.IntegerField(label='birthMonth')
    birthYear = forms.IntegerField(label='birthYear')
    userType = forms.CharField(label='userType',max_length=100)
    
    discountRate = forms.IntegerField(label='discountRate',required=False)
    credit= forms.IntegerField(label='credit',required=False)
    nameOnCard = forms.CharField(label='nameOnCard',max_length=100,required=False)
    cardNumber = forms.CharField(label='cardNumber',max_length=16,required=False)
    month = forms.CharField(label='month',min_length=1,max_length=2,required=False)
    year = forms.CharField(label='year',min_length=4,max_length=4,required=False)

class selfModifyUserForm(forms.Form):
    firstName = forms.CharField(label='firstName',max_length=100)
    lastName = forms.CharField(label='lastName',max_length=100)
    
    birthDay = forms.IntegerField(label='birthDay')
    birthMonth = forms.IntegerField(label='birthMonth')
    birthYear = forms.IntegerField(label='birthYear')

    password = forms.CharField(label='password',required=False)

    nameOnCard = forms.CharField(label='nameOnCard',max_length=100,required=False)
    cardNumber = forms.CharField(label='cardNumber',max_length=16,required=False)
    month = forms.CharField(label='month',min_length=1,max_length=2,required=False)
    year = forms.CharField(label='year',min_length=4,max_length=4,required=False)

class LoginForm(forms.Form):
    userName = forms.CharField(label='userName',max_length=200)
    password = forms.CharField(label='password',max_length=200)

class DiscountRequestForm(forms.Form):
    discount = forms.CharField(label='discount',max_length=100)
    

class AddFilmForm(forms.Form):
    inputImage = forms.ImageField(label='inputImg', required=False)
    inputTitle = forms.CharField(label='inputTitle',max_length=100)
    inputAgeRating = forms.CharField(label='inputAgeRating',max_length=50)
    inputHour = forms.CharField(label='inputHour',max_length=25)
    inputMinute = forms.CharField(label='inputMinute',max_length=25)
    inputSecond = forms.CharField(label='inputSecond',max_length=25)
    inputDesc = forms.CharField(label="inputDesc",max_length=200)
    advertisementTier = forms.CharField(label="advertisementTier",max_length=200,required=False)

class AddShowTimeForm(forms.Form): 
    inputFilm = forms.IntegerField(label='inputFilm',required=True)
    inputStartDate = forms.DateField(label='inputStartDate',required=True)
    inputEndDate = forms.DateField(label='inputEndDate',required=True)
    inputShowTime = forms.TimeField(label='inputShowTime',required=True)
    inputPrice = forms.FloatField(label="inputPrice",required=True)

class CancellationForm(forms.Form):
    ticketId = forms.CharField(label='ticketId',max_length=100)
    requestReason = forms.CharField(label='requestReason',max_length=100)

    firstName= forms.CharField(label='firstName',max_length=200)
    lastName= forms.CharField(label='lastName',max_length=200)

class CancellationsLoggedInForm(forms.Form):
    requestReason = forms.CharField(label='requestReason',max_length=400)

class BuyCreditForm(forms.Form):
    creditAmmount = forms.IntegerField(label='creditAmmount',required=True)

class ViewDailyTransactionsForm(forms.Form):
    dayMonthYear = forms.DateField(label='dayMonthYear',required=True)

class MonthReportForm(forms.Form):
    month = forms.CharField(label='month',required=True)
    year1 = forms.CharField(label='year1',required=True)

class YearlyReportForm(forms.Form):
    year2 = forms.CharField(label='year2',required=True)

class StudentJoinRequestForm(forms.Form):
    firstName= forms.CharField(label='firstName',max_length=200)
    lastName= forms.CharField(label='lastName',max_length=200)
    birthDay = forms.IntegerField(label='birthDay')
    birthMonth = forms.IntegerField(label='birthMonth')
    birthYear = forms.IntegerField(label='birthYear')
    club = forms.CharField(label='club',max_length=200)
    password = forms.CharField(label='password',max_length=200)
    userType = forms.CharField(label='userType',max_length=200)

class AddScreenForm(forms.Form):
    inputRoomNo = forms.CharField(label='inputRoomNo')
    inputCapacity = forms.IntegerField(label='inputCapacity')

class checkOutForm(forms.Form):
    inputStudentQty = forms.IntegerField(label='inputStudentQty',required=False)
    inputGuestQty = forms.IntegerField(label='inputGuestQty',required=False)
    inputFirstName = forms.CharField(label='inputFirstName',required=False)
    inputLastName = forms.CharField(label='inputLastName',required=False)
    inputTotalPrice = forms.FloatField(label='inputTotalPrice',required=False)
    inputEmail = forms.CharField(label='inputEmail',required=False)
    inputPhone = forms.CharField(label='inputPhone',required=False)
    inputShowDate = forms.CharField(label='inputShowDate',required=False)
