from random import randint

from django.core.files.storage import FileSystemStorage
from django.http import *
from django.shortcuts import *
from pymysql import *
from django.views.decorators.csrf import *
from datetime import *
from database import *
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import smtplib
from email.message import EmailMessage

conn=Connect("127.0.0.1",'root','','showbox+')

def start(request):
    return render(request,"start.html")



def login(request):
    if "admin" in request.session:
        return redirect(manageMovies)
    elif "user" in request.session:
        return redirect(userHome)
    else:
        a={"msg":''}
        return render(request,"login.html",{"ar":a,"mr":a})

@csrf_exempt
def signin(request):
    email=request.POST["textbox1"]
    password=request.POST["textbox2"]
    s="select * from admin"

    result=Fetchall(s)
    x=False
    y=False
    for row in result:
        if email==row[0] and password==row[3]:
            type=row[5]
            x=True
            break
    if x==True:
           request.session["admin"]=email
           if type=="Blocked":
                d = {"msg2": "You acount has been blocked. Contact us for more information."}
                a = {"msg": ''}
                return render(request, "login.html", {"ar": a, "mr": d})
           return redirect(manageMovies)
    else:
        q="select * from clientregistration"
        result=Fetchall(q)
        for row1 in result:
            if email==row1[0] and password==row1[2]:
                type=row1[3]
                y=True
                break
        if y==True:
            request.session["user"]=email
            if type=="unsubscribed":

                return HttpResponseRedirect("subPage")
            elif type=="Blocked":
                d = {"msg2": "Your account has been blocked. Contact us for more information."}
                a = {"msg": ''}
                return render(request, "login.html", {"ar": a, "mr": d})
            else:
                z=f"select * from subscription where email='{email}'"
                w=Fetchone(z)
                today=date.today()
                givenenddate=w[3]
                enddate = givenenddate+ timedelta(days=0)
                if (today<=enddate):
                    return HttpResponseRedirect("userHome")
                else:
                    z=f"update clientregistration set type='unsubscribed' where email='{email}'"
                    w=Update(z)
                    return HttpResponseRedirect("subPage")

        else:
            d = {"msg2": "Invalid Credentials"}
            a = {"msg": ''}
            return render(request, "login.html", {"ar": a, "mr": d})


def signup(request):
    a={"msg":''}
    return render(request,"signup.html",{"ar":a})

@csrf_exempt
def addUser(request):
    email=request.POST["email"]
    name=request.POST["name"]
    mobile=request.POST["mobile"]
    type="unsubscribed"
    password=request.POST["password"]
    otp='0'

    s="select * from clientregistration"
    result=Fetchall(s)
    x=True

    for row in result:
        if email==row[0]:
            x=False
            break

    if x==True:
        q=f"insert into clientregistration values ('{email}','{name}','{password}','{type}','{mobile}','{otp}')"
        d=Insert(q)
        a={"msg":"Account Created"}
        esub="Welcome to ShowBox"
        emailmsg="Hi "+name+",\nThanks for signing up to ShowBox. You can purchase our subscription starting at Rs 179 to enjoy the latest blockbuster Movies and Web-Series. \n\nRegards, \nShowBox"
        sendEmail(email,emailmsg,esub)
        return render(request,"login.html",{"ar":a})
    else:
        a={"msg":"Email already registered"}
        return render(request,"signup.html",{"ar":a})


def sendEmail(rec,emsg,esub):
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()

    try:
         # Authentication
        s.login("projectshowbox@gmail.com", "Mankirat98")

        # message to be sent
        msg = EmailMessage()

        msg.set_content(emsg)

        msg['Subject'] = esub
        msg['From'] = "projectshowbox@gmail.com"
        msg['To'] = rec
        # sending the mail
        s.send_message(msg)

        # terminating the session
        s.quit()
    except Exception as e:
        print(e)






def forgotPassword(request):
    d={"msg":''}
    return render(request,"forgotPassword.html",{"ar":d})

@csrf_exempt
def generateOtp(request):
    email=request.POST["email"]
    mobile=request.POST["mobile"]
    x = False
    s=f"select * from admin where email='{email}' and mobile='{mobile}'"
    result=Fetchone(s)
    if result==None:
        s = f"select * from clientregistration where email='{email}' and mobile='{mobile}'"
        result=Fetchone(s)
        print("first if")
        if (result!=None):

            x=True
            table="clientregistration"

    else:
        x=True
        table="admin"



    if x==True:
        otp=randint(1000,9999)
        d=Update("update "+table+" set otp='"+str(otp)+"' where email='"+email+"'")
        emailsubject="Forgot Password"
        emailmsg = "Hi " + result[1] + ",\nThe One-Time-Password (OTP) for your account is "+str(otp)+". Use it to re-set your password.\n\nRegards, \nShowBox"
        sendEmail(email, emailmsg,emailsubject)
        return HttpResponseRedirect("enterOtp?email="+email+"&mobile="+mobile)
    else:
        d={"msg":"Wrong email and phone combinaton"}
        return render(request,"forgotPassword.html",{"ar":d})

def enterOtp(request):


    email=request.GET["email"]
    mobile=request.GET["mobile"]
    d={"email":email,"mobile":mobile}
    m={"msg":''}
    return render(request,"enterOtp.html",{"ar":d,"mr":m})

@csrf_exempt
def newPassword(request):
    email=request.POST["email"]
    mobile=request.POST["mobile"]
    otp=request.POST["otp"]

    s=f"select * from admin where email='{email}' and mobile='{mobile}' and otp='{otp}'"
    result=Fetchone(s)
    x=False
    if result==None:
        s = f"select * from clientregistration where email='{email}' and mobile='{mobile}' and otp='{otp}'"
        result=Fetchone(s)
        if result!=None:
            x=True
            table="clientregistration"
    else:
        x=True
        table="admin"
    d = {"email": email, "mobile": mobile}

    if x==True:

        return render(request,"newPassword.html",{"ar":d,"table":table})
    else:
        m={"msg":"Invalid OTP"}
        return render(request,"enterOtp.html",{"ar":d,"mr":m})

@csrf_exempt
def resetPassword(request):
    email=request.POST["email"]
    password=request.POST["newpassword"]
    table=request.POST["table"]


    d=Update("update "+table+" set otp='0', password='"+password+"' where email='"+email+"'")
    a={"msg":"Password Updated"}
    m={"msg2":''}
    return render(request,"login.html",{"ar":a,"mr":m})






def manageMovies(request):
    if "admin" in request.session:
        s="select * from movies"
        result=Fetchall(s)
        x=[]
        for row in result:
            d={"mid":row[0],"mname":row[1],"genre":row[3],"cast":row[4],"image":row[6],"rating":row[8],"date":row[9],"catname":row[10]}
            x.append(d)
        return render(request,"manageMovies.html",{"ar":x})
    else:
        return redirect(login)


def insertMovie(request):
    if "admin" in request.session:
        s="select * from genre"
        result=Fetchall(s)
        x=[]
        for row in result:
            d={"genre":row[0]}
            x.append(d)
        q="select * from category"
        result=Fetchall(q)
        y=[]
        for row in result:
            d={"catname":row[0]}
            y.append(d)

        return render(request,"insertMovie.html",{"gr":x,"cr":y})
    else:
        return redirect(login)

@csrf_exempt
def addMovie(request):
    if "admin" in request.session:
        mname=request.POST["textbox1"]
        genre = request.POST["textbox2"]
        cast = request.POST["textbox3"]
        director = request.POST["textbox4"]
        link = request.POST["textbox5"]
        rating = request.POST["textbox6"]
        desc=request.POST["textbox7"]

        catname=request.POST["catname"]

        image = request.FILES["image"]
        bgimage=request.FILES["bgimage"]
        imagename=datetime.now().strftime("%Y%m%d%H%M%S")+image.name
        bgimagename = datetime.now().strftime("%Y%m%d%H%M%S") + bgimage.name


        s=f"insert into movies values ('{NULL}','{mname}','{desc}','{genre}','{cast}','{director}','{imagename}','{link}','{rating}','{bgimagename}','{catname}')"
        d=Insert(s)
        fs = FileSystemStorage()
        fs.save(imagename, image)
        fs.save(bgimagename, bgimage)
        return HttpResponseRedirect("manageMovies")
    else:
        return redirect(login)

def editMovie(request):
    if "admin" in request.session:
        vid=request.GET["q"]
        s=f"select * from movies where vid='{vid}'"
        result=Fetchone(s)
        dd = {"vid":result[0], "title": result[1], "desc":result[2],"genre": result[3], "cast": result[4],"director":result[5], "image": result[6],"path":result[7], "rating": result[8],
             "bgimage": result[9], "catname": result[10]}
        a = "select * from genre"
        result = Fetchall(a)
        x = []
        for row in result:
            d = {"genre": row[0]}
            x.append(d)
        q = "select * from category"
        result = Fetchall(q)
        y = []
        for row in result:
            d = {"catname": row[0]}
            y.append(d)

        return render(request,"editMovie.html",{"ar":dd,"gr":x,"cr":y})
    else:
        return redirect(login)

def edittedMovie(request):
    if "admin" in request.session:
        vid=request.POST["vid"]
        title = request.POST["textbox1"]
        genre = request.POST["textbox2"]
        cast = request.POST["textbox3"]
        director = request.POST["textbox4"]
        link = request.POST["textbox5"]
        rating = request.POST["textbox6"]
        desc = request.POST["textbox7"]

        catname = request.POST["catname"]



        oldimage=request.POST["oldimage"]
        oldbg=request.POST["oldbg"]
        status=request.POST["status"]
        print(status+"checking")
        fs = FileSystemStorage()

        imagename=oldimage
        bgimagename=oldbg
        if status=="image":
            image = request.FILES["image"]

            imagename = datetime.now().strftime("%Y%m%d%H%M%S") + image.name
            fs.save(imagename, image)
        elif status=="bgimage":
            bgimage = request.FILES["bgimage"]

            bgimagename = datetime.now().strftime("%Y%m%d%H%M%S") + bgimage.name
            fs.save(bgimagename, bgimage)
        elif status=="both":
            bgimage = request.FILES["bgimage"]
            image = request.FILES["image"]
            imagename = datetime.now().strftime("%Y%m%d%H%M%S") + image.name
            fs.save(imagename, image)
            bgimagename = datetime.now().strftime("%Y%m%d%H%M%S") + bgimage.name
            fs.save(bgimagename, bgimage)





        s=f"update movies set title='{title}',description='{desc}',genre='{genre}',cast='{cast}',director='{director}',image='{imagename}',link='{link}',rating='{rating}',bgimage='{bgimagename}',catname='{catname}' where vid='{vid}'"
        d = Update(s)



        return HttpResponseRedirect("manageMovies")
    else:
        return redirect(login)

def deleteVideo(request):
    if "admin" in request.session:
        vid=request.GET["q"]
        s=f"delete from movies where vid='{vid}'"
        d=Delete(s)
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect(login)


def manageEpisodes(request):
    if "admin" in request.session:
        vid=request.GET["q"]
        s=f"select * from movies where vid='{vid}'"
        result=Fetchone(s)
        d={"vid":vid,"title":result[1]}
        q=f"select * from episodes where vid='{vid}'"
        result2=Fetchall(q)
        x=[]
        for row in result2:
            a={"eid":row[0],"epinumber":row[2],"epititle":row[3],"description":row[4],"photo":row[6]}
            x.append(a)

        return render(request,"manageEpisodes.html",{"vr":d,"zr":x})
    else:
        return redirect(login)

@csrf_exempt
def addEpisode(request):
    if "admin" in request.session:
        vid=request.POST["vid"]

        s=f"select * from movies where vid='{vid}'"
        result=Fetchone(s)
        d={"vid":result[0],"title":result[1]}

        return render(request,"addEpisode.html",{"vr":d})
    else:
        return redirect(login)

def editEpisode(request):
    if "admin" in request.session:
        vid=request.GET["q"]
        s=f"select * from movies where vid='{vid}'"
        result=Fetchone(s)
        d={"vid":result[0],"title":result[1]}
        d1={}

        epinumber=request.GET["e"]
        s1=f"select * from episodes where vid='{vid}' and epinumber='{epinumber}'"
        result1=Fetchone(s1)
        d1={"eid":result1[0],"epinumber":result1[2],"epititle":result1[3],"description":result1[4],"link":result1[5],"photo":result1[6]}

        return render(request,"editEpisode.html",{"vr":d,"er":d1})
    else:
        return redirect(login)


@csrf_exempt
def insertEpisode(request):
    if "admin" in request.session:
        vid=request.POST["vid"]
        epino=request.POST["epino"]
        epititle=request.POST["epititle"]
        epidesc=request.POST["epidesc"]
        epipath=request.POST["epipath"]

        epiphoto=request.FILES["epiphoto"]
        epiphotoname = datetime.now().strftime("%Y%m%d%H%M%S") + epiphoto.name


        s=f"select * from episodes where vid='{vid}'"
        result=Fetchall(s)
        x=True
        for row in result:
            if str(row[2])==epino:
                x=False
                break
        if x==True:
            q=f"insert into episodes values ('{NULL}','{vid}','{epino}','{epititle}','{epidesc}','{epipath}','{epiphotoname}')"
            cr=conn.cursor()
            cr.execute(q)
            conn.commit()
            a="Episode Added"
            fs = FileSystemStorage()
            fs.save(epiphotoname, epiphoto)
        else:
            a="Episode number already exists"
        return HttpResponseRedirect("manageEpisodes?q="+vid)
    else:
        return redirect(login)

def editedEpisode(request):
    if "admin" in request.session:
        vid = request.POST["vid"]
        epino = request.POST["epino"]
        epititle = request.POST["epititle"]
        epidesc = request.POST["epidesc"]
        epipath = request.POST["epipath"]
        status=request.POST["status1"]

        s=f"select * from episodes where vid='{vid}' and epinumber='{epino}'"
        result=Fetchone(s)
        if status=="true":
            epiphoto = request.FILES["epiphoto"]
            epiphotoname = datetime.now().strftime("%Y%m%d%H%M%S") + epiphoto.name
            fs = FileSystemStorage()
            fs.save(epiphotoname, epiphoto)
        else:
            epiphotoname=result[6]


        q = f"update episodes set title='{epititle}',description='{epidesc}',videopath='{epipath}',photo='{epiphotoname}' where vid='{vid}' and epinumber='{epino}'"
        cr = conn.cursor()
        cr.execute(q)
        conn.commit()

        return HttpResponseRedirect("manageEpisodes?q=" + vid)
    else:
        return redirect(login)

def deleteEpisode(request):
    if "admin" in request.session:
        eid=request.GET["q"]
        vid=request.GET["vid"]
        s=f"delete from episodes where eid='{eid}'"
        d=Delete(s)
        return HttpResponseRedirect("manageEpisodes?q=" + vid)
    else:
        return redirect(login)


def insertGenre(request):
    if "admin" in request.session:
        d={"msg":''}
        return render(request,"insertGenre.html",{"ar":d})
    else:
        return redirect(login)

def addGenre(request):
    if "admin" in request.session:
        s="select * from genre"
        genre=request.GET["textbox1"]
        desc=request.GET["textbox2"]

        cr=conn.cursor()
        cr.execute(s)
        result=cr.fetchall()
        x=True
        for row in result:
            if row[0]==genre:
                x=False
                break
        if x==True:
            d={"msg":"Genre Added Successfully"}
            cr.execute("insert into genre values ('"+genre+"','"+desc+"')")
            conn.commit()
        else:
            d={"msg":"Genre Already exists"}

        return render(request,"insertGenre.html",{"ar":d})
    else:
        return redirect(login)

def viewGenre(request):
    if "admin" in request.session:
        s="select * from genre"
        cr=conn.cursor()
        cr.execute(s)

        result=cr.fetchall()
        x=[]
        for row in result:
            d={"genre":row[0],"desc":row[1]}
            x.append(d)

        return render(request,"viewGenre.html",{"ar":x})
    else:
        return redirect(login)

def editGenre(request):
    if "admin" in request.session:
        a=request.GET["q"]
        s="select * from genre where gname='"+a+"'"
        cr=conn.cursor()
        cr.execute(s)
        result=cr.fetchone()
        d={"genre":result[0],"desc":result[1]}


        return render(request,"editGenre.html",{"dr":d})
    else:
        return redirect(login)

@csrf_exempt
def genreEditted(request):
    if "admin" in request.session:
        genre=request.POST["genre"]
        desc=request.POST["desc"]

        s="update genre set description='"+desc+"' where gname='"+genre+"'"

        cr=conn.cursor()
        cr.execute(s)
        conn.commit()
        return HttpResponseRedirect("viewGenre")
    else:
        return redirect(login)

def deleteGenre(request):
    if "admin" in request.session:
        genre=request.GET["q"]
        s="delete from genre where gname='"+genre+"'"
        cr = conn.cursor()
        cr.execute(s)
        conn.commit()
        return HttpResponseRedirect("viewGenre")
    else:
        return redirect(login)

def plans(request):
    if "admin" in request.session:
        s="select * from plan"
        result=Fetchall(s)
        x=[]
        for row in result:
            d={"id":row[0],"timeperiod":row[1],"price":row[2]}
            x.append(d)
        return render(request,"plans.html",{"ar":x})
    else:
        return redirect(login)

@csrf_exempt
def editplan(request):
    if "admin" in request.session:
        pid=request.POST["pid"]
        price=request.POST["price"]
        s=f"update plan set price='{price}' where id='{pid}'"
        d=Update(s)

        return redirect(plans)
    else:
        return redirect(login)

def subscriptions(request):
    if "admin" in request.session:
        s="select * from subscription"
        result=Fetchall(s)
        x=[]
        for row in result:
            d={"subid":row[0],"email":row[1],"start":row[2],"end":row[3]}
            x.append(d)
        q="select count(email),type from clientregistration"
        w="select count(type) from clientregistration where type='subscribed'"
        result2=Fetchone(w)
        result1=Fetchone(q)
        a={"count":result1[0],"active":result2[0]}



        return render(request,"subscriptions.html",{"ar":x,"cr":a})
    else:
        return redirect(login)

def showUserInvoice(request):
    if "admin" in request.session:
        subid=request.GET["q"]
        bill1 = f"select * from bill where subid='{subid}'"
        result=Fetchall(bill1)
        x=[]
        for row in result:
            d={"bid":row[0],"email":row[1],"subid":row[2],"amount":row[3],"cardno":row[4],"cardexp":row[5],"date":row[7]}
            x.append(d)
        sub=f"select * from clientregistration where email='{row[1]}'"
        result1=Fetchone(sub)
        a={"email":result1[0],"name":result1[1],"type":result1[3],"mobile":result1[4]}
        return render(request,"showUserInvoice.html",{"br":x,"ar":a})
    else:
        return redirect(login)

def invoiceDetails(request):
    if "admin" in request.session:
        bill1 = f"select * from bill"
        result = Fetchall(bill1)
        x = []
        for row in result:
            d = {"bid": row[0], "email": row[1], "subid": row[2], "amount": row[3], "cardno": row[4], "cardexp": row[5],
                 "date": row[6]}
            x.append(d)
        q = "select count(email),type from clientregistration"
        w = "select count(type) from clientregistration where type='subscribed'"
        result2 = Fetchone(w)
        result1 = Fetchone(q)
        a = {"count": result1[0], "active": result2[0]}
        return render(request,"invoiceDetails.html",{"br":x,"cr":a})
    else:
        return redirect(login)

def adminsDeatils(request):
    if "admin" in request.session:
        admin=request.session["admin"]
        s = f"select * from admin  "
        result = Fetchall(s)
        x=[]
        for row in result:
            if row[0]==admin:
                    a={"email": row[0], "name": row[1], "mobile": row[2], "type": row[5]}
            else:
                 d = {"email": row[0], "name": row[1], "mobile": row[2], "type": row[5]}
                 x.append(d)
        return render(request,"adminsDetails.html",{"ar":x,"self":a})
    else:
        return redirect(login)


@csrf_exempt
def addAdmin(request):
    if "admin" in request.session:
        admin=request.session["admin"]
        adst=f"select * from admin where email='{admin}'"
        adres=Fetchone(adst)
        if adres[5]=="SuperAdmin":
            email=request.POST["email"]
            name=request.POST["name"]
            mobile=request.POST["mobile"]
            password=request.POST["password"]
            type=request.POST["type"]
            otp='0'

            s="select * from admin"
            result=Fetchall(s)
            x=True
            for row in result:
                if row[0]==email or row[2]==mobile:
                    x=False
                    a="Email/Mobile already registered"
                    break
            if x==True:
                q=f"insert into admin values ('{email}','{name}','{mobile}','{password}','{otp}','{type}')   "
                d=Insert(q)
                if(d=="success"):
                    a="New Admin added"
                else:
                    a=d
        else:
            a="You cannot add new admins"


        return HttpResponse(a)
    else:
        return redirect(login)

def adminAccount(request):
    if "admin" in request.session:
        admin=request.session["admin"]
        s=f"select * from admin where email='{admin}' "
        result=Fetchone(s)
        d={"email":result[0],"name":result[1],"mobile":result[2],"password":result[3],"type":result[5]}

        return render(request,"adminAccount.html",{"ar":d})
    else:
        return redirect(login)



@csrf_exempt
def changeAdminPassword(request):
    if "admin" in request.session:
        email=request.session["admin"]
        oldpassword=request.GET["old"]
        newpassword=request.GET["new"]
        cnf=request.GET["cnf"]
        if cnf!=newpassword:
            x="New password and confirm new password do not match"
        else:
            s="select * from admin"
            result=Fetchall(s)
            x=False
            for row in result:
                if email==row[0] and oldpassword==row[3]:
                    x=True
                    break
            if x==True:
                q=f"update admin set password='{newpassword}' where email='{email}'"
                d=Update(q)
                if (d == "success"):
                    x= "Password Changed"
                else:
                    x =  d
            else:
                x="Invalid Old password"

        return HttpResponse(x)
    else:
        return redirect(login)

def editAdminDetails(request):
    if "admin" in request.session:
        admin=request.session["admin"]
        name=request.GET["name"]
        mobile=request.GET["mobile"]
        s=f"select * from admin where not email='{admin}'"
        result=Fetchall(s)
        x=True
        for row in result:
            if (row[2]==mobile):
                x=False
                a="Mobile number already registered"
                break
        if x==True:
            s1=f"update admin set name='{name}', mobile='{mobile}' where email='{admin}'"
            cr=conn.cursor()
            cr.execute(s1)
            conn.commit()

            print(admin,name,mobile)
            a="Details Updated"

        return HttpResponse(a)
    else:
        return redirect(login)

def changeStatus(request):
    if "admin" in request.session:
        admin=request.session["admin"]
        adst=f"select * from admin where email='{admin}'"
        adres=Fetchone(adst)
        if adres[5]=="SuperAdmin":
            status=request.GET["q"]
            email=request.GET["z"]
            if status=="Block":
                s=f"update admin set type='Blocked' where email='{email}'"
            elif status=="Unblock":
                s = f"update admin set type='Admin' where email='{email}'"

            d=Update(s)
            return redirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect(login)

def changeUserStatus(request):
    if "admin" in request.session:
        status = request.GET["q"]
        email = request.GET["z"]
        if status == "Block":
            s = f"update clientregistration set type='Blocked' where email='{email}'"
        elif status == "Unblock":
            z = f"select * from subscription where email='{email}'"
            w = Fetchone(z)
            if (w==None):
                s = f"update clientregistration set type='unsubscribed' where email='{email}'"
                print("if")
            else:
                print("else")
                today = date.today()
                givenenddate = w[3]
                enddate = givenenddate + timedelta(days=0)
                if today <= enddate:
                    s = f"update clientregistration set type='subscribed' where email='{email}'"
                else:
                    s = f"update clientregistration set type='unsubscribed' where email='{email}'"
        cr=conn.cursor()
        cr.execute(s)
        conn.commit()

        return redirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect(login)

def viewUsers(request):
    if "admin" in request.session:
        s="select * from clientregistration"
        result=Fetchall(s)
        x=[]
        for row in result:
            d={"email":row[0],"name":row[1],"mobile":row[4],"type":row[3],"password":row[2]}
            x.append(d)

        return render(request,"viewUsers.html",{"ar":x})
    else:
        return redirect(login)



def userHome(request):
    if "user" in request.session:
        s="select * from movies"
        result=Fetchall(s)
        x=[]
        y=[]
        for row in result:
            d={"vid":row[0],"title":row[1],"image":row[6],"genre":row[3],"path":row[7]}
            x.append(d)
        q="select genre from genre inner join movies on genre.gname=movies.genre group by movies.genre"
        result=Fetchall(q)
        for row in result:
            d={"genre":row[0]}
            y.append(d)
        category={"cat":"All","one":"29","two":"45","three":"51"}
        return render(request,"userHome.html",{"ar":x,"gr":y,"cat":category})
    else:
        return redirect(login)

def userMovies(request):
    if "user" in request.session:
        s="select * from movies where catname='Movies'"
        result = Fetchall(s)
        x = []
        y=[]
        for row in result:
            d = {"vid":row[0],"title":row[1], "image":row[6], "genre":row[3], "path":row[7]}
            x.append(d)
        q = "select genre from genre inner join movies on genre.gname=movies.genre where movies.catname='"+"Movies"+"' group by movies.genre"
        result = Fetchall(q)
        for row in result:
            d = {"genre": row[0]}
            y.append(d)
        category={"cat":"movies","one":"29","two":"51","three":"52"}
        return render(request, "userHome.html", {"ar": x, "gr": y,"cat":category})
    else:
        return redirect(login)


def userShows(request):
    if "user" in request.session:
        s="select * from movies where catname='Web Series'"
        result = Fetchall(s)
        x = []
        y=[]
        for row in result:
            d = {"vid":row[0],"title":row[1], "image":row[6], "genre":row[3], "path":row[7]}
            x.append(d)
        q = "select genre from genre inner join movies on genre.gname=movies.genre where movies.catname='"+"Web Series"+"' group by movies.genre"
        result = Fetchall(q)
        for row in result:
            d = {"genre": row[0]}
            y.append(d)
        category={"cat":"web","one":"53","two":"54","three":"45"}
        return render(request, "userHome.html", {"ar": x, "gr": y,"cat":category})
    else:
        return redirect(login)


def coverPage(request):
    if "user" in request.session:
        vid=request.GET["q"]
        s=f"select * from movies where vid='{vid}'"
        result=Fetchone(s)

        d={"vid": result[0], "title": result[1], "desc": result[2], "genre": result[3], "cast": result[4],
             "director": result[5], "image": result[6], "path": result[7], "rating": result[8],
             "bgimage": result[9], "catname": result[10]}
        x = []
        if result[10]=="Web Series":
            q=f"select * from episodes where vid='{vid}'"
            eresult=Fetchall(q)

            for row in eresult:
                a={"eid":row[0],"eno":row[2],"ename":row[3],"edesc":row[4],"epath":row[5],"ephoto":row[6]}
                x.append(a)
        user=request.session["user"]
        z=f"select * from watchlist where vid='{vid}' and email='{user}'"
        result3=Fetchone(z)
        if result3==None:
            t="0"
        else:
            t="1"

        rev=f"select review.review,review.email,clientregistration.name,review.nature from review inner join clientregistration on review.email=clientregistration.email where vid='{vid}'"
        revresult=Fetchall(rev)
        rr=[]
        userrev=''
        positive=negative=neutral=0
        for revrow in revresult:
            revvar={"review":revrow[0],"name":revrow[2],"nature":revrow[3]}
            rr.append(revvar)
            if revrow[1]==user:
                userrev=revrow[0]
            if revrow[3]==-1:
                negative=negative+1
            elif revrow[3]==0:
                neutral=neutral+1
            elif revrow[3]==1:
                positive=positive+1
        revnature="Neutral"
        if (negative>=neutral and negative>positive):
            revnature="Negative"
        if (positive>negative and positive>=neutral):
            revnature="Positive"
        if (positive==negative==neutral==0):
            revnature="No User Reviews"

        print(neutral,positive,negative)


        return render(request,"coverPage.html",{"ar":d,"er":result[10],"t":t,"ep":x,"rr":rr,"userrev":userrev,"revnature":revnature})
    else:
        return redirect(login)

@csrf_exempt
def addReview(request):
    if "user" in request.session:
        email=request.session["user"]
        vid=request.POST["vid"]
        review=request.POST["review"]
        nature=reviewNature(review)
        print(nature)
        s=f"select * from review where email='{email}' and vid='{vid}'"
        result=Fetchone(s)
        if result==None:
            s1=f"insert into review values ('{NULL}','{email}','{vid}','{review}','{nature}')"
            d=Insert(s1)
        else:
            s1=f"update review set review='{review}', nature='{nature}' where rid='{result[0]}'"
            d=Update(s1)
        return redirect(request.META.get('HTTP_REFERER'))

    else:
        return redirect(login)

def deleteReview(request):
    if "user" in request.session:
        email=request.session["user"]
        vid=request.GET["q"]
        s=f"delete from review where vid='{vid}' and email='{email}'"
        d=Delete(s)
        return redirect(request.META.get('HTTP_REFERER'))

    else:
        return redirect(login)

def playVid(request):
    if "user" in request.session:
        user=request.session["user"]
        s=f"select * from clientregistration where email='{user}'"
        result=Fetchone(s)
        if result[3]=="unsubscribed":
            return HttpResponseRedirect("subPage")
        else:
            d={"path":request.GET["q"]}
            return render(request,"playVid.html",{"ar":d})
    else:
        return redirect(login)

def addToWatchList(request):
    if "user" in request.session:
        user=request.session["user"]
        vid=request.GET["vid"]
        s=f"select * from watchlist where email='{user}'"
        result=Fetchall(s)
        x=True
        for row in result:
            if int(vid)==row[0]:
                x=False
                break
        if x==True:
            q=f"insert into watchlist values ('{vid}','{user}')"
            d=Insert(q)

        return redirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect(login)

def removeFromWatchList(request):
    if "user" in request.session:
        user=request.session["user"]
        vid=request.GET["vid"]
        s=f"delete from watchlist where email='{user}' and vid='{vid}'"
        d=Delete(s)
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect(login)



def watchList(request):
    if "user" in request.session:
        user=request.session["user"]
        s=f"select * from watchlist where email='{user}'"
        result=Fetchall(s)
        x=[]
        flag=1
        for video in result:
            s2=f"select * from movies where vid='{video[0]}'"
            result2=Fetchall(s2)
            for row in result2:
                d = {"vid":row[0],"title":row[1], "image":row[6], "catname":row[10], "path":row[7]}
                x.append(d)
        if x==[]:
            flag=0
        return render(request,"watchList.html",{"ar":x,"ur":user,"flag":flag})
    else:
        return redirect(login)

def videoSearch(request):
    if "user" in request.session:
        search=request.GET["search"]
        search=search.lower()
        s=f"select  * from movies where title like '%"+search+"%'"
        result=Fetchall(s)
        x=[]
        flag=1
        for row in result:
            d = {"vid": row[0], "title": row[1], "image": row[6], "catname": row[10], "path": row[7]}
            x.append(d)
        print(x)
        if x==[]:
            flag=0
        print(flag)
        return render(request,"videoSearch.html",{"ar":x,"flag":flag})
    else:
        return redirect(login)





def changeUserPassword(request):
    if "user" in request.session:
        user = request.session["user"]
        s = f"select * from clientregistration where email='{user}'"
        result = Fetchone(s)
        oldpassword=result[2]
        newpassword=request.GET["new"]
        oldpassworduser=request.GET["old"]
        cnf=request.GET["cnf"]
        if cnf!=newpassword:
            a="New password and confirm new password do not match"
        elif oldpassword==oldpassworduser:
            q=f"update clientregistration set password='{newpassword}' where email='{user}'"
            d=Update(q)
            a="Password Updated"

        else:
            a="Incorrect Password"
            

        return HttpResponse(a)
    else:
        return redirect(login)

def logout(request):
    if "user" in request.session :
        del request.session["user"]
    elif "admin" in request.session:
        del request.session["admin"]
    return redirect(login)

def subPage(request):
    if "user" in request.session:
        user=request.session["user"]
        s="select * from plan"
        x=[]
        result=Fetchall(s)
        for row in result:
            d={"price":row[2],"timeperiod":row[1],"id":row[0]}
            x.append(d)
        return render(request,"subPage.html",{"user":user,"ar":x})
    else:
        return redirect(login)

@csrf_exempt
def payment(request):
    if "user" in request.session:
        user=request.session["user"]
        cardno=request.POST["cardno"]
        expiry=request.POST["expiry"]
        code=request.POST["code"]
        plan=request.POST["plan"]

        p=f"select * from plan where id='{plan}'"
        presult=Fetchone(p)



        startdate=date.today()
        if plan=="1":
            z=30
        elif plan=="2":
            z=90
        else:
            z=365
        enddate = startdate + timedelta(days=z)

        s=f"update clientregistration set type='subscribed' where email='{user}'"
        d=Update(s)

        sub=f"select * from subscription where email='{user}'"
        result1=Fetchone(sub)
        if result1==None:
            q=f"insert into subscription values ('{NULL}','{user}','{startdate}','{enddate}')"
            d=Insert(q)
        else:
            oldenddate=result1[3]
            enddate=oldenddate+timedelta(days=z)

            q=f"update subscription set enddate='{enddate}' where email='{user}'"
            d=Update(q)
        sub=f"select * from subscription where email='{user}'"
        resul2=Fetchone(sub)
        subid=resul2[0]
        print(subid)
        b=f"insert into bill values ('{NULL}','{user}','{subid}','{presult[2]}','{cardno}','{expiry}','{code}','{startdate}')"
        d=Insert(b)

        esub = "Receipt of Subscription"
        emailmsg = "Hello There,\nThanks for purchasing the subscription of ShowBox. You can now enjoy the latest blockbuster Movies and Web-Series anytime anywhere.\nYour subscriptions details are as follows:\nDate purchased : "+str(startdate)+"\nValid Upto : "+str(enddate)+"\nAmount : "+str(presult[2])+" \n\nRegards, \nShowBox"
        sendEmail(user, emailmsg, esub)

        return redirect(userHome)

    else:
        return redirect(login)


def userAccount(request):
    if "user" in request.session:
        user=request.session["user"]
        s=f"select * from clientregistration where email='{user}'"
        result=Fetchone(s)
        d={"email":result[0],"name":result[1],"password":result[2],"type":result[3],"mobile":result[4]}
        return render(request,"userAccount.html",{"ar":d})
    else:
        return redirect(login)

def editUserDetails(request):
    if "user" in request.session:
        user = request.session["user"]
        name = request.GET["name"]
        mobile = request.GET["mobile"]
        s = f"select * from clientregistration where not email='{user}'"
        result = Fetchall(s)
        x = True
        for row in result:
            if (row[4] == mobile):
                x = False
                a = "Mobile number already registered"
                break
        if x == True:
            s1 = f"update clientregistration set name='{name}', mobile='{mobile}' where email='{user}'"
            cr = conn.cursor()
            cr.execute(s1)
            conn.commit()


            a = "Details Updated"

        return HttpResponse(a)
    else:
        return redirect(login)


def reviewNature(review):
    ob = SentimentIntensityAnalyzer()
    result = ob.polarity_scores(review)


    if result['compound'] >= 0.5 :
        return 1
    elif result['compound'] <=-0.5:
        return -1
    else:
        return 0
