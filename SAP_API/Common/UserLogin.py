from dataclasses import dataclass

@dataclass
class UserLogin:
    def __init__(self, user = None, password = None) -> None:
        self.isAnonymous = user == None  and password == None

        if(not self.isAnonymous):
            self.user = user 
            self.password = password