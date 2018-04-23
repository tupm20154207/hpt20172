import os


class User(object):
    users = {}
    DB = "users/acc.csv"

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.is_active = False
        self.root_dir = "users" + os.sep + "@" + username
        if not os.path.isdir(self.root_dir):
            os.makedirs(self.root_dir)
        User.users[username] = self

    @classmethod
    def login(cls, username, password):
        user = cls.users.get(username)
        if user is not None \
                and user.password == password \
                and not user.is_active:
            user.is_active = True
            return user
        return None

    @classmethod
    def sign_up(cls, username, password):
        if cls.users.get(username) is None:
            new_acc = cls(username, password)
            cls.store_users()
            return new_acc
        return None

    @classmethod
    def load_users(cls):
        with open(cls.DB, "r") as f:
            for line in f.readlines():
                info = line[:-1].split(';')
                cls(info[0], info[1])

    @classmethod
    def store_users(cls):
        with open(cls.DB, "w") as f:
            for user in cls.users:
                f.write(user + ';' + cls.users[user].password + '\n')

    def log_out(self):
        self.is_active = False
