from flask import Flask,request,render_template,redirect,url_for,flash,session
from otp import genotp
from cmail import sendmail
from stoken import encode,decode
from flask_session import Session
import mysql.connector
app=Flask(__name__)
app.secret_key='codegnan@2018'
app.config['SESSION_TYPE']='filesystem'
Session(app)
mydb=mysql.connector.connect(host='localhost',user='root',password='admin',db='snmproject')

@app.route('/')
def home():
    return render_template('welcome.html')

@app.route('/create',methods=['GET','POST'])
def create():
    if request.method=='POST':
        print(request.form)
        username=request.form['user_name']
        uemail=request.form['email']
        password=request.form['password']
        conformpassword=request.form['confirm_password']
        cursor=mydb.cursor()
        cursor.execute("select count(useremail) from users where useremail=%s",[uemail])
        result=cursor.fetchone() 
        print(result)
        if result[0]==0:
            gotp=genotp()
            print(gotp)
            udata={'username':username,'uemail':uemail,'password':password,'otp':gotp}
            subject="OTP for Simple Notes Manager"
            body=f"otp for registration of Simple notes manger {gotp}"
            sendmail(to=uemail,subject=subject,body=body)
            flash('OTP has send to your mail')
            return redirect(url_for('otp',enudata=encode(data=udata)))  
        elif result[0]>0:
            flash('Email already existed')
            return redirect(url_for('login')) 
        else:
            return 'something is wrong'
    return render_template('create.html')

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method=='POST':
        uemail=request.form['email']
        password=request.form['password']
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select count(useremail) from users where useremail=%s',[uemail])
        c=cursor.fetchone()
        if c[0]==0:
            flash("Your details not Exist please register first")
            return redirect(url_for('create'))
        else:
            cursor.execute('select password from users where useremail=%s',[uemail])
            bpassword=cursor.fetchone() 
            # print("password:",password)
            # print("result password:",bpassword[0].decode('utf-8'))
            # print(type(password),type(bpassword[0].decode('utf-8')))
            if bpassword[0].decode('utf-8') == password:
                print(session)
                session['user']=uemail
                print("After:",session)
                return redirect(url_for("dashboard"))
            else:
                return "Incorrect Credientails"
    return render_template('login.html')

@app.route('/otp/<enudata>',methods=['POST','GET'])
def otp(enudata):
    if request.method=='POST':
        otpr=request.form.get("otp")
        try:
            dudata=decode(data=enudata)   #{'userid':userid,'username':username,'uemail':uemail,'password':password,'otp':gotp}
        except Exception as e:
            print(e)
            return "Something is wrong"
        else:
            if otpr==dudata['otp']:
                cursor=mydb.cursor()
                cursor.execute("insert into users(username,useremail,password) values(%s,%s,%s)",[dudata['username'],dudata['uemail'],dudata['password']])
                mydb.commit()
                cursor.close()
                return redirect(url_for('login'))
            else:
                return "Invalid OTP"   
    return render_template('otp.html')

@app.route("/dashboard",methods=['POST','GET'])
def dashboard():
    return render_template('dashboard.html')
@app.route("/addnotes",methods=['POST','GET'])
def addnotes():
    if request.method=="POST":
        title=request.form["title"]
        desc=request.form["desc"]
        cursor=mydb.cursor(buffered=True)
        cursor.execute("select user_id from users where useremail=%s",[session.get('user')])
        id=cursor.fetchone()
        if id:
            try:
                cursor.execute('insert into notes(title,n_description,user_id) values(%s,%s,%s)',[title,desc,id[0]])
                mydb.commit()
                cursor.close()
            except mysql.connector.errors.IntegrityError:
                flash("Duplicate Title Entry")
                return redirect(url_for('dashboard'))
            else:
                flash("Notes add successfully")
                return redirect(url_for('dashboard'))
        else:
            return "Something went wrong"
    return render_template("addnotes.html")
@app.route('/viewallnotes',methods=['POST',"GET"])
# def viewallnotes():
#     try:
#         cursor=mydb.cursor(buffered=True)
#         cursor.execute("select user_id from users where useremail=%s",[session.get('user')])
#         uid=cursor.fetchone()
#         cursor.execute('select n_id,title,create_at from notes where user_id=%s',[uid[0]])
#         result=cursor.fetchall()
#         print(result)
#     except Exception as e:
#         print(e)
#         return redirect(url_for("dashboard"))
#     else:
#         return render_template("viewallnotes.html",result=result)
# @app.route('/viewnotes/<uid>')
# def viewnotes(uid):
#     try:
#         cursor=mydb.cursor(buffered=True)
#         cursor.execute("select * from notes where n_id=%s",[uid])
#         notes=cursor.fetchone()
#     except Exception as e:
#         print(e)
#         return redirect(url_for("viewallnotes"))
#     else:
#         return render_template("viewnotes.html",notes=notes)
# @app.route("/updatenotes/<uid>",methods=["POST","GET"])
# def updatenotes(uid):
#     cursor=mydb.cursor(buffered=True)
#     cursor.execute("select * from notes where n_id=%s",[uid])
#     notes=cursor.fetchone()
#     if request.method=="POST":
#         try:
#             title=request.form["title"]
#             desc=request.form["desc"]
#             cursor=mydb.cursor(buffered=True)
#             cursor.execute('update notes set title=%s,n_description=%s where n_id=%s',[title,desc,uid])
#             mydb.commit()
#             cursor.close()
#         except Exception as e:
#             print(e)
#         else:
#             flash("Notes updates successfully")
#             return redirect(url_for('dashboard'))
#     return render_template("updatenotes.html",notes=notes)
# @app.route("/deletenotes/<uid>",methods=["POST","GET"])
# def deletenotes(uid):
#     try:
#         cursor=mydb.cursor(buffered=True)
#         cursor.execute("delete from notes where n_id=%s",[uid])
#         mydb.commit()
#         cursor.close()
#     except Exception as e:
#         print(e)
#     else:
#         flash("Deleted successfully")
#         return redirect(url_for("viewallnotes"))
# @app.route('/search',methods=['GET','POST'])
# def search():
#     if session.get('user'):
#         try:
#             if request.method=='POST':
#                 sdata=request.form['sname'] #''python',s22
#                 strg=['A-Za-z0-9']
#                 pattern=re.compile(f'^{strg}',re.IGNORECASE)
#                 if (pattern.match(sdata)):
#                     cursor=mydb.cursor(buffered=True)
#                     cursor.execute('select * from notes where nid like %s or title like %s or ndescription like %s or create_at like %s',[sdata+'%',sdata+'%',sdata+'%',sdata+'%'])
#                     sdata=cursor.fetchall()
#                     cursor.close()
#                     return render_template('dashboard.html',sdata=sdata)
#                 else:
#                     flash('no data found')
#                     return redirect(url_for('dashboard'))
#             else:
#                 return redirect(url_for('dashboard'))
#         except Exception as e:
#             print(e)
#             flash('Cantfind anything')
#             return redirect(url_for('login'))
#     else:
#         return redirect(url_for('login'))
app.run(use_realoader=True)
