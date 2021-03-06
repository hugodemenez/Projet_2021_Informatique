
from seleniumwire import webdriver
from time import sleep
import json
import re
from selenium.webdriver.firefox.options import Options
class scraping():
    """
    Cette classe regroupe les differentes fonctions de scraping utilisées pour récuperer les données de WebAurion
    """
    def __init__(self):
        #On initialise le headless webbrowser
        options = Options()
        options.headless = True
        profile = webdriver.FirefoxProfile()
        #On met la langue en français pour pouvoir reconnaitre les élements comme "Mon Planning" ou "Mes Notes"
        profile.set_preference('intl.accept_languages', 'fr-FR, fr')
        self.driver = webdriver.Firefox(options=options,firefox_profile=profile)
        

    def get_planning(self,username,password):
        """
        Cette fonction sert à récuperer une liste des différents cours sous forme de dictionnaires avec :
        dictionnaire["salle"],
        dictionnaire["professeur"],
        dictionnaire["debut"],
        dictionnaire["fin"],
        dictionnaire["cours"]
        """


        #Ouverture de la page de connexion aurion
        self.driver.get('https://aurion.junia.com/faces/Login.xhtml')
        
        #Remplissage du nom utilisateur
        inputElement = self.driver.find_element_by_id("username")
        inputElement.send_keys(username)

        #Remplissage du mot de passe
        inputElement = self.driver.find_element_by_id("password")
        inputElement.send_keys(password)

        #Validation des données d'identification
        inputElement.submit() 
        
        #Recherche de la zone pour acceder au planning
        counter=0
        print("Recherche du planning")
        while(True):
            try:
                
                inputElement =self.driver.find_element_by_link_text("Mon Planning")
                print("Planning trouvé")
                #Une fois la zone selectionnée : on clique dessus
                inputElement.click()
                break
            except:
                sleep(1)
                if counter == 10:
                    self.driver.quit()
                    #Au bout de 10 secondes sans trouver l'element "Mon Planning", on considère que la connexion a échoué
                    raise Exception("Impossible de charger l'emploi du temps")
                counter+=1
                pass
        
        #On se déplace sur la page d'accueil pour être sûr de ne pas figer le headless webbrowser
        self.driver.get('https://aurion.junia.com/')

        #Recupération de la requete du planning
        counter=0
        print("En attente de la réponse du serveur Aurion")
        while(True):
            try:
                #On accède aux requetes envoyées par le HeadlessWebbrowser
                for request in self.driver.requests:
                    #S'il y a une reponse
                    if request.response:
                        #On verifie que la reponse correspond bien au planning
                        if 'Planning' in request.url :
                            if 'POST' in request.method:
                                response = request.response.body
                                #On met la reponse au format texte afin de pouvoir la traiter
                                response=str(response)
                #On verifie si la reponse existe (sinon cela lève une exception)
                response
                break
            except Exception as error:
                if counter>10:
                    self.driver.quit()
                    #Au bout de 10 secondes si nous n'avons pas trouvé la requête correspondant au planning alors on considère que cela a échoué
                    raise Exception("Impossible de récuperer le planning")
                counter +=1
                sleep(1)
        

        
        #On met en forme la reponse pour pouvoir créer une liste de dictionnaires
        response = response[response.find('events')+11:].strip()
        response = response[:response.find(']}]]')].strip()
        response = response+','
        response = response.split("{")

        
        #On initialise la liste
        data=[]

        for elem in response:
            try:
                if elem !='':
                    #On remet en forme le string pour être traduit en dictionnaire
                    string_dict = '{'+elem
                    string_dict=string_dict[:-1]
                    
                    #On remplace les caractères speciaux afin de ne pas avoir d'erreur
                    string_dict=string_dict.replace("\\xc3\\xa9", "e")
                    string_dict=string_dict.replace("\\xc3\\xa8", "e")
                    string_dict=string_dict.replace(r"\'", "'")
                    string_dict=string_dict.replace(r"\\n\\n", r"\\n")
                    
                    #On traduit le string en dictionnaire
                    dict=json.loads(string_dict)
                    #On initialise le dictionnaire à renvoyer
                    dictionnaire={}
                    #On traite les infos pour récuperer ce qui nous interesse
                    titre = re.split(r"\\n",dict["title"])

                    salle = titre[0]
                    cours = titre[1]
                    professeur = titre[-1]

                    #pour les fichiers csv
                    date_debut= re.sub("[-]",'/', re.search("[0-9-]+[0-9]+",dict["start"]).group())

                    heure_debut=re.search("[0-9:]{5}",dict["start"]).group()

                    date_fin=re.sub("[-]",'/', re.search("[0-9-]+[0-9]+",dict["end"]).group())

                    heure_fin=re.search("[0-9:]{5}",dict["end"]).group()

                    #Mise en forme pour l'api google agenda 
                    heure_et_jour_debut = date_debut + 'T' + heure_debut + ':00+02:00'
                    heure_et_jour_fin = date_fin + 'T' + heure_fin + ':00+02:00'



                    #On reformule le dictionnaire avec les informations classées
                    dictionnaire["salle"]=salle
                    dictionnaire["professeur"] = professeur
  
                    dictionnaire["date_debut"] = date_debut
                    dictionnaire["heure_debut"] = heure_debut
                    dictionnaire["date_fin"] = date_fin
                    dictionnaire["heure_fin"] = heure_fin
                    dictionnaire["cours"] = cours
                    dictionnaire["date_google_api_debut"] = heure_et_jour_debut.replace('/','-')
                    dictionnaire["date_google_api_fin"] = heure_et_jour_fin.replace('/','-')
                    #On ajoute le dictionnaire à la liste qui contient les differents cours de la semaine
                    data.append(dictionnaire)
            except Exception as error:
                
                print(error)
                pass
        self.driver.quit()

        return data

    def get_marks(self,username,password):

        #Ouverture de la page de connexion aurion
        self.driver.get('https://aurion.junia.com/faces/Login.xhtml')

        #Remplissage du nom utilisateur
        inputElement = self.driver.find_element_by_id("username")
        inputElement.send_keys(username)

        #Remplissage du mot de passe
        inputElement = self.driver.find_element_by_id("password")
        inputElement.send_keys(password)

        #Validation des données d'identification
        inputElement.submit() 
        

        #Recherche de la zone pour acceder à la zone scolarité
        counter=0
        print("Recherche de la scolarité")
        while(True):
            
            try:
                inputElement =self.driver.find_element_by_link_text("Scolarité")
                break
            except:
                sleep(1)
                if counter == 10:
                    #Si au bout de 10 secondes nous n'avons pas trouvé la zone "Scolarité" alors on considère que la connexion a échoué
                    raise Exception("Impossible de trouver la scolarité")
                counter+=1
                pass

        #Une fois la zone selectionnée : on clique dessus
        inputElement.click() 

        #Recherche de la zone pour acceder aux notes
        counter=0
        print("Recherche des notes")
        while(True):
            
            try:
                inputElement =self.driver.find_element_by_link_text("Mes notes")
                break
            except:
                sleep(1)
                if counter == 10:
                    #Si au bout de 10 secondes nous n'avons pas trouvé les notes, on considère que cela a échoué
                    raise Exception("Impossible de charger les notes")
                counter+=1
                pass

        #Une fois la zone selectionnée : on clique dessus
        inputElement.click() 

        #On attends que les requetes soient toutes soumises
        sleep(5)

        #On accède aux requetes envoyées par le HeadlessWebbrowser
        for request in self.driver.requests:
            #S'il y a une reponse
            if request.response:
                #On verifie que la reponse correspond bien au planning
                if 'Notation' in request.url :
                    if 'GET' in request.method:
                        response = request.response.body
                        response=str(response)

        
        #On met en forme la reponse pour pouvoir créer une liste de dictionnaires

        #On recupere le contenu du body
        response = response[response.find('</thead>'):].strip()
        response = response[:response.find('</tbody>')].strip()
            #On recupere seulement le texte present dans le body (on retire les balises)
        response = re.sub('<[^>]+>', '', response)

        #On retire les caractères spéciaux
        response=response.replace(r"\xc3\xa8", "e") 
        response=response.replace(r"\xc3\xa9", "e") 
        response=response.replace(r"\xc2\xb0", "O")
        response=response.replace(r"\xc3\xb4", "o")
        response=response.replace(r"\xc3\xa7", "c")
        response=response.replace(r"\'", "'")

        #On decoupe les resultats à chaque fois que l'on dispose d'une date sous la forme : D/M/Y
        responses = re.split(r'(\d{2}/\d{2}/\d{4})', response)
        

        notes = []
        for position in range (len(responses)-1):
            try:
                date=responses[position]
                #On recupère la note et l'intitulé de la matère
                note = re.search("[0-9]{1,2}[.][0-9]{2}",responses[position+1]).group()
                if float(note)>20:
                    note = note[1:]
                

                matiere = re.sub("[a-z]+",'',responses[position+1].split(' ', 1)[0])[:-1]
                
                #On ajoute le dictionnaire dans une liste que l'on renvoit par la suite
                notes.append({'title':matiere,'mark':note,'date':date})
                position+=2
            except:
                pass
        

        self.driver.quit()

        return notes

    def check_connection(self,username,password):
        """Renvoie Vrai si la connexion est établie, sinon Faux"""
        #Ouverture de la page de connexion aurion
        self.driver.get('https://aurion.junia.com/faces/Login.xhtml')

        #Remplissage du nom utilisateur
        inputElement = self.driver.find_element_by_id("username")
        inputElement.send_keys(username)

        #Remplissage du mot de passe
        inputElement = self.driver.find_element_by_id("password")
        inputElement.send_keys(password)

        #Validation des données d'identification
        inputElement.submit() 
        counter = 0
        while(True):
            try :
                counter += 1
                #Fonction permettant de reconnaitre la partie du code html indiquant que la connexion a échoué
                self.driver.find_element_by_xpath("//*[contains(text(),'invalide')]")
                self.driver.quit()
                return False
            except:
                if counter >5:
                    #Au bout de 5 secondes si on ne trouve pas l'information concernant l'echec de la connexion, on considère que la connexion est établie
                    self.driver.quit()
                    return True
                sleep(1)


if __name__ == "__main__":
    pass