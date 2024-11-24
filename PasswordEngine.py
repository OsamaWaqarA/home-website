import os 
from cryptography.fernet import Fernet
class password():
    def gen(self,alt,style):
        import random
        num = [48, 49, 50, 51, 52, 53, 54, 55, 56, 57]
        lc = [97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122]
        uc = [65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90]
        s = [33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,58,59,60,61,62,63,64,91,92,93,94,95,96,123,124,125,126,451,247]
        new = [33,64,35,36,37,94,38,42,46,40,41]
        numl = 0
        strong = style
        lcl = 0
        ucl = 0
        sl = 0
        size = alt
        draft = 0
        word = []
        count = 0
        password = ""
        better = []
        for i in range(0,1000):
            random.shuffle(num)
            random.shuffle(lc)
            random.shuffle(uc)
            if strong == True:
                random.shuffle(s)
            else:   
                random.shuffle(new)

        while True:
            if size >= 5 :
                draft = int(size * 0.2)
                break

        while True:
            better = []
            while True:
                ran = int(random.SystemRandom().randint(1, 4))
                if ran >= 1 and ran <= 4:
                    if ran not in better:
                        better.append(ran)
                if len(better) == 4:
                    break

            for i in range(0,4):
                if better[i] == 1:
                    word.append(num[numl])
                elif better[i] == 2:
                    word.append(lc[lcl])
                elif better[i] == 3:
                    word.append(uc[ucl])
                elif better[i] == 4:
                    if strong == True:
                        word.append(s[sl])
                    else:
                        word.append(new[sl])
                    
            numl += 1
            lcl += 1
            ucl += 1
            sl += 1
            count += 1
            random.shuffle(word)
            if numl >= 9:
                numl = 0
            if lcl >= 25:
                lcl = 0
            if ucl >= 25:
                ucl = 0
            if sl >= 33 and strong == True:
                sl = 0
            if sl >= 10 and strong == False:
                sl = 0
            if count == draft:
                break
            
        count = count * 4


        while True:
            ran = int(random.SystemRandom().randint(0, 1000))
            if (ran >= 33 and ran <= 94) or (ran >= 97 and ran <= 126) or (ran == 451) or (ran == 247):
                word.append(ran)
                count += 1
                random.shuffle(word)
            if count >= size:
                break


        sl = 0
        lcl = 0
        ucl = 0
        numl = 0

        random.shuffle(word)

        while True:
            if (word[0] >= 65 and word[0] <= 90) or (word[0] >= 97 and word[0] <= 122):
                break
            else:
                random.shuffle(word)


        for i in range(0,(size)):
            if (word[i] >= 33 and word[i] <= 47) or (word[i] >= 58 and word[i] <= 64) or (word[i] >= 91 and word[i] <= 96) or (word[i] >= 123 and word[i] <= 126) or (word[i] == 451) or (word[i] == 247):
                sl += 1
            if word[i] >= 97 and word[i] <= 122:
                lcl += 1
            if word[i] >= 65 and word[i] <= 90:
                ucl += 1
            if word[i] >= 48 and word[i] <= 57:
                numl += 1
            password = password+(chr(word[i]))
        return password
    

    def codename(self,name):
        search = ""
        for i in range(0,len(name)):
            search += chr(ord(name[i:i+1])+113)
        search = search + ".txt"
        return search
    
    def decodename(self,name):
        search = ""
        name = name[0:-4]
        for i in range(0,len(name)):
            search += chr(ord(name[i:i+1])-113)
        return search
    
    def decodeit(self,real,f):
        real = real = f.decrypt(real)
        real = real.decode()
        return real

    def codeit(self,real,f):
        real = real.encode()
        real = f.encrypt(real)
        return real
    
    def login(self,user,passcode):
        if os.path.exists(os.getcwd()+"//passwords//"+user):
            username = self.codename(user)
            if os.path.exists(os.getcwd()+"//passwords//"+user+"//"+username):
                with open(os.getcwd()+"//passwords//"+user+"//"+username,"rb") as file:
                    key = file.readline().strip()
                    real = file.readline().strip()
                if passcode == self.decodeit(real,Fernet(key)):
                    return "login"
                else:
                    return "wrong username and password"
                
            else:
                return "file corrupt"
        else:
            return "username error"
        
    def create_account(self,username,passcode,email):
        if os.path.exists(os.getcwd()+"//passwords//"+username):
            return "User All Ready Exists"
        else:
            os.makedirs(os.getcwd()+"//passwords//"+username)#add otp here
            key = Fernet.generate_key()
            f = Fernet(key)
            with open(os.getcwd()+"//passwords//"+username+"//"+(self.codename(username)),"ab") as file:
                file.write(key)
                file.write(b"\n")
                file.write(self.codeit(passcode,f))
                file.write(b"\n")
                file.write(self.codeit(email,f))
            return "acount created"
        
    def make_password(self,username,password_final,name,des):
        key = Fernet.generate_key()
        f = Fernet(key)
        with open(os.getcwd()+"//passwords//"+username+"//"+(self.codename(name)),"ab") as file:
            file.write(key)
            file.write(b"\n")
            file.write((self.codeit(des,f)))
            file.write(b"\n")
            file.write((self.codeit(password_final,f)))
        return "Done"
    
    def read_password(self,username,name):
        with open(os.getcwd()+"//passwords//"+username+"//"+(self.codename(name)),"rb") as file:
            key = file.readline().strip()
            des = file.readline().strip()
            passcode = file.readline().strip()
        f = Fernet(key)
        return self.decodeit(passcode,f) , self.decodeit(des,f)
    
    def del_password(self,username,name):
        if os.path.exists(os.getcwd()+"//passwords//"+username+"//"+(self.codename(name))):
            os.remove(os.getcwd()+"//passwords//"+username+"//"+(self.codename(name)))
            return "Done"
        else:
            return "notDone"
    
        