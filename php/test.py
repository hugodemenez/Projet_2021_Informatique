import sys,sqlite3,os
from webscraping import scraping
username = sys.argv[1]
password = sys.argv[2]
email =sys.argv[3]
niveau = sys.argv[4]
specialite = sys.argv[5]


if scraping().check_connection(username,password):
    path = "db/database.db"
    if os.path.isfile(path):
        connexion = sqlite3.connect(path)
        cursor = connexion.cursor()
        #Add user to user table :
        users=[{
        'username' : username,
        'password' : password,
        'email' : email,
        }]

        for user in users:
            parametres = (user['username'],user['password'],user['email'])
            command = "INSERT OR REPLACE INTO user VALUES (?,?,?)"
            cursor.execute(command,parametres)
            connexion.commit()
        cursor.execute("SELECT * FROM user")
        print("ok")

else:
    print("NONE")