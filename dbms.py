import mysql.connector, time, threading, random

from datetime import datetime

class dbms:

    def search_video(self,name,cat = None):
        pass # remove for privacy
    
    def recommend_video(self,ip,watching = ""):
        pass # remove for privacy

    def time_delta_calculator(self):
        now = datetime.today()
        delta = now - self.time
        elapsed_minutes = delta.total_seconds() / 60
        return elapsed_minutes
    
    def refresh_exIP(self):
        pass # remove for privacy
    
    def sleep_db(self):
        while True:
            te = self.time_delta_calculator()
            self.refresh_exIP()
            if te >= 5:
                self.exit()
                self.on = False
                return
            else:
                time.sleep(((5-te)*60))

    def getdata(self,cmd):
        if not self.on:
            self.connect()
        with self.lock:
            self.cur.execute(cmd)
            rows = self.cur.fetchall()
        self.time = datetime.today()
        return rows

    def sendata(self, cmd):
        if not self.on:
            self.connect() 
        with self.lock:
            self.cur.execute(cmd)
            self.cnx.commit() 
        self.time = datetime.today()

    def get_ip_from_name(self,name):
        pass # remove for privacy

    def verify_iden(self,ip):
        pass # remove for privacy
        
    def get_uid_from_ip(self,ip):
        pass # remove for privacy
    
    def get_watchTime_video(self,vid_ID,ip):
        pass # remove for privacy

    def update_video_history(self,ip,vid_ID,ct):
        pass # remove for privacy

    def get_name(self, ip):
        pass # remove for privacy
        
    def connect(self):
        self.cnx = mysql.connector.connect(
            host="",
            port=0000,
            user="",
            password="")# multipal info removed for privacy
        
        self.cnx.autocommit = True
        self.cur = self.cnx.cursor()
        self.cur.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")
        self.on = True
        self.time = datetime.today()
        s1 = threading.Thread(target=self.sleep_db)
        s1.start()

    def __init__(self):
        pass # remove for privacy

    def exit(self):
        self.cnx.close()
