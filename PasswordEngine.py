import os, random
from cryptography.fernet import Fernet
class password():
    
    def gen(self,full_size,style,p_number = 20,p_lower_case = 20,p_upper_case = 20,p_symbol = 20):#Stype True is full and False is limited
        
        number = [48, 49, 50, 51, 52, 53, 54, 55, 56, 57]
        Full_symbol = [33,35,36,37,38,40,41,42,43,44,45,46,47,58,59,60,61,62,63,64,91,92,93,94,95,96,123,124,125,126,451,247]
        limited_symbol = [33,64,35,36,37,38,42,46,40,41]

        if style:
            symbol = Full_symbol
        else:
            symbol = limited_symbol

        num_size = int(full_size * (p_number/100))
        symbol_size = int(full_size * (p_symbol/100))
        lower_case_size = int(full_size * (p_lower_case/100))
        upper_case_size = int(full_size * (p_upper_case/100))
        password_list = []

        if num_size < len(number) and num_size > 0:
            for i in range(0,len(number)):
                random.shuffle(number)
        
        if symbol_size < len(symbol) and symbol_size > 0:
            for i in range(0,len(symbol)):
                random.shuffle(symbol)

        counter = 0
        for i in range(0,num_size):
            password_list.append(number[counter])
            counter += 1
            if counter >= len(number):
                counter = 0

        random.shuffle(password_list)

        counter = 0
        for i in range(0,symbol_size):
            password_list.append(symbol[counter])
            counter += 1
            if counter >= len(symbol):
                counter = 0

        random.shuffle(password_list)

        alfa_list = set()
        for i in range(0,upper_case_size):
            while True:
                ran = random.randint(65,91)
                if len(alfa_list) >= 26 or ran not in alfa_list:
                    break
            alfa_list.add(ran)  

        password_list.extend(alfa_list)
        random.shuffle(password_list)

        alfa_list = set()
        for i in range(0,lower_case_size):
            while True:
                ran = random.randint(97,123) 
                if len(alfa_list) >= 26 or ran not in alfa_list:
                    break
            alfa_list.add(ran)  

        password_list.extend(alfa_list)
        random.shuffle(password_list)

        if len(password_list) < full_size:
            for i in range(0,(full_size-len(password_list))):
                while True:
                    ran = random.randint(33,451)
                    if ran in symbol or ran in number or (ran >= 65 and ran <= 91) or (ran >= 97 and ran <= 123):
                        break
                password_list.append(ran)

        while True:
            if (password_list[0] >= 65 and password_list[0] <= 91) or (password_list[0] >= 97 and password_list[0] <= 123) or lower_case_size + upper_case_size == 0:
                break
            random.shuffle(password_list)

        password = "".join(chr(string) for string in password_list)

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
    
        
