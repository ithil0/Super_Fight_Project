import requests #para la realización de llamadas a la API
import random 
import math
from collections import Counter
import time

class Personaje:
    def __init__(self, intelligence, strength,speed,durability,power,combat,fb,name, img): 
        self.name = name
        self.img = img
        self.sta = random.choice(range(0,11)) # actual stamina
        self.fb = fb
        self.intel = math.floor(((2 * intelligence + self.sta)/1.1)*self.fb) #fb es el Filiation Coefficient
        self.st = math.floor(((2 * strength + self.sta)/1.1)*self.fb)
        self.sp = math.floor(((2 * speed + self.sta)/1.1)*self.fb)
        self.dur = math.floor(((2 * durability + self.sta)/1.1)*self.fb)
        self.pow = math.floor(((2 * power + self.sta)/1.1)*self.fb)
        self.com = math.floor(((2 * combat + self.sta)/1.1)*self.fb)   
        self.hp = math.floor((self.st*0.8 + self.dur*0.7 + self.pow)/2 * (1 + (self.sta/10))) + 100 

    def atack(self): #retorna un ataque aleatorio entre los 3 disponibles
        self.mental = round((self.intel*0.7 + self.sp*0.2 + self.com*0.1) * self.fb)
        self.strong = round((self.st*0.6 + self.pow*0.2 + self.com*0.2) * self.fb)
        self.fast = round((self.sp*0.55 + self.dur*0.25 + self.st*0.2) * self.fb)
        self.rand_atack = random.choice(['mental','strong','fast'])
        if(self.rand_atack == 'mental'):
            return 'mental', self.mental
        elif(self.rand_atack == 'strong'):
            return 'strong', self.strong
        else:
            return 'fast', self.fast

def fb(alignment, team):
    if(alignment==team):
        return (1 + random.choice(range(0,10)))
    else:
        return (1/(1 + random.choice(range(0,10))))

def crear_personajes():
    ids = []
    personajes = []
    alignments = []    
    while len(ids)<10:        
        i = random.choice(range(1,732))
        if(i in ids):
            continue
        request_biography = requests.get(f"https://akabab.github.io/superhero-api/api/biography/{i}.json")
        if(request_biography.status_code==200):
            alignment = request_biography.json()['alignment']
            alignments.append(alignment)            
            ids.append(i)    
    team1_alignment, _= Counter(alignments[:5]).most_common(1)[0] 
    team2_alignment, _= Counter(alignments[5:]).most_common(1)[0]
    for id in ids:       
        request_data = requests.get(f"https://akabab.github.io/superhero-api/api/id/{id}.json")   
        name = request_data.json()['name']      
        intelligence, strength,speed,durability,power,combat = list(request_data.json()['powerstats'].values())  
        img = list(request_data.json()['images'].values())[0]
        index = ids.index(id)        
        if(index <= 4):
            f = fb(alignments[index],team1_alignment)
        else:
            f = fb(alignments[index],team2_alignment)
        p = Personaje(intelligence, strength,speed,durability,power,combat,f,name,img)
        personajes.append(p)         
    return personajes

def imprimir_tablero(personajes):
    data = [[' Equipo 1 ', 'Puntos de vida',' Equipo 2 ', 'Puntos de vida']]
    for i in range(5):        
        datos = [str(i+1)+'-. ' + personajes[i].name, ' HP: '+str(personajes[i].hp), str(i+6)+'-. ' + personajes[i+5].name, ' HP: '+str(personajes[i+5].hp)]   
        data.append(datos)
    col_width = max(len(word) for row in data for word in row) + 2  # padding    
    for row in data:
        print("".join(word.ljust(col_width) for word in row))

def post_mail(nombre, mail, texto):
	return requests.post(
		"https://api.mailgun.net/v3/sandboxb36bb597e2ca405999bb38bd6517d295.mailgun.org/messages",
		auth=("api", "7412e3a2e5d9d5669fb1135e03cf75bf-f2340574-279b1ed0"),
		data={"from": "Mailgun Sandbox <postmaster@sandboxb36bb597e2ca405999bb38bd6517d295.mailgun.org>",
			"to": f"{nombre} <{mail}>",
			"subject": "Resultados Super Fight",			
            "html": f'{texto}'})

def main():
    print("Bienvenido a Super Fight, la batalla entre superhéroes y supervillanos.\n")
    while True:
        iniciar = input('Deseas comenzar una pelea?\n1-. Si\n2-.No\n')    
        if(iniciar not in ['1','Si','si','Sí','sí','2','No','no']):
            print("Debes ingresar una opción válida.")
        else:
            break
    if(iniciar in ['1','Si','si','Sí','sí']):        
        nombre = input("Genial! Ingresa tu nombre:\n")
        mail = input(f"Hola {nombre}, por favor ingresa tu email para enviarte el resultado de esta batalla:\n")        
        personajes = crear_personajes()    
        texto = f'Hola {nombre}! Este es un resumen de la batalla:<br>El equipo 1 estuvo compuesto por: {personajes[0].name} (HP: {personajes[0].hp}), {personajes[1].name} (HP: {personajes[1].hp}), {personajes[2].name} (HP: {personajes[2].hp}), {personajes[3].name} (HP: {personajes[3].hp}) y {personajes[4].name} (HP: {personajes[4].hp})<br>El equipo 2 estuvo compuesto por: {personajes[5].name} (HP: {personajes[5].hp}), {personajes[6].name} (HP: {personajes[6].hp}), {personajes[7].name} (HP: {personajes[7].hp}), {personajes[8].name} (HP: {personajes[8].hp}) y {personajes[9].name} (HP: {personajes[9].hp})<br>'
        print("Estos son los equipos luchadores:\n")
        imprimir_tablero(personajes)  
        juego=True
        soldado_caido1 = -1
        soldado_caido2 = -1
        while(juego==True):  
            if(soldado_caido1==4 and soldado_caido2>0):
                print("El equipo 2 ha ganado la batalla!\n")
                imprimir_tablero(personajes)
                print("Adiós")
                texto = texto + '<b>Vencedores absolutos: Equipo 2</b>'
                post_mail(nombre, mail, texto)
                break
            elif(soldado_caido2==4 and soldado_caido1>0) :
                print("El equipo 1 ha ganado la batalla!\n")
                imprimir_tablero(personajes)
                print("Adiós")
                texto = texto + '<b>Vencedores absolutos: Equipo 1</b>'
                post_mail(nombre, mail, texto)
                break
            elif(soldado_caido1 == 0 and soldado_caido2 == 0):
                print("Ambos equipos han perdido!\n")
                imprimir_tablero(personajes)
                print("Adiós")
                texto = texto + '<b>Vencedores absolutos: Ambos equipos perdieron</b>'
                post_mail(nombre, mail, texto)
                break
            while True:
                luchador1 = input('Ingresa un número del 1 al 5 para elegir al representante del equipo 1 en esta lucha.\n')    
                if(luchador1 not in map(str,range(1,6))):
                    print("Debes ingresar una opción válida.\n")                  
                else:
                    if(personajes[int(luchador1)-1].hp==0):
                        print("Este personaje agotó su HP. Elige a un personaje que aún tenga puntos de vida para poder pelear.\n")
                    else:
                        break
            while True:
                luchador2 = input('Ingresa un número del 6 al 10 para elegir al representante del equipo 2 en esta lucha.\n')    
                if(luchador2 not in map(str,range(6,11))):
                    print("Debes ingresar una opción válida.\n")                  
                else:
                    if(personajes[int(luchador2)-1].hp==0):
                        print("Este personaje agotó su HP. Elige a un personaje que aún tenga puntos de vida para poder pelear.\n")
                    else:
                        break
            name1 = personajes[int(luchador1)-1].name
            name2 = personajes[int(luchador2)-1].name
            while True:                          
                ataque1, points1 = personajes[int(luchador1)-1].atack()
                ataque2, points2 = personajes[int(luchador2)-1].atack()
                print("El ataque random de "+name1+ " es de tipo "+ataque1+" de "+str(points1)+" puntos." )      
                print("El ataque random de "+name2+ " es de tipo "+ataque2+" de "+str(points2)+" puntos." )  
                aux1 = personajes[int(luchador1)-1].hp
                aux2 = personajes[int(luchador2)-1].hp   
                personajes[int(luchador2)-1].hp = aux2 - points1
                personajes[int(luchador1)-1].hp = aux1 - points2 
                time.sleep(1)
                print("Ambos personajes han hecho sus ataques!")
                hp1=personajes[int(luchador1)-1].hp
                hp2=personajes[int(luchador2)-1].hp
                if(hp1>0 and hp2>0):
                    imprimir_tablero(personajes)
                    print(name1+" ha quedado con "+str(hp1)+ " HP.")
                    print(name2+" ha quedado con "+str(hp2)+ " HP.")
                    print("<----- To be continued")
                    continue
                elif(hp1>0 and hp2<=0):
                    personajes[int(luchador2)-1].hp=0
                    hp2=0
                    soldado_caido2+=1
                    imprimir_tablero(personajes)
                    print(name1+" ha quedado con "+str(hp1)+ " HP.")
                    print(name2+" ha quedado con "+str(hp2)+ " HP.")
                    print(name1+" ha ganado esta pelea.")
                    texto = texto + f'Pelea entre {name1} y {name2}. Ganadxr--> {name1}<br>'
                    break
                elif(hp2>0 and hp1<=0):
                    personajes[int(luchador1)-1].hp=0
                    hp1=0
                    soldado_caido1+=1
                    imprimir_tablero(personajes)
                    print(name1+" ha quedado con "+str(hp1)+ " HP.")
                    print(name2+" ha quedado con "+str(hp2)+ " HP.")
                    print(name2+" ha ganado esta pelea.")
                    texto = texto + f'Pelea entre {name1} y {name2}. Ganadxr--> {name2}<br>'
                    break
                elif(hp2<=0 and hp1<=0):
                    personajes[int(luchador1)-1].hp=0
                    hp1=0
                    personajes[int(luchador2)-1].hp=0
                    hp2=0
                    soldado_caido1+=1
                    soldado_caido2+=1
                    imprimir_tablero(personajes)
                    print("Ambos personajes han quedado con 0 HP.")
                    texto = texto + f'Pelea entre {name1} y {name2}. Ambos perdieron todo su HP<br>'
                    break     
                  
    else:
        print("Adiós")
main()



