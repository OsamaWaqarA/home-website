from flask import Flask, render_template, request, jsonify,redirect,abort

import os, PasswordEngine, datetime, dbms, random, threading, ssl, smtplib, requests

from email.message import EmailMessage

password_ins = PasswordEngine.password()

info = dbms.dbms()

app = Flask(__name__)

def ip_translate(ip,secure):
    if "https" in ip and not secure:
        ip = ip.replace("https","http")
    elif "https" not in ip and secure:
        ip = ip.replace("http","https")
    ip = ip.replace("//","((")
    ip = ip[0:ip.find("/")]
    ip = ip.replace("((","//")
    return ip

def refresh_exip_Api():
    try:
        response = requests.post("http://192.168.1.106/refreshExIP", timeout=5)
        response.raise_for_status()  
        return response.json(),"success"
    except requests.exceptions.RequestException as e:
        return None,"Failed"

def send_email(code,rec):
    password = "" # personal info redacted
    subject = "⚠️ Classified Drop: Your Code's Here"
    body = f"""
    Yo legend,

    Your access code is: {code}

    Keep it locked. No sharing, no screenshots — just vibes.  
    The internet's wild, but you're wilder. Use it like a pro. ⚡

    Catch you on the flip side,  
    M.O.A 😎
    """
    em = EmailMessage()
    em['From'] = "" # personal info redacted
    em['To'] = rec
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login("", password)# personal info redacted
        smtp.send_message(em)

def code_maker(size):
    ran = []
    part = int(size / 3)
    for i in range(0,part):
        ran.append(random.randint(65,90))
        ran.append(random.randint(97,122))
        ran.append(random.randint(48,57))
    if len(ran) < size:
        for i in range(0,(size-len(ran))):
            ran.append(random.randint(48,57))
    code = ""
    random.shuffle(ran)
    for num in ran:
        code += chr(num)
    return code

@app.route("/task")
def schedule():
    tasks = []
    dates = []#2001-05-26T23:00
    color = []
    cip = str(request.remote_addr)
    if os.path.exists(os.getcwd()+"//static//tasks//"+cip+".txt"):
        with open(os.getcwd()+"//static//tasks//"+cip+".txt","r") as file:
            while True:
                line = file.readline().strip()
                if line:
                    hold,hold1,hold2,hold3 = line.split("*")
                    if hold3 == "False":
                        tasks.append(hold)
                        dates.append(hold1)
                        color.append(hold2)
                else:
                    break
    return render_template("schedule.html",tasks=tasks,dates=dates,color=color)

@app.route("/task/adder", methods=['POST','GET'])
def task_adder():
    cip = str(request.remote_addr)
    data = request.get_json()
    name = data.get('name')
    date = data.get('date')
    color = data.get('color')

    with open(os.getcwd()+"//static//tasks//"+cip+".txt","a") as file:
        file.write(name)
        file.write("*")
        file.write(date)
        file.write("*")
        file.write(color)
        file.write("*False")
        file.write("\n")

    return jsonify({'status': 'success'}) 

@app.route("/task/done", methods=['POST','GET'])
def task_done():
    cip = str(request.remote_addr)
    data = request.get_json()
    name = data.get('name')
    date = data.get('date')
    color = data.get('color')

    newline = str(name)+"*"+str(date)+"*"+str(color)+"*True"

    filedata = []

    found = False

    with open(os.getcwd()+"//static//tasks//"+cip+".txt","r") as file:
        while True:
            line = file.readline().strip()
            if line:
                filedata.append(line)
            else:
                break
    for i in range(0,len(filedata)):
        if name in filedata[i] and date in filedata[i] and color in filedata[i] and "False" in filedata[i]:
            filedata[i] = newline
            found = True
            break
    with open(os.getcwd()+"//static//tasks//"+cip+".txt","w") as file:
        for data in filedata:
            file.write(data)
            file.write("\n")
    if found:
        return jsonify({'status': 'success'}) 
    else:
        return jsonify({'status': 'fail'}) 

def allow_password(cip):
    try:
        if os.path.exists(os.getcwd()+"//login_password//"+str(cip)+".txt"):
            with open(os.getcwd()+"//login_password//"+str(cip)+".txt","r") as file:
                user = file.readline().strip()
                line = file.readline().strip()     
            if len(line) <= 0:
                os.remove(os.getcwd()+"//login_password//"+str(cip)+".txt") 
                return False
            info2 = str(datetime.datetime.today() - (datetime.datetime.strptime(line, '%Y-%m-%d %H:%M:%S.%f')))
            h,m,s = info2.split(":")
            m = int(m)
            m += (int(h) * 60)
            m += int(float(s) / 60)
            if m >= 5:
                os.remove(os.getcwd()+"//login_password//"+str(cip)+".txt") 
                return False, None
            else:
                return True, user
        else:
            return False, None
    except Exception:
        return False, None
        
@app.route("/")
def index():
    ip = request.host_url
    ip = ip_translate(ip,False)
    return redirect(ip)


@app.route("/password")
def Password():
    ans,user = allow_password(request.remote_addr)
    if ans:
        return redirect ("select_password")
    else:
        return render_template("password.html")

@app.route("/password_login", methods=['post'])
def password_login():
    detail = []
    detail.append(request.form.get('text', '').strip())
    detail.append(request.form.get('password', '').strip())
    
    if "login" in password_ins.login(detail[0],detail[1]):
        with open(os.getcwd()+"//login_password//"+str(request.remote_addr)+".txt","a")as file:
            file.write(detail[0])
            file.write("\n")
            file.write(str(datetime.datetime.today()))
            return redirect("/select_password")
    else:
        return render_template("password.html",text= detail[0],password= detail[1],message = password_ins.login(detail[0],detail[1]))
@app.route("/password/create account")
def create_password_Account():
    return render_template("create_password_account.html")

@app.route("/password/create account/pos", methods=['post'])
def crearte_password_pos_acc():
    detail = []
    detail.append(request.form.get('text', '').strip())
    detail.append(request.form.get('password', '').strip())
    detail.append(request.form.get('email', '').strip())
    ans = password_ins.create_account(detail[0],detail[1],detail[2])
    if "Done" in ans:
        return redirect("/password")
    else:
        return ans
    
@app.route("/password/public")
def public_select():
    ans , username = allow_password(request.remote_addr)
    if ans:
        stored_password = os.listdir(os.getcwd()+"//passwords//public")
        list_passwords = []
        des_passwords = []
        for i in range(0,len(stored_password)):
            stored_password[i] = password_ins.decodename(stored_password[i])
        for passkey in stored_password:
            temp_pass ,temp_des = password_ins.read_password("public",passkey)
            list_passwords.append(temp_pass)
            des_passwords.append(temp_des)
        return render_template("select_password.html",storage=stored_password,keys=list_passwords,des=des_passwords,typer="Move to private")
    else:
        return redirect("/password")



@app.route("/select_password")
def select_password():
    ans , username = allow_password(request.remote_addr)
    if ans:
        user = password_ins.codename(username)
        stored_password = os.listdir(os.getcwd()+"//passwords//"+username)
        list_passwords = []
        des_passwords = []
        stored_password.remove(user)
        for i in range(0,len(stored_password)):
            stored_password[i] = password_ins.decodename(stored_password[i])
        for passkey in stored_password:
            temp_pass ,temp_des = password_ins.read_password(username,passkey)
            list_passwords.append(temp_pass)
            des_passwords.append(temp_des)
        return render_template("select_password.html",storage=stored_password,keys=list_passwords,des=des_passwords,typer="Move to public")
    else:
        return redirect("/password")
    
@app.route("/password/create")
def make_password():
    ans, user = allow_password(request.remote_addr)
    if ans:
        return render_template("make_password.html")
    else:
        return redirect("/password")

@app.route("/password/create/preview", methods=['GET','POST'])
def preview_password():
    ans, user = allow_password(request.remote_addr)
    if ans:
        found = "clear"
        ans = ""
        data = request.get_json()
        size = data.get("size")
        op =  data.get("option") == "True"
        name = data.get("name")
        view = data.get("view")
        num = int(data.get("num"))
        lc = int(data.get("lc"))
        uc = int(data.get("uc"))
        symbol = int(data.get("symbol"))
        print(num,lc,uc,symbol)
        if size == "":
            size = 0
        else:
            size = int(size)
        if size >= 5:
            ans = password_ins.gen(size,op,num,lc,uc,symbol)
        if view == "private":
            username = user
        elif view == "public":
            username = "public"
        else:
            return jsonify({"passwords" : "There has been a error a error that should have never happend this is not a password call Osama ASAP :)", "found":found}) 
        passwords = os.listdir(os.getcwd()+"//passwords//"+username)
        name = password_ins.codename(name)
        if name in passwords:
            found = "match"
        return jsonify({"passwords" : ans, "found":found}) 
    else:
        return redirect("/password")

@app.route("/password/create/pos", methods=['POST'])
def create_password():
    passwordUpload = request.form.get('passwordUpdate', '').strip()
    name = request.form.get('text', '').strip()
    size = int(request.form.get('number', '').strip())
    op = request.form.get('style', '').strip()
    des = request.form.get('des', '').strip()
    view = request.form.get('view', '').strip()
    if view == "private":
        with open(os.getcwd()+"//login_password//"+str(request.remote_addr)+".txt","r") as file:
            username = file.readline().strip()
    else:
        username = "public"
    if len(passwordUpload) == size:
        ans = password_ins.make_password(username,passwordUpload,name,des)
    else:
        pass#make the error page after 10s redirect to the make password page
    return redirect("/select_password")

@app.route("/password/del", methods=['POST','GET'])
def password_del():
    data = request.get_json()
    dothis = data.get("thisDel")
    view = data.get("view")
    if "public" in view:
        with open(os.getcwd()+"//login_password//"+str(request.remote_addr)+".txt","r") as file:
            username = file.readline().strip()
    else:
        username = "public"

    ans = password_ins.del_password(username,dothis)

    return jsonify(ans)

@app.route("/password/do I stay", methods=['POST','GET'])
def Do_i_stay():
    ans, user = allow_password(request.remote_addr)
    if ans:
        return jsonify("stay")
    else:
        return jsonify("Kick")
    
@app.route("/otpSendCode", methods=['POST','GET'])
def otpSendCode():
    data = request.get_json()
    email = data.get("email")
    code = data.get("code")
    cmd = f"select v.otp, TIMESTAMPDIFF(MINUTE, v.time, NOW()), i.uid from iden.verify as v join iden.id as i on i.uid = v.uid where email = '{email}';"
    rows = info.getdata(cmd)
    if len(rows) != 0:
        if rows[0][1] <= 2 :
            if rows[0][0] == code:
                cmd = f"delete from iden.exIP where uid = {rows[0][2]};"
                info.sendata(cmd)
                cmd = f"insert into iden.exIP (uid, ip, time) values({rows[0][2]}, '{request.remote_addr}', now());"
                info.sendata(cmd)
                info.refresh_exIP()
                refresh_exip_Api()
                return jsonify({"status":"done"})
            else:
                return jsonify({"status":"wrong code"})
        else:
            return jsonify({"status":"time up"})
    else:
        return jsonify({"status":"no record found"})
    
@app.route("/chat")
def chat():
    names = []
    rows = info.getdata(f"select name from iden where ip != '192.168.1.106' and ip != '{request.remote_addr}';")
    for row in rows :
        names.append(row[0])
    return render_template("chat.html",names=names)
    
@app.route("/optEmailCheck", methods=['POST','GET'])
def otpEmailCheck():
    data = request.get_json()
    email = data.get("email")
    cmd = f"select uid from iden.id where email = '{email}';"
    rows = info.getdata(cmd)
    if len(rows) != 0:
        uid = rows[0][0]
        code = code_maker(6)
        s1 = threading.Thread(target=send_email, args=(code,email,))
        s1.start()
        cmd = f"delete from iden.verify where uid = {uid};"
        info.sendata(cmd)
        cmd = f"delete from iden.exIP where uid = {uid};"
        info.sendata(cmd)
        cmd = f"insert into iden.verify(uid,otp,time) values({uid},'{code}',now());"
        info.sendata(cmd)
        return jsonify({"status":"done"})
    else:
        return jsonify({"status":"not done"})

@app.route("/password/logout")
def pass_logout():
    if os.path.exists(os.getcwd()+"//login_password//"+str(request.remote_addr)+".txt"):
        os.remove(os.getcwd()+"//login_password//"+str(request.remote_addr)+".txt")
    return redirect("/password")

@app.before_request
def limit():
    flag = info.verify_iden(str(request.remote_addr))
    if flag == False and request.path != "/static/5.jpg" and request.path != "/static/icon.png" and request.path != "/static/web_data/403.css" and request.path != "/static/web_data/403.js" and request.path != "/otpSendCode" and request.path != "/optEmailCheck":
        abort(403)

@app.errorhandler(404)
def http_error_handler(error):
    return render_template('404.html'), 404
@app.errorhandler(403)
def http_error_handler(error):
    return render_template("403.html"),403



if __name__ == "__main__":
    #ssl_context = 'adhoc'
    #ssl_context=('cert.pem', 'key.pem') port 443 for https
    app.run(host= "0.0.0.0", debug = False, port = 443, ssl_context=('cert.pem', 'key.pem'))
