from flask import Flask, render_template, request, jsonify, send_file,redirect,abort

import os, threading, time,shutil,re,pypandoc, videoMaster, requests,dbms

info = dbms.dbms()

#import logging
#logging.basicConfig(level=logging.DEBUG)

from urllib.parse import quote, unquote


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

def send_to_control_Api(ip,data):
    try:
        response = requests.post("http://192.168.1."+str(ip)+":5000/info", json=data, timeout=5)
        response.raise_for_status()  
        return response.json(),"success"
    except requests.exceptions.RequestException as e:
        return None,"Failed"

def clean_filename(filename,respace = True):
    cleaned_filename = re.sub(r'[^\w\s.-]', '', filename)
    while respace:
        if " " not in  cleaned_filename:
            break
        hold =  cleaned_filename[0: cleaned_filename.find(" ")]
        cleaned_filename =  cleaned_filename[ cleaned_filename.find(" ")+1:len( cleaned_filename)]
        cleaned_filename = hold +"_"+  cleaned_filename
    return cleaned_filename

def remove_after_done(name,page):
    time.sleep(60*int(page))
    os.remove(str(os.getcwd())+"/" +str(name))

@app.route('/video/<video_filename>')
def serve_video(video_filename):
    cmd = "select l.location, v.name from vid.location as l join vid.video as v on v.vid_ID = l.vid_ID  where v.vid_ID = '"+str(video_filename)+"';"
    ans = info.getdata(cmd)
    video_path = f"/media/osama/{ans[0][0]}/{ans[0][1]}.mp4"
    return send_file(video_path, mimetype='video/mp4')

def file_size_man(size):
    units = ["bytes", "KB", "MB", "GB", "TB"]
    factor = 1000  
    unit_index = 0

    while size >= factor and unit_index < len(units) - 1:
        size /= factor
        unit_index += 1

    return f"{size:.2f} {units[unit_index]}"


@app.route("/")
def index():
    fsize = ""
    backup = False

    if os.path.exists(os.getcwd()+"//static//website.tar.gz"):
        backup = True
        size = os.path.getsize(os.getcwd()+"//static//website.tar.gz")
        fsize = "The file size: "+file_size_man(size)
    name = info.get_name(str(request.remote_addr))

    return render_template("index.html",name=name,fsize=fsize,show="“I Crashed my Airplane” - What can we learn from this Trevor Jacob React",names="“I Crashed my Airplane” - What can we learn from this Trevor Jacob React.jpg")

@app.route("/refreshExIP", methods=['GET','POST'])
def refreshexIP():
    info.refresh_exIP()
    return jsonify({"status":"done"})

@app.route("/removeTrash")
def TrashClean():
    Thelist = []
    Thelist = os.listdir(os.getcwd()+"//static//trash")
    for data in Thelist:
        os.remove(os.getcwd()+"//static//trash//"+data)
    return redirect("/")

@app.route("/search",methods=['POST'])
def search():
    op = request.form.get('option', '').strip()
    text = request.form.get('text', '').strip()

    if "All" in op and len(text) > 0:
        newlist = info.search_video(text)
    elif "All" not in op:
        newlist = info.search_video(text,op)
    else:
        return redirect("/select_video")
    
    ids = []
    name  = []
    nail = []

    ops = ["All"]
    op = info.getdata("select cat_name from vid.category;")
    for data in op:
        ops.append(data[0])
    
    for data in newlist:
        name.append(data[0])
        ids.append(data[1])
        nail.append(data[0]+".jpg")
            
    return render_template("select_video.html",shows = name,names=nail,links = ids,ops=ops)

@app.route("/display_playlist<filename>")
def display_playlist(filename):
    uid = info.get_uid_from_ip(request.remote_addr)
    rows = info.getdata(f"select v.name, v.vid_ID, IFNULL(h.duration, 0) from vid.video as v left join vid.history as h on h.vid_ID = v.vid_ID and h.uid = {uid[0][0]}  where v.playlistID = '{filename}' order by episode asc;")
    

@app.route("/playlist")
def playlist():
    rows = info.getdata('select playlistID, Playlist_name  from vid.playlist where playlistID != "AA00";')
    plists = []
    link = []
    nail = []
    for row in rows:
        nailtemp = info.getdata(f"select name from vid.video where playlistID = '{row[0]}' order by episode asc limit 1;")
        nail.append(nailtemp[0][0]+".jpg") #make this more effiect calling db in each loop is madness
        link.append(row[0])
        plists.append(row[1])
    return render_template("select_playlist.html", lines = link,shows = plists,nail=nail)
    

@app.route("/select_video")
def select_video():
    name  = []
    nail = []
    ids = []
    cuslist = info.recommend_video(request.remote_addr)

    ops = ["All"]
    op = info.getdata("select cat_name from vid.category;")
    for data in op:
        ops.append(data[0])

    for data in cuslist:
        name.append(data[0])
        nail.append(data[0]+".jpg")
        ids.append(data[1])
    return render_template("select_video.html",shows = name,names=nail,links = ids,ops=ops)

@app.route("/update_loc", methods=['GET','POST'])
def update_loc():
    data = request.get_json()
    ip = str(data.get("ip"))
    

    res, result = send_to_control_Api(ip,data)
    if result == "success" :
        return jsonify(res)
    else:
        if "123" in ip:
            ip = "102"
        else:
            ip = "123"
        res, result = send_to_control_Api(ip,data)
        if result == "success":
            return jsonify(res)
        else:
            return jsonify({"status":"failed"})

@app.route("/control_device")
def master_control():
    return render_template("remote_control.html")
    
@app.route('/update_time', methods=['POST'])
def update_time():
    data = request.get_json()
    current_time = data.get('time')
    loc = data.get('loc').strip()

    loc = (loc[-6:len(loc)])
    info.update_video_history(request.remote_addr,loc[-6:len(loc)],current_time)

    return jsonify({'status': 'success'}) 

@app.route("/transfer")
def transfer():
    plist = os.listdir(os.getcwd()+"//static//drive//")
    option2data = []
    for data in plist:
        if "trash" not in data:
            option2data.append(info.get_name(data))
    folder = os.listdir(os.getcwd()+"//static//drive//"+plist[0])
    option3data = ["lobby"]
    filenames = []
    types = []
    for data in folder:
        if os.path.isdir(os.getcwd()+"//static//drive//"+plist[0]+"//"+data):
            option3data.append(data)
    
    filedata = os.listdir(os.getcwd()+"//static//uploads")
    for data in filedata:
        filenames.append(data)
        if ".jpg" in data or ".png" in data or ".jpeg" in data:
            types.append("image")
        elif ".mp4" in data:
            types.append("video")
        else:
            types.append("unknown")

    return render_template("transfer.html",loc="public_download",filenames=filenames,types=types,option2data=option2data,option3data=option3data,op1data = ["public","private"],option1data = ["private","public"])

@app.route("/transfer/data", methods=['POST','GET'])
def transfer_Data():
    data = request.get_json()
    op1data = data.get("op1data")
    op2data = data.get("op2data")

    option1data = data.get("option1data")
    option2data = data.get("option2data")
    option3data = data.get("option3data")
    copylist = data.get("copylist")

    if "public" in op1data:
        if "public" in option1data:
            return jsonify({"status":"can not copy and paste at same location"})
        if "lobby" in option3data:
            for data in copylist:
                try: 
                    shutil.move(os.getcwd()+"//static//uploads//"+data, os.getcwd()+"//static//drive//"+info.get_ip_from_name(option2data)+"//")
                except Exception as e:
                    if os.path.exists(os.getcwd()+"//static//uploads//"+data) and os.path.exists(os.getcwd()+"//static//drive//"+info.get_ip_from_name(option2data)+"//"+data):
                        os.remove(os.getcwd()+"//static//uploads//"+data)
        else:
            for data in copylist:
                try:
                    shutil.move(os.getcwd()+"//static//uploads//"+data, os.getcwd()+"//static//drive//"+info.get_ip_from_name(option2data)+"//"+option3data+"//")
                except Exception as e:
                    if os.path.exists(os.getcwd()+"//static//uploads//"+data) and os.path.exists(os.getcwd()+"//static//drive//"+info.get_ip_from_name(option2data)+"//"+option3data+"//"+data):
                        os.remove(os.getcwd()+"//static//uploads//"+data)           
    else:
        if op2data in option3data and str(request.remote_addr) in info.get_ip_from_name(option2data):
            return jsonify({"status":"can not copy and paste at same location"})
        if "public" in option1data:
            if "lobby" in op2data:
                for data in copylist:
                    try:
                        shutil.move(os.getcwd()+"//static//drive//"+str(request.remote_addr)+"//"+data,os.getcwd()+"//static//uploads//")
                    except Exception as e:
                        if os.path.exists(os.getcwd()+"//static//drive//"+str(request.remote_addr)+"//"+data) and os.path.exists(os.getcwd()+"//static//uploads//"+data):
                            os.remove(os.getcwd()+"//static//drive//"+str(request.remote_addr)+"//"+data)
            else:
                for data in copylist:
                    try:
                        shutil.move(os.getcwd()+"//static//drive//"+str(request.remote_addr)+"//"+op2data+"//"+data,os.getcwd()+"//static//uploads//")
                    except Exception as e:
                        if os.path.exists(os.getcwd()+"//static//drive//"+str(request.remote_addr)+"//"+op2data+"//"+data) and os.path.exists(os.getcwd()+"//static//uploads//"+data):
                            os.remove(os.getcwd()+"//static//drive//"+str(request.remote_addr)+"//"+op2data+"//"+data)
        else:
            if "lobby" in op2data and "lobby" in option3data:
                for data in copylist:
                    try:
                        shutil.move(os.getcwd()+"//static//drive//"+str(request.remote_addr)+"//"+data,os.getcwd()+"//static//drive//"+info.get_ip_from_name(option2data)+"//")
                    except Exception as e:
                        if os.path.exists(os.getcwd()+"//static//drive//"+str(request.remote_addr)+"//"+data) and os.path.exists(os.getcwd()+"//static//drive//"+info.get_ip_from_name(option2data)+"//"+data):
                            os.remove(os.getcwd()+"//static//drive//"+str(request.remote_addr)+"//"+data)
            elif "lobby" in op2data and "lobby" not in option3data:
                for data in copylist:
                    try:
                        shutil.move(os.getcwd()+"//static//drive//"+str(request.remote_addr)+"//"+data,os.getcwd()+"//static//drive//"+info.get_ip_from_name(option2data)+"//"+option3data+"//")
                    except Exception as e:
                        if os.path.exists(os.getcwd()+"//static//drive//"+str(request.remote_addr)+"//"+data) and os.path.exists(os.getcwd()+"//static//drive//"+info.get_ip_from_name(option2data)+"//"+option3data+"//"+data):
                            os.remove(os.getcwd()+"//static//drive//"+str(request.remote_addr)+"//"+data)
            elif "lobby" not in op2data and "lobby" in option3data:
                for data in copylist:
                    try:
                        shutil.move(os.getcwd()+"//static//drive//"+str(request.remote_addr)+"//"+op2data+"//"+data,os.getcwd()+"//static//drive//"+info.get_ip_from_name(option2data)+"//")
                    except Exception as e:
                        if os.path.exists(os.getcwd()+"//static//drive//"+str(request.remote_addr)+"//"+op2data+"//"+data) and os.path.exists(os.getcwd()+"//static//drive//"+info.get_ip_from_name(option2data)+"//"+data):
                            os.remove(os.getcwd()+"//static//drive//"+str(request.remote_addr)+"//"+op2data+"//"+data)
            else:
                try:
                    shutil.move(os.getcwd()+"//static//drive//"+str(request.remote_addr)+"//"+op2data+"//"+data,os.getcwd()+"//static//drive//"+info.get_ip_from_name(option2data)+"//"+option3data+"//")
                except Exception as e:
                    if os.path.exists(os.getcwd()+"//static//drive//"+str(request.remote_addr)+"//"+op2data+"//"+data) and os.path.exists(os.getcwd()+"//static//drive//"+info.get_ip_from_name(option2data)+"//"+option3data+"//"+data):
                        os.remove(os.getcwd()+"//static//drive//"+str(request.remote_addr)+"//"+op2data+"//"+data)

    return jsonify({"status":"sucess"})

@app.route("/transfer/config/<op1data>/<op2data>/<option1data>/<option2data>/<option3data>")
def transfer_config(op1data,op2data,option1data,option2data,option3data):
    op1data = clean_filename(op1data,False)
    op2data = clean_filename(op2data,False)
    option1data = clean_filename(option1data,False)
    option2data = clean_filename(option2data,False)
    option3data = clean_filename(option3data,False)
    filenames = []
    types = []
    newop1data = []
    newop1data.append(op1data)
    newop2data = []
    loc = ""
    if "public" in op1data:
        loc = "public_download"
        newop1data.append("private")
        fdata = os.listdir(os.getcwd()+"//static//uploads")
    else:
        loc = "private_drive"
        newop1data.append("public")
        newop2data.append("lobby")
        if op2data == None or op2data == "":
            op2data = "lobby"
        filedata = os.listdir(os.getcwd()+"//static//drive//"+str(request.remote_addr))

        if "lobby" in op2data:
            fdata = []
            for data in filedata:
                if os.path.isfile(os.getcwd()+"//static//drive//"+str(request.remote_addr)+"//"+data):
                    fdata.append(data)
        else:
            fdata = os.listdir(os.getcwd()+"//static//drive//"+str(request.remote_addr)+"//"+op2data)

        for data in filedata:
            if os.path.isdir(os.getcwd()+"//static//drive//"+str(request.remote_addr)+"//"+data):
                newop2data.append(data)
        for i in range(0,len(newop2data)):
            if op2data == newop2data[i] and i > 0:
                newop2data[i] = newop2data[0]
                newop2data[0] = op2data

    for data in fdata:
        filenames.append(data)
        if ".jpg" in data or ".png" in data or ".jpeg" in data:
            types.append("image")
        elif ".mp4" in data:
            types.append("video")
        else:
            types.append("unknown")
    
    newop1 = [option1data]
    newop2 = []
    newop3 = []

    if "private" in option1data:
        plist = os.listdir(os.getcwd()+"//static//drive//")
        newop1.append("public")
        if option2data == "" or option2data == "<>" or option2data == None:
            for data in plist:
                if os.path.isdir(os.getcwd()+"//static//drive//"+data) and "trash" not in data:
                    option2data = info.get_name(data)
                    option3data = "lobby"
                    break
        newop2.append(option2data)
        plist = os.listdir(os.getcwd()+"//static//drive//")
        for data in plist:
            if os.path.isdir(os.getcwd()+"//static//drive//"+data) and "trash" not in data:
                if info.get_name(data) not in option2data :
                    newop2.append(info.get_name(data))
        plist = os.listdir(os.getcwd()+"//static//drive//"+info.get_ip_from_name(option2data)) 
        for data in plist:
            if os.path.isdir(os.getcwd()+"//static//drive//"+info.get_ip_from_name(option2data)+"//"+data):
                newop3.append(data)
        newop3.append("lobby")
        for i in range(0,len(newop3)):
            if option3data ==  newop3[i] and i > 0:
                newop3[i] = newop3[0]
                newop3[0] = option3data

    else:
        newop1.append("private")
        newop2 = []
        newop3 = []

    return render_template("transfer.html",IP=str(request.remote_addr),loc=loc,filenames=filenames,types=types,option1data = newop1,option2data=newop2,option3data=newop3,op1data = newop1data,op2data=newop2data )

@app.route("/drive")
def drive_select():
    return render_template("drive.html")

@app.route("/submit")
def submit():
    return render_template('submit.html',loc = "public_upload")

@app.route("/drive/upload")
def pdrive_upload():
    folders = ["lobby","+"]
    if os.path.exists(os.getcwd()+"//static/drive//"+str(request.remote_addr)):
        result = os.listdir(os.getcwd()+"//static/drive//"+str(request.remote_addr))
        for data in result:
            if os.path.isdir(os.getcwd()+"//static/drive//"+str(request.remote_addr)+"//"+data):
                folders.append(data)
    return render_template('submit.html',loc = "private_drive",options=folders)

@app.route("/get_download_name", methods=['POST','GET'])
def get_download_name():
    data = request.get_json()
    want = data.get("want")
    if "public_download" in want:
        result = os.listdir(os.getcwd()+"//static//uploads")
    elif "private_drive" in want:
        roomloc = data.get("roomloc")
        if "lobby" in roomloc:
            hold = os.listdir(os.getcwd()+"//static/drive//"+str(request.remote_addr))
            result = []
            for data in hold:
                if os.path.isfile(os.getcwd()+"//static/drive//"+str(request.remote_addr)+"//"+data):
                    result.append(data)
        else:
            result = os.listdir(os.getcwd()+"//static/drive//"+str(request.remote_addr)+"//"+roomloc)
        
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
        return jsonify({'status': 'error'})
    
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
            op = str(request.form.get('option', '').strip())
            if "+" in op:
                newloc = str(request.form.get('newfolder', '').strip())
                newloc = clean_filename(newloc)
            if os.path.exists(os.getcwd()+"//static//drive//"+str(request.remote_addr)):
                pass
            else:
                os.mkdir(os.getcwd()+"//static//drive//"+str(request.remote_addr))
                os.mkdir(os.getcwd()+"//static//drive//trash//"+str(request.remote_addr))
            if "lobby" in op:
                file.save(os.getcwd()+"//static//drive/" +str(request.remote_addr)+"/"+ file.filename)
            elif "+" in op:
                if len(newloc) < 2 :
                    return jsonify({'status': 'error'})
                if os.path.exists(os.getcwd()+"//static//drive//"+str(request.remote_addr)+"/"+newloc):
                    pass
                else:
                    os.mkdir(os.getcwd()+"//static//drive//"+str(request.remote_addr)+"/"+newloc)
                file.save(os.getcwd()+"//static//drive/" +str(request.remote_addr)+"/"+newloc+"/"+ file.filename)
            else:
                if os.path.exists(os.getcwd()+"//static//drive/" +str(request.remote_addr)+"/"+op):
                    file.save(os.getcwd()+"//static//drive/" +str(request.remote_addr)+"/"+op+"/"+ file.filename)
                else:
                    return jsonify({'status': 'error'})
        else:
            return jsonify({'status': 'error'})
    return jsonify({'status': 'success'}) 

@app.route('/play_video/<filename>')
def play_video(filename):
    cip = str(request.remote_addr)  
    resume = info.get_watchTime_video(filename,cip)
    custom_controls = False 
    with open("custom_controls.txt","r") as file:
        while True:
            line = file.readline().strip()
            if line:
                if str(request.remote_addr) in line:
                    custom_controls = True
            else:
                break
    name  = []
    nail = []
    ids = []
    v_title = info.getdata(f"select name from vid.video where vid_ID = '{filename}';")
    v_title = v_title[0][0]
    ops = ["All"]
    op = info.getdata("select cat_name from vid.category;")
    for data in op:
        ops.append(data[0])
    cuslist = info.recommend_video(cip,watching=filename)
    for i in range(0,len(cuslist)):
        name.append(cuslist[i][0])
        nail.append(cuslist[i][0]+".jpg")
        ids.append(cuslist[i][1])
    return render_template('play_video.html',custom_controls = custom_controls,dataTitle = v_title,filename=filename,shows = name,names=nail,links = ids,resume=resume,next_vid=ids[0],ops=ops)

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
    
    file.filename = clean_filename(file.filename)
    
    file.save(os.getcwd()+"/" +file.filename)

    command = "-o media=A4"
    command = command + " -n " + str(number)
    if  "False" in color:
        command = command + " -o ColorModel=Gray"
    else:
        command = command + " -o ColorModel=RGB"
    if "Portrait" in angle:
        command += " -o orientation-requested=3"
    else:
        command += " -o orientation-requested=3"#error
    if "True" in  side:
        command += " -o sides=two-sided-long-edge"
    else:
        command += " -o sides=one-sided"

    if ".docx" in file.filename:
        output = pypandoc.convert_file(str(os.getcwd())+"/" +str(file.filename), 'pdf', outputfile= str(os.getcwd())+"/" +str(file.filename[0:-5])+".pdf")
        os.remove(str(os.getcwd())+"/" +str(file.filename))
        file.filename = file.filename[0:-5]+".pdf"

    os.system("lp "+command+" "+str(os.getcwd())+"/" +str(file.filename))
    thename = file.filename
    remove_the_file = threading.Thread(target=remove_after_done,args=(thename,number))
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

@app.route("/drive/download/folder/<foldername>")
def custom_folder_drive_download(foldername):
    cip = str(request.remote_addr) 
    if os.path.exists(os.getcwd()+"//static//drive//"+cip):
        hold = os.listdir(os.getcwd()+"//static//drive//"+cip)
        filenames = []
        rooms = []
        rooms.append(foldername)
        rooms.append("lobby")
        for data in hold:
            if (os.path.isdir(os.getcwd()+"//static//drive//"+cip+"//"+data)):
                if foldername != data:
                    rooms.append(data)
        hold = os.listdir(os.getcwd()+"//static//drive//"+cip+"//"+foldername)
        for data in hold:
            if os.path.isfile(os.getcwd()+"//static//drive//"+cip+"//"+foldername+"//"+data):
                filenames.append(data)
        types = []
        for file in filenames:
            if ".jpg"  in file or ".jpeg"  in file or ".png" in file:
                types.append("image")
            elif ".mp4" in file:
                types.append("video")
            else :
                types.append("unknown")
        
        return render_template("download.html",filenames=filenames,loc = "private_drive",IP= cip,types=types,dataop = rooms)
    else:
        return redirect("/drive/upload")

@app.route("/drive/download")
def fdrive_download():
    cip = str(request.remote_addr) 
    if os.path.exists(os.getcwd()+"//static//drive//"+cip):
        hold = os.listdir(os.getcwd()+"//static//drive//"+cip)
        filenames = []
        rooms = []
        rooms.append("lobby")
        for data in hold:
            if (os.path.isfile(os.getcwd()+"//static//drive//"+cip+"//"+data)):
                filenames.append(data)
            else:
                rooms.append(data)
        types = []
        for file in filenames:
            if ".jpg"  in file or ".jpeg"  in file or ".png" in file:
                types.append("image")
            elif ".mp4" in file:
                types.append("video")
            else :
                types.append("unknown")
        
        return render_template("download.html",filenames=filenames,loc = "private_drive",IP= cip,types=types,dataop = rooms)
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
                roomloc = data.get("roomloc")
                if roomloc == "lobby":
                    shutil.move((os.getcwd()+"//static//drive//"+str(request.remote_addr)+"//"+delete),os.getcwd()+"//static//drive//trash//"+str(request.remote_addr)+"/"+delete)
                else:
                    shutil.move((os.getcwd()+"//static//drive//"+str(request.remote_addr)+"//"+roomloc+"//"+delete),os.getcwd()+"//static//drive//trash//"+str(request.remote_addr)+"/"+delete)
    else:
        if "public_download" in loc:
            shutil.move((os.getcwd()+"//static//uploads//"+deletes),(os.getcwd()+"//static//trash//"+deletes))
        elif "private_drive" in loc:
            roomloc = data.get("roomloc")
            if roomloc == "lobby":
                shutil.move((os.getcwd()+"//static//drive//"+str(request.remote_addr)+"/"+deletes),os.getcwd()+"//static//drive//trash//"+str(request.remote_addr)+"/"+deletes)
            else:
                shutil.move((os.getcwd()+"//static//drive//"+str(request.remote_addr)+"//"+roomloc+"//"+delete),os.getcwd()+"//static//drive//trash//"+str(request.remote_addr)+"/"+delete)
    return jsonify({'status': 'success'}) 

@app.before_request
def limit():
    flag  = info.verify_iden(str(request.remote_addr))
    if flag == False:
        abort(403) 

@app.errorhandler(404)
def http_error_handler(error):
    return render_template('404.html'), 404

@app.errorhandler(403)
def http_error_handler(error):
    ip = request.host_url
    ip = ip_translate(ip,True)+"/password"
    return redirect(ip)



if __name__ == "__main__":
    #ssl_context = 'adhoc'
    #ssl_context=('cert.pem', 'key.pem') port 443 for https
    app.run(host= "0.0.0.0",debug = False,port = 80)
