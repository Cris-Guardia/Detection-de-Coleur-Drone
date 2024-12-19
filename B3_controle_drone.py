# Importation des bibliothèques nécessaires
import cv2  # Bibliothèque pour le traitement d'images et la capture vidéo
import numpy as np  # Bibliothèque pour les opérations sur les tableaux
from djitellopy import Tello  # Bibliothèque pour le contrôle du drone Tello
import time  # Pour gérer les délais (time.sleep)

# Initialisation de la capture vidéo locale (webcam)
#cap = cv2.VideoCapture(0)  # Utilisation de la caméra locale
cv2.namedWindow('Camera')  # Création d'une fenêtre OpenCV nommée "Camera"

# Initialisation du drone Tello
tello = Tello()  # Création de l'objet Tello
tello.connect()  # Connexion au drone via Wi-Fi
tello.streamon()  # Activation du flux vidéo du drone
frame_read = tello.get_frame_read()  # Récupération du flux vidéo du drone

# Variables globales pour le suivi des couleurs (caméra locale)
color = 100  # Teinte initiale pour la détection en HSV
lo = np.array([color - 5, 100, 50])  # Limite basse de la couleur en HSV
hi = np.array([color + 5, 255, 255])  # Limite haute de la couleur en HSV

enlair = False

# Fonction de rappel pour la souris (sur la caméra locale)
def souris(event, x, y, flags, param):
    global color, lo, hi
    if event == cv2.EVENT_LBUTTONDBLCLK:
        # Capture la valeur de couleur sur un double clic gauche
        color = imageHSV[y, x][0]
        lo[0] = color - 5
        hi[0] = color + 5
        # print("click")
    elif event == cv2.EVENT_LBUTTONDBLCLK:  # Si un double-clic gauche est détecté
        color = image[y, x, 0]  # Récupération de la teinte HSV au pixel cliqué
        lo = np.array([color - 5, 100, 50])  # Mise à jour des limites basse
        hi = np.array([color + 5, 255, 255])  # Mise à jour des limites haute
    elif event == cv2.EVENT_MOUSEWHEEL:
    # Ajuste la couleur avec la molette de la souris
        if flags > 0:
            color += 1
        else:
            color -= 1
        lo[0] = color - 5
        hi[0] = color + 5
    

# Lien de la fonction de souris à la fenêtre OpenCV
cv2.setMouseCallback('Camera', souris)

# Début de la boucle principale
while True:
    # Capture d'une image depuis la caméra locale
    
    # ret, frame_local = cap.read()
    # if not ret:
    #     print("Erreur : Impossible de lire la trame de la caméra locale.")
    #     break

    # Capture d'une image depuis le drone
    frame_drone = frame_read.frame  # Récupération du dernier frame vidéo du drone
    frame_drone=cv2.cvtColor(frame_read.frame, cv2.COLOR_RGB2BGR)
    
    imageHSV = cv2.cvtColor(frame_drone, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(frame_drone, lo, hi)  # Crée un masque pour la couleur choisie
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # Détection des contours de la zone colorée
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        # Trouve le plus grand contour
        c = max(contours, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)

        # if radius > 10:  # Si le rayon est significatif
        #     cv2.circle(frame_drone, (int(x), int(y)), int(radius), (0, 255, 0), 2)  # Dessine un cercle autour
        #     cv2.putText(frame_drone, f"Couleur: {color}", (int(x), int(y) - 10),
        #                 cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    if frame_drone is None:
        print("Erreur : Impossible de lire le flux vidéo du drone.")
        break

    # Dimensions de l'image (les deux flux doivent être affichés au même centre)
    height, width = frame_drone.shape[:2]

    # Ajout du niveau de batterie du drone sur le flux local
    cv2.putText(frame_drone, f"Batterie Drone : {tello.get_battery()}%",
                (width - 250, height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    #frame=cv2.cvtColor(frame_read.frame, cv2.COLOR_RGB2BGR)
    # Ajout des axes bleus (centre de l'image)
    center_x, center_y = width // 2, height // 2  # Coordonnées du centre de l'image
    cv2.line(frame_drone, (center_x, 0), (center_x, height), (255, 0, 0), 2)  # Axe vertical
    cv2.line(frame_drone, (0, center_y), (width, center_y), (255, 0, 0), 2)  # Axe horizontal

    # Conversion en HSV pour le suivi des couleurs (caméra locale)
    image = cv2.cvtColor(frame_drone, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(image, lo, hi)  # Masque binaire pour la couleur sélectionnée
    mask = cv2.erode(mask, None, iterations=1)  # Réduction du bruit par érosion
    mask = cv2.dilate(mask, None, iterations=1)  # Dilatation pour restaurer la forme

    # Recherche des contours dans le masque
    elements = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    if len(elements) > 0:
        # Plus grand contour trouvé
        c = max(elements, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)

        if radius > 10:  # Si le rayon est significatif
            # Dessin d'un cercle jaune autour de l'objet
            cv2.circle(frame_drone, (int(x), int(y)), int(radius), (0, 255, 255), 2)
            # Texte indiquant la position relative et la taille
            text = f"Position: ({int(x - center_x)}, {int(y - center_y)}) | Taille: {int(radius)}"
            cv2.putText(frame_drone, text, (10, height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            cv2.putText(frame_drone, f"Couleur: {color}", (int(x), int(y) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    # Affichage du flux local et du flux du drone
    #cv2.imshow("Coleur", frame_couleur)  # Flux de la caméra locale
    cv2.imshow("Camera", frame_drone)  # Flux vidéo du drone

    # Gestion des entrées clavier
    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # Touche ESC pour quitter
        break
    elif key == 32:  # Barre espace pour faire décoller ou atterrir le drone
        if enlair: # Vérifie si le drone est enlair
            tello.land() # Atterit le drone
            # state = tello.get_current_state()  # Obtiene el estado actual del drone
            # print(state) 
        else:
            # state = tello.get_current_state()  # Obtiene el estado actual del drone
            # print(state) 
            tello.takeoff() # Fait decoler le drone
            tello.send_keepalive()
            enlair = not enlair # Inverse la valeur en enlair

    #AVANT DERRIERE

    elif key == ord('o'): #AVANT
        tello.send_rc_control(0, 50, 0, 0)  
        time.sleep(0.1)  
        tello.send_rc_control(0, 0, 0, 0)  

    elif key == ord('l'): #DERRIERE
        tello.send_rc_control(0, -50, 0, 0)  
        time.sleep(0.1)  
        tello.send_rc_control(0, 0, 0, 0)  
    
    #GAUCHE DROIT

    elif key == ord('k'): #GAUCHE
        # tello.move_left(30)
        tello.send_rc_control(-50, 0, 0, 0)  
        time.sleep(0.1)  
        tello.send_rc_control(0, 0, 0, 0)  

    elif key == ord('m'): #DROIT
        tello.send_rc_control(50, 0, 0, 0)  
        time.sleep(0.1)
        tello.send_rc_control(0, 0, 0, 0) 

    #ASCENDRE DESCENDRE

    elif key == ord('w'): # DESCENDRE
        tello.send_rc_control(0, 0, -50, 0)  
        time.sleep(0.1)  
        tello.send_rc_control(0, 0, 0, 0)  
    elif key == ord('x'): #ASCENDRE
        tello.send_rc_control(0, 0, 50, 0)  
        time.sleep(0.1)  
        tello.send_rc_control(0, 0, 0, 0) 
    
    #ROTATION

    elif key == ord('q'):  # Drone rotation gauche
        tello.send_rc_control(0, 0, 0, -50)
        time.sleep(0.1)  
        tello.send_rc_control(0, 0, 0, 0) 
    elif key == ord('s'):  # Drone rotation droite
        tello.send_rc_control(0, 0, 0, 50)
        time.sleep(0.1)  
        tello.send_rc_control(0, 0, 0, 0) 
    elif key == ord('a'):  # Drone rotation droite
        tello.send_rc_control(0, 0, 0, 0)
        time.sleep(0.1)  
        tello.send_rc_control(0, 0, 0, 0) 

    # Vérification si la fenêtre est fermée (croix)
    if cv2.getWindowProperty("Camera", cv2.WND_PROP_VISIBLE) < 1 : #or \
    #    cv2.getWindowProperty("Drone", cv2.WND_PROP_VISIBLE) < 1:
        break

# Libération des ressources
cap.release()  # Ferme la caméra locale
cv2.destroyAllWindows()  # Ferme toutes les fenêtres OpenCV
tello.streamoff()  # Arrête le flux vidéo du drone
tello.end()  # Termine la connexion avec le drone