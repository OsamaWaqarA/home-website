from flask import Flask, render_template, request, jsonify, send_file,redirect,abort

import os, threading, random, time, PasswordEngine, datetime,shutil,re

password_ins = PasswordEngine.password()

import logging
logging.basicConfig(level=logging.DEBUG)

from urllib.parse import quote, unquote

def clean_filename(filename):
    cleaned_filename = re.sub(r'[^\w\s.-]', '', filename)
    return cleaned_filename


who = []
ip = []

def video_recommend(cip,list_vid):
    [random.shuffle(list_vid) for i in range(0,100)]
    ans = []
    fcat = ""
    if os.path.exists(os.getcwd()+"/history/"+str(cip)+".txt"):
        with open(os.getcwd()+"/history/"+str(cip)+".txt","r") as file:
            line = file.readline().strip()
        parts = []
        cats = []
        parts = line.split("*")
        parts[1] = parts[1][32:len(parts[1])]
        for vid in list_vid:
            if parts[1] in vid:
                name = vid
                name = name[0:name.find("*")]
                list_vid.remove(vid)
                break
        hold = os.listdir(os.getcwd()+"//static")
        for cat in hold:
            if ".txt" in cat:
                cats.append(cat)
        for cat in cats:
            with open(os.getcwd()+"//static//"+cat,"r",errors="ignore") as file:
                while True:
                    line = file.readline().strip()
                    if line:
                        if line in name:
                            fcat = cat
                    elif line == "":
                        break
            if fcat != "":
                break
        if fcat == "":
            ans = list_vid
        else:
            for vid in list_vid:
                with open(os.getcwd()+"//static//"+fcat,"r",errors="ignore") as file:
                    while True:
                        line = file.readline().strip()
                        if line:
                            if line in vid:
                                ans.append(vid)
                        else:
                            break
            while True:
                if len(ans) >= len(list_vid):
                    break
                for vid in list_vid:
                    if vid not in ans :
                        ans.append(vid)
    else:
        ans = list_vid
    return ans
    
    

def how_much_done(filename,cip):
    resume = 0
    userList = os.listdir(os.getcwd()+"/history") 
    for user in userList:
        if cip in user:
            with open(os.getcwd()+"/history/"+user,"r") as file:
                while True:
                    line = file.readline().strip()
                    if line:
                        if filename in line:
                            notneed, notneed,resume = line.split("*")
                    else:
                        break 
    return resume 

def video_id_spearate(coded):
    loc = coded.find("*")
    video = coded[0:loc]
    id = coded[loc+1:len(coded)]
    true_id = []
    with open("video_id.txt","r") as file:
        while True:
            line = file.readline().strip()
            if line:
                if video in line and id in line:
                    return video,id
            else:
                break
    return "", ""

def video_id():
    videos = []
    with open("video.txt","r") as file:
        while True:
            line = file.readline().strip()
            if line:
                videos.append(line)
            else:
                break
    ids = []
    with open("video_id.txt","r") as file:
        while True:
            line = file.readline().strip()
            if line:
                ids.append(line)
            else:
                break
    for video in videos:
        found = False
        for id in ids:
            if video in id:
                found = True
                break
        if found == False:
            result = ""

            while True:
                ran = int(random.SystemRandom().randint(48, 122))
                if ran >= 48 and ran <= 57:
                    result += (chr(ran))
                elif ran >= 65 and ran <= 90:
                    result += (chr(ran))
                elif ran >= 97 and ran <= 122:
                    result += (chr(ran))
                if len(result) == 20:
                    if result not in ids:
                        break
                    else:
                        result = ""
            ids.append(video+"*"+result)
    with open("video_id.txt","w") as file:
        for id in ids:
            file.write(id)
            file.write("\n")
    
        
    
    

def check_videos():
    v_slow = os.listdir("/media/osama/slow")
    v_usb = os.listdir("/media/osama/usb")
    for i in range(0,100):
        for j in range(0,len(v_slow)):
            if ".mp4" not in v_slow[j] or ".mkv" not in v_slow[j]:
                v_slow.remove(v_slow[j])
                break
    for i in range(0,100):
        for j in range(0,len(v_usb)):
            if ".mp4" not in v_usb[j] or ".mkv" not in v_usb[j]:
                v_usb.remove(v_usb[j])
                break
            
    hold = []
    for i in range(0,len(v_slow)):
        hold.append(v_slow[i])
    for i in range(0,len(v_usb)):
        hold.append(v_usb[i])
        
    try:
        os.remove("video.txt")
    except FileNotFoundError:
        pass
    
    with open("video.txt","a") as file:
        for i in range(0,len(hold)):
            file.write(hold[i])
            file.write("\n")
    video_id()
        

def identify(ip):
    twho = []
    tip = []

    with open(os.getcwd()+"//loc.txt","r") as file:
        while True:
            line = file.readline().strip()
            if line:
                tip.append(line)
            else:
                break
    for i in range(0,len(tip)):
        num = int(tip[i].find("*"))
        twho.append(tip[i][num+1:len(tip[i])])
        tip[i] = tip[i][0:num]
        if ip == tip[i]:
            return twho[i]
    


twho = []
tip = []

with open(os.getcwd()+"//loc.txt","r") as file:
    while True:
        line = file.readline().strip()
        if line:
            tip.append(line)
        else:
            break
for i in range(0,len(tip)):
    num = int(tip[i].find("*"))
    twho.append(tip[i][num+1:len(tip[i])])
    tip[i] = tip[i][0:num]
ip = tip
who = twho

app = Flask(__name__)

#start_video = threading.Thread(target=check_videos)

#start_video.start()

@app.route('/video/<video_filename>')
def serve_video(video_filename):
    data = []
    with open("video_id.txt","r") as file:
        while True:
            line = file.readline().strip()
            if line:
                data.append(line)
            else:
                break
    for i in range(0,len(data)):
        video_temp,hold  = video_id_spearate(data[i])
        if video_filename == hold:
            video_filename = video_temp
            break
    if os.path.exists("/media/osama/slow/" + video_filename):
        video_path = "/media/osama/slow/" + video_filename
    else:
        video_path = "/media/osama/usb/" + video_filename
    return send_file(video_path, mimetype='video/mp4')


@app.route("/")
def index():
    start_video = threading.Thread(target=check_videos)
    start_video.start()
    here = -1
    for i in range(0,len(ip)):
        if str(request.remote_addr) == ip[i]:
            here = i
            break
    if here == -1 :
        return render_template("index.html",name = "Guest")
    else:
        return render_template("index.html",name=who[here])

        

@app.route("/select_video")
def select_video():
    read = []
    with open("video_id.txt","r") as file:
        while True:
            line = file.readline().strip()
            if line:
                read.append(line)
            else:
                break
            
    read = video_recommend(str(request.remote_addr),read)
            
    video = []
    ids = []
    
    for i in range(0,10):
        video_hold,ids_hold = video_id_spearate(read[i])
        video.append(video_hold)
        ids.append(ids_hold)
            
    name  = []
    nail = []
    for i in range(0,10):
        name.append(video[i][0:-4])
        nail.append(video[i][0:-4]+".jpg")
    return render_template("select_video.html",shows = name,names=nail,links = ids)

@app.route("/restVideo", methods=['GET','POST'])
def rest_of_video():
    data = request.get_json()
    present = data.get("videosHere")
    rest_control = data.get("number_called")
    full = False
    video = []
    hold = []
    link = []
    if rest_control == -1:
        size = 10000
    else:
        size = 10
    with open("video_id.txt", "r") as file:
        while True:
            line = file.readline().strip()
            if line:
                hold.append(line)
            else:
                break
    hold = video_recommend(str(request.remote_addr),hold)
    if len(present) >= len(hold):
        return jsonify({'status': 'success',
                        "full": True}) 
    i = 0
    while True:
        video_temp,link_temp = video_id_spearate(hold[i])
        if link_temp in present:
            pass
        else:
            video.append(video_temp)
            link.append(link_temp)
        i += 1
        if len(video) == size or i > len(hold)-1:
            break
    video_data = []
    for i in range(0,len(video)):
        video_data.append({
            "shows": video[i][0:-4],
            "names": video[i][0:-4] + ".jpg",
            "lines": link[i],
            "full": full
        })

    return jsonify(video_data) 
    
@app.route('/update_time', methods=['POST'])
def update_time():
    data = request.get_json()
    current_time = data.get('time')
    loc = data.get('loc').strip()

    loc = unquote(loc.replace("http://192.168.1.106:5000/play_video/",""))
    reads = [str(request.remote_addr)+"*"+str(loc)+"*"+str(current_time)]
    try:
        with open(os.getcwd()+"//history//"+str(request.remote_addr)+".txt","r") as file:
            while True:
                line = file.readline().strip()
                if line:
                    reads.append(line)
                else:
                    break
        try:
            if loc in reads[1]:
                reads.remove(reads[1])
        except IndexError:
            pass
        with open(os.getcwd()+"//history//"+str(request.remote_addr)+".txt","w") as file:
            for read in reads:
                file.write(read)
                file.write("\n")   
    except(FileNotFoundError):
        with open(os.getcwd()+"//history//"+str(request.remote_addr)+".txt","a") as file:
            file.write(reads[0])
    
    return jsonify({'status': 'success'}) 

@app.route("/drive")
def drive_select():
    return render_template("drive.html")

@app.route("/submit")
def submit():
    return render_template('submit.html',loc = "public_upload")

@app.route("/drive/upload")
def pdrive_upload():
    return render_template('submit.html',loc = "private_drive")

@app.route("/get_download_name", methods=['POST','GET'])
def get_download_name():
    data = request.get_json()
    want = data.get("want")
    if "public_download" in want:
        result = os.listdir(os.getcwd()+"//static//uploads")
    elif "private_drive" in want:
        result = os.listdir(os.getcwd()+"//static/drive//"+str(request.remote_addr))
    else:
        return jsonify({"status":"Wrong_type"})
    return jsonify({"status":"sucess","result":result})

@app.route("/drive/upload/force", methods=['POST','GET'])
def pdrive_upload_force():
    data = request.get_json()
    filename = data.get('getthis')
    for file in filename:
        if os.path.exists(os.getcwd()+"//static//drive//"+str(request.remote_addr)):
            shutil.move(os.getcwd()+"//static//uploads//"+file, os.getcwd()+"//static//drive//"+str(request.remote_addr)+"//"+file)
        else:
            os.mkdir(os.getcwd()+"//static//drive//"+str(request.remote_addr))
            os.mkdir(os.getcwd()+"//static//drive//trash//"+str(request.remote_addr))
            shutil.move(os.getcwd()+"//static//uploads//"+file, os.getcwd()+"//static//drive//"+str(request.remote_addr)+"//"+file)
    return jsonify({"status":"sucess"})
    
@app.route('/upload', methods=['POST'])
def upload_file():
    loc = request.form.get('fromwhere', '').strip()
    if 'file[]' not in request.files:
        return 'No file part'
    
    files = request.files.getlist('file[]')

    if len(files) == 0:
        return jsonify({'status': 'error'})
    for file in files:
        if file.filename == '':
            return jsonify({'status': 'error'})
        file.filename = clean_filename(file.filename)
        if "public_upload" in loc:
            file.save(os.getcwd()+"//static//uploads/" + file.filename)
        elif "private_drive" in loc:
            if os.path.exists(os.getcwd()+"//static//drive//"+str(request.remote_addr)):
                file.save(os.getcwd()+"//static//drive/" +str(request.remote_addr)+"/"+ file.filename)
            else:
                os.mkdir(os.getcwd()+"//static//drive//"+str(request.remote_addr))
                os.mkdir(os.getcwd()+"//static//drive//trash//"+str(request.remote_addr))
                file.save(os.getcwd()+"//static//drive/" +str(request.remote_addr)+"/"+ file.filename)
        else:
            return jsonify({'status': 'error'})
    return jsonify({'status': 'success'}) 

@app.route('/play_video/<filename>')
def play_video(filename):
    cip = str(request.remote_addr)
    resume = how_much_done(filename,cip)   
    custom_controls = False 
    with open("custom_controls.txt","r") as file:
        while True:
            line = file.readline().strip()
            if line:
                if str(request.remote_addr) in line:
                    custom_controls = True
                    logging.warning("we have a custom boy")
            else:
                break
    video = []
    ids = []
    data = []
    
    with open("video_id.txt","r") as file:
        while True:
            line = file.readline().strip()
            if line:
                data.append(line)
            else:
                break
    for i in range(0,len(data)):
        video_temp,hold_1  = video_id_spearate(data[i])
        if filename == hold_1:
            v_title = video_temp
            break
    data = video_recommend(cip,data)
    for i in range(0,2):
        video_hold,ids_hold = video_id_spearate(data[i])
        video.append(video_hold)
        ids.append(ids_hold)
            
    name  = []
    nail = []
    percent = []
    for i in range(0,len(video)):#try index out of range add that here
        name.append(video[i][0:-4])
        nail.append(video[i][0:-4]+".jpg")
    return render_template('play_video.html',custom_controls = custom_controls,dataTitle = v_title,filename=filename,shows = name,names=nail,links = ids,resume=resume)

@app.route("/print")
def print():
    return render_template('print.html',number = 1)

@app.route('/printout', methods=['POST'])
def printout():
    side = request.form.get('side', '').strip()
    number = request.form.get('number', '').strip()
    color = request.form.get('color', '').strip()
    angle = request.form.get('angle','').strip()
     
    if 'file' not in request.files:
        return 'No file part'
    
    file = request.files['file']

    if file.filename == '':
        return 'No selected file'
    
    file.save(os.getcwd()+"/" +file.filename)

    os.system("lp "+str(os.getcwd())+"/" +str(file.filename))
    def remove_after_done():
        time.sleep(30)
        os.remove("lp "+str(os.getcwd())+"/" +str(file.filename))
    remove_the_file = threading.Thread(target=remove_after_done)
    remove_the_file.start()
    
    return render_template("done.html")



@app.route("/zakat")
def zakat():
    history = []
    red = []
    uip = request.remote_addr
    if uip == "192.168.1.107":
        with open(os.getcwd()+"/zakat.txt","r") as file:
            amount = float(file.readline().strip())
        with open(os.getcwd()+"/zakat_history.txt","r") as file:
            while True:
                history.append(file.readline().strip())
                if "EOF" in history:
                    break
        history.remove("EOF")
        for i in range(0,len(history)):
            if "+" in history[i]:
                red.append("False")
            else:
                red.append("True")
        return render_template("admin_zakat.html",amount = amount,historys=history,red=red)
    else:
        with open(os.getcwd()+"/zakat.txt","r") as file:
            amount = float(file.readline().strip())
        return render_template("zakat.html",amount = amount)
    
@app.route("/process_zakat", methods=['POST'])
def process_zakat():
    history = []
    update = request.form.get('number', '').strip()
    op = request.form.get('option', '').strip()
    uip = request.remote_addr

    if uip == "192.168.1.107":

        if "neg" in op:
            with open(os.getcwd()+"/zakat.txt","r") as file:
                amount = float(file.readline().strip())
            amount -= float(update)
            with open(os.getcwd()+"/zakat.txt","w") as file:
                file.write(str(amount))
            with open(os.getcwd()+"/zakat_history.txt","r") as file:
                while True:
                    history.append(file.readline().strip())
                    if "EOF" in history:
                        break
            history.remove("EOF")
            history.append(time.ctime()+" : -"+update)
            history.append("EOF")
            with open(os.getcwd()+"/zakat_history.txt","w") as file:
                for i in range(0,len(history)):
                    file.write(history[i])
                    file.write("\n")
            return redirect("/zakat")
        elif "pos" in op:
            with open(os.getcwd()+"/zakat.txt","r") as file:
                amount = float(file.readline().strip())
            amount += float(update)
            with open(os.getcwd()+"/zakat.txt","w") as file:
                file.write(str(amount))
            with open(os.getcwd()+"/zakat_history.txt","r") as file:
                while True:
                    history.append(file.readline().strip())
                    if "EOF" in history:
                        break
            history.remove("EOF")
            history.append(time.ctime()+" : +"+update)
            history.append("EOF")
            with open(os.getcwd()+"/zakat_history.txt","w") as file:
                for i in range(0,len(history)):
                    file.write(history[i])
                    file.write("\n")
            return redirect("/zakat")
    else:
        abort(403)
        
@app.route("/download/")
def download():
    filenames = os.listdir(os.getcwd()+"//static//uploads")
    types = []
    for file in filenames:
        if ".jpg"  in file or ".jpeg"  in file or ".png" in file:
            types.append("image")
        elif ".mp4" in file:
            types.append("video")
        else :
            types.append("unknown")
    return render_template("download.html",filenames=filenames,loc = "public_download",types = types)


@app.route("/drive/download")
def fdrive_download():
    cip = str(request.remote_addr) 
    if os.path.exists(os.getcwd()+"//static//drive//"+cip):
        filenames = os.listdir(os.getcwd()+"//static//drive//"+cip)
        types = []
        for file in filenames:
            if ".jpg"  in file or ".jpeg"  in file or ".png" in file:
                types.append("image")
            elif ".mp4" in file:
                types.append("video")
            else :
                types.append("unknown")
        return render_template("download.html",filenames=filenames,loc = "private_drive",IP= cip,types=types)
    else:
        return redirect("/drive/upload")

@app.route("/delete_file",methods=['GET','POST'])
def delete_file():
    data = request.get_json()
    deletes = data.get("delThis")
    loc = data.get("loc")
    if type(deletes) == list:
        for delete in deletes:
            if "public_download" in loc:
                shutil.move((os.getcwd()+"//static//uploads//"+delete),(os.getcwd()+"//static//trash//"+delete))
            elif "private_drive" in loc:
                shutil.move((os.getcwd()+"//static//drive//"+str(request.remote_addr)+"/"+delete),os.getcwd()+"//static//drive//trash//"+str(request.remote_addr)+"/"+delete)
    else:
        if "public_download" in loc:
            shutil.move((os.getcwd()+"//static//uploads//"+deletes),(os.getcwd()+"//static//trash//"+deletes))
        elif "private_drive" in loc:
            shutil.move((os.getcwd()+"//static//drive//"+str(request.remote_addr)+"/"+deletes),os.getcwd()+"//static//drive//trash//"+str(request.remote_addr)+"/"+deletes)
    return jsonify({'status': 'success'}) 

@app.route("/password")
def Password():
    if os.path.exists(os.getcwd()+"//login_password//"+str(request.remote_addr)+".txt"):
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

@app.route("/select_password")
def select_password():
    ids = []
    ids = os.listdir(os.getcwd()+"//login_password")
    for id in ids:
        if str(request.remote_addr) in id:
            with open(os.getcwd()+"//login_password//"+id,"r") as file:
                username = file.readline().strip()
                break
    stored_password = os.listdir(os.getcwd()+"//passwords//"+username)
    list_passwords = []
    des_passwords = []
    for i in range(0,len(stored_password)):
        stored_password[i] = password_ins.decodename(stored_password[i])
    stored_password.remove(username)
    for passkey in stored_password:
        temp_pass ,temp_des = password_ins.read_password(username,passkey)
        list_passwords.append(temp_pass)
        des_passwords.append(temp_des)
    
    return render_template("select_password.html",storage=stored_password,keys=list_passwords,des=des_passwords)
@app.route("/password/create")
def make_password():
    return render_template("make_password.html")

@app.route("/password/create/preview", methods=['GET','POST'])
def preview_password():
    found = "clear"
    ans = ""
    data = request.get_json()
    size = data.get("size")
    op = bool(data.get("option"))
    name = data.get("name")
    if size == "":
        size = 0
    else:
        size = int(size)
    if size >= 5:
        ans = password_ins.gen(size,op)
    with open(os.getcwd()+"//login_password//"+str(request.remote_addr)+".txt","r") as file:
        username = file.readline().strip()
    passwords = os.listdir(os.getcwd()+"//passwords//"+username)
    name = password_ins.codename(name)
    if name in passwords:
        found = "match"
    return jsonify({"passwords" : ans,
                   "found":found}) 

@app.route("/password/create/pos", methods=['POST'])
def create_password():
    passwordUpload = request.form.get('passwordUpdate', '').strip()
    name = request.form.get('text', '').strip()
    size = int(request.form.get('number', '').strip())
    op = request.form.get('style', '').strip()
    des = request.form.get('des', '').strip()
    with open(os.getcwd()+"//login_password//"+str(request.remote_addr)+".txt","r") as file:
        username = file.readline().strip()
    if len(passwordUpload) == size:
        ans = password_ins.make_password(username,passwordUpload,name,des)
    else:
        pass#make the error page after 10s redirect to the make password page
    return redirect("/select_password")

@app.route("/password/del", methods=['POST','GET'])
def password_del():
    data = request.get_json()
    dothis = data.get("thisDel")
    with open(os.getcwd()+"//login_password//"+str(request.remote_addr)+".txt","r") as file:
        username = file.readline().strip()

    ans = password_ins.del_password(username,dothis)

    return jsonify(ans)
@app.route("/password/logout")
def pass_logout():
    if os.path.exists(os.getcwd()+"//login_password//"+str(request.remote_addr)+".txt"):
        os.remove(os.getcwd()+"//login_password//"+str(request.remote_addr)+".txt")
    return redirect("/password")

@app.route("/chat/group")
def group_chat():
    log = []
    message = []
    times = []
    name = []
    with open(os.getcwd()+"//static//web_data//chat//group.txt","r") as file:
        for i in range (0,20):
            line = file.readline().strip()
            if line:
                log.append(line)
            else:
                break
        for i in range(0,len(log)):
            tname,ttimes,tmessage = log[i].split("*")
            name.append(tname)
            times.append(ttimes)
            message.append(tmessage)
    return render_template("chat.html",lines = message,times = times,names = name)

@app.route("/chat_update" , methods=['GET','POST'])
def chat_update():
    data = request.get_json()
    message = data.get("message")
    to = data.get("to")
    nameF = identify(str(request.remote_addr))
    responds = (nameF+"*"+str(time.ctime())+"*"+str(message))
    if "group" in to:
        with open(os.getcwd()+"//static//web_data//chat//group.txt","a")as file:
            file.write(responds)
            file.write("\n")
    return jsonify({'status': 'success'})  

@app.before_request
def limit():
    flag = False
    for ips in ip:
        if request.remote_addr == ips:
            flag = True
            break
    if flag == False and request.path != "/static/locks.mp4" and request.path != "/static/icon.png":
        abort(403) 

@app.errorhandler(404)
def http_error_handler(error):
    return render_template('404.html'), 404

@app.errorhandler(403)
def http_error_handler(error):
    return render_template("403.html"),403


if __name__ == "__main__":
    app.run(host= "0.0.0.0",debug = True,port = 8000)