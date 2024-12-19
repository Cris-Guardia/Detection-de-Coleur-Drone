# connectez-vous sur le reseau Wifi de votre drone : Tello-XXXXXX
# executez ensuite le code suivant

from djitellopy import Tello #Importation de l'object tello depuis la bibiliotheque djitellopy
import cv2 # importation de la bibliothéque openCV comme cv2
import time

tello = Tello() # Initialization de l'object tello via son contructeur
tello.connect() # Connection  le drone via Wi-fi
tello.streamon() # Instruction permetant d'établir la transmission vidéo avec le drone
frame_read = tello.get_frame_read() # La fonction tello.get_frame_read() retorune l'object BackgroundFrameRead
                                    # qui permet de lire les frames tranmis par le drone et les stocke au frame_read
titreFenetre = "Acquisition du flux video du drone Tello" #Definit un titre par la fenetre
enlair = False # Variable boolenne qui indique si le drone est en l'aire o non

img = frame_read.frame # Obtien le dernier frame transmit par le drone
height, width = img.shape[:2] # img.shape[:2] fournit les dimension de l'image heigh represente la hauteur et width la largeur

while True: # Boucle infinie pour afficher, pendant une durée indétérminée, les images captées par le drone
    img = frame_read.frame # Obtien le dernier frame de la caméra du drone et le stocke dans img
    cv2.putText(img, "La taille de l'image est {}x{}.".format(width,height), (10, height-20), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)
    # cv2.putText ajoute du texte sur l'image reçue du drone en utilisant 8 paramètres
    # 1) img est l'image à mettre
    # 2) "La taille de l'image est {}x{}." est le texte à mettre, .format(width,height) etabli les dimension
    # 3) (10, height-20) : les coordones (x, y) du texte dans l'image
    # 4) cv2.FONT_HERSHEY_DUPLEX la typographie du texte
    # 5) 1 la taille du texte
    # 6) (255, 255, 255) la couleur du texte (Blanc)
    # 7) 1 l'épaisseur du lignes du texte
    # 8) cv2.LINE_AA le type de ligne pour le texte

    cv2.putText(img, "niv. batterie:{}%".format(tello.get_battery()), (width-300, 50), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255), 1, cv2.LINE_AA)
    # cv2.putText ajoute du texte sur l'image reçue du drone en utilisant 8 paramètres
    # 1) img est l'image à mettre
    # 2) "niv. batterie:{}%" est le texte à mettre .format(tello.get_battery()) instert le pourcentage de batterie du drone
    # 3) (width-300, 50) : les coordones (x, y) du texte dans l'image
    # 4) cv2.FONT_HERSHEY_DUPLEX la typographie du texte
    # 5) 1 la taille du texte
    # 6) (0, 0, 255) la couleur du texte (Rouge)
    # 7) 1 l'épaisseur du lignes du texte
    # 8) cv2.LINE_AA le type de ligne pour le texte

    cv2.imshow(titreFenetre, img) # Affiche une fenêtre avec le titre titreFenetre et l'image img
    key = cv2.waitKey(1) & 0xFF # key = cv2.waitKey(1) verifie a chaque miliseconde si une touche a été pressée et le stocke au key
    if key == 27: # Vérifie si la touche pressé est la touche ESC
        break # Sort de la boucle infini

    elif key == 32: # Vérifie si la touche pressé est la touche Space
        if enlair: # Vérifie si le drone est enlair
            tello.land() # Atterit le drone
            # state = tello.get_current_state()  # Obtiene el estado actual del drone
            # print(state) 
        else:
            # state = tello.get_current_state()  # Obtiene el estado actual del drone
            # print(state) 
            tello.takeoff() # Fait decoler le drone
        enlair = not enlair # Inverse la valeur en enlair

    #AVANT DERRIERE

    elif key == ord('o'): #AVANT
        tello.send_rc_control(0, 20, 0, 0)  
        time.sleep(0.1)  
        tello.send_rc_control(0, 0, 0, 0)  

    elif key == ord('l'): #DERRIERE
        tello.send_rc_control(0, -20, 0, 0)  
        time.sleep(0.1)  
        tello.send_rc_control(0, 0, 0, 0)  
    
    #GAUCHE DROIT

    elif key == ord('k'): #GAUCHE
        # tello.move_left(30)
        tello.send_rc_control(-30, 0, 0, 0)  
        time.sleep(0.1)  
        tello.send_rc_control(0, 0, 0, 0)  

    elif key == ord('m'): #DROIT
        tello.send_rc_control(30, 0, 0, 0)  
        time.sleep(0.1)
        tello.send_rc_control(0, 0, 0, 0) 

    #ASCENDRE DESCENDRE

    elif key == ord('w'): # DESCENDRE
        tello.send_rc_control(0, 0, -30, 0)  
        time.sleep(0.1)  
        tello.send_rc_control(0, 0, 0, 0)  
    elif key == ord('x'): #ASCENDRE
        tello.send_rc_control(0, 0, 30, 0)  
        time.sleep(0.1)  
        tello.send_rc_control(0, 0, 0, 0)  
    
    #ROTATION

    elif key == ord('s'): # 
        tello.send_rc_control(0, 0, 0, 40)  
        time.sleep(0.1)  
        tello.send_rc_control(0, 0, 0, 0)  
    elif key == ord('q'): #
        tello.send_rc_control(0, 0, 0, -40)  
        time.sleep(0.1)  
        tello.send_rc_control(0, 0, 0, 0)  


    if cv2.getWindowProperty(titreFenetre, cv2.WND_PROP_VISIBLE)<1 :
        # cv2.getWindowProperty recupère les propietes d'une fenêtre
        # titreFenetre est le titre de cette fenêtre, cv2.WND_PROP_VISIBLE indique si la fenêtre et visible o non
        # if cv2.getWindowProperty(titreFenetre, cv2.WND_PROP_VISIBLE)<1 : vérifie donc si la fenêtre est encore ouvert
        break # Sort de la boucle infinie

tello.streamoff() # Coupe la transmision de vidéo
cv2.destroyAllWindows() # Ferme toutes les fenêtres ouvertes par openCV
tello.end() # Termine la conection avec le drone
