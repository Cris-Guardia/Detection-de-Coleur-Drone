import cv2  # Bibliothèque pour le traitement d'images et la capture vidéo
import numpy as np  # Bibliothèque pour les opérations sur les tableaux
from djitellopy import Tello  # Bibliothèque pour le contrôle du drone Tello
import time  # Pour gérer les délais (time.sleep)

# Initialisation de la fenêtre OpenCV
cv2.namedWindow('Camera')  # Création d'une fenêtre OpenCV nommée "Camera"

# Initialisation du drone Tello
tello = Tello()  # Création d'un objet Tello
try:
    tello.connect()  # Connexion au drone
    tello.streamon()  # Activation du flux vidéo
    frame_read = tello.get_frame_read()  # Récupération du flux vidéo
    print("Drone connecté avec succès !")
except Exception as e:
    print(f"Erreur lors de la connexion au drone : {e}")
    exit()

# Variables globales pour le suivi des couleurs
color = 100  # Teinte initiale pour la détection en HSV
lo = np.array([color - 5, 100, 50])  # Limite basse de la couleur en HSV
hi = np.array([color + 5, 255, 255])  # Limite haute de la couleur en HSV

# Variables pour le contrôle proportionnel
Kp = 0.1  # Gain proportionnel

# Variables pour le déplacement gauche-droite
deplacement = "droite"  # Direction initiale du mouvement
vitesse_laterale = 10  # Vitesse de déplacement latéral
duree_deplacement = 0.2  # Durée d'un déplacement latéral en secondes
faire_correction = False

# Fonction de rappel pour la souris
def souris(event, x, y, flags, param):
    global color, lo, hi, imageHSV
    if event == cv2.EVENT_LBUTTONDBLCLK:
        color = imageHSV[y, x][0]
        lo[0] = color - 5
        hi[0] = color + 5

# Liaison de la fonction souris à la fenêtre OpenCV
cv2.setMouseCallback('Camera', souris)

# Début de la boucle principale
while True:
    try:
        # Capture d'une image depuis le drone
        frame_read = tello.get_frame_read()
        frame_drone = frame_read.frame  # Récupération de la dernière image
        frame_drone = cv2.cvtColor(frame_drone, cv2.COLOR_RGB2BGR)  # Conversion RGB en BGR

        # Conversion en HSV
        imageHSV = cv2.cvtColor(frame_drone, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(imageHSV, lo, hi)  # Crée un masque pour la couleur choisie
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        # Dimensions de l'image
        height, width = frame_drone.shape[:2]
        center_x = width // 2

        # Ajout d'une ligne pour indiquer le centre
        cv2.line(frame_drone, (center_x, 0), (center_x, height), (255, 0, 0), 2)

        # Initialisation de l'erreur et de la correction
        erreur = 0
        correction = 0

        # Détection des contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            # Trouver le plus grand contour
            c = max(contours, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)

            if radius > 10:  # Si le rayon est significatif
                cv2.circle(frame_drone, (int(x), int(y)), int(radius), (0, 255, 0), 2)

                # Calcul de l'erreur et de la correction
                erreur = int(x - center_x)
                correction = int(Kp * erreur)

                # Envoi de la commande au drone
                if faire_correction:
                    tello.send_rc_control(0, 0, 0, correction)

                # Affichage des informations
                cv2.putText(frame_drone, f"Erreur: {erreur} | Correction: {correction}",
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Affichage du gain proportionnel
        cv2.putText(frame_drone, f"Kp: {Kp:.2f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        cv2.putText(frame_drone, f"Batterie Drone : {tello.get_battery()}%",
                (width - 250, height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    except Exception as e:
        print(f"Erreur dans la boucle principale : {e}")
        break
    
    if erreur == 0:
        faire_correction = False

    # Gestion du déplacement gauche-droite
    if faire_correction: 
        if deplacement == "droite":
            tello.send_rc_control(-vitesse_laterale, 0, 0, correction)
        else:
            tello.send_rc_control(vitesse_laterale, 0, 0, correction)

    time.sleep(duree_deplacement)
    tello.send_rc_control(0, 0, 0, 0)

    # Inversion de la direction
    deplacement = "gauche" if deplacement == "droite" else "droite"

    # Affichage du flux vidéo
    cv2.imshow("Camera", frame_drone)

    # Gestion des entrées clavier
    key = cv2.waitKey(10) & 0xFF
    if key == 27:  # Touche ESC pour quitter
        break
    elif key == 32:  # Barre espace pour décoller ou atterrir
        if tello.is_flying:
            tello.land()
        else:
            tello.takeoff()

    # Ajustement du gain proportionnel
    elif key == ord('+'):
        Kp += 0.01
        vitesse_laterale = 10

    elif key == ord('-'):
        Kp -= 0.01
        vitesse_laterale = -10

    #MOVEMENT MANUEL DU DRONE

    #AVANT DERRIERE

    elif key == ord('o'): #AVANT
        tello.send_rc_control(0, 50, 0, 0)  
        tello.send_rc_control(0, 0, 0, 0)  

    elif key == ord('l'): #DERRIERE
        tello.send_rc_control(0, -50, 0, 0)  
        tello.send_rc_control(0, 0, 0, 0)  
    
    #GAUCHE DROIT

    elif key == ord('k'): #GAUCHE
        tello.send_rc_control(-50, 0, 0, 0)  
        tello.send_rc_control(0, 0, 0, 0)  

    elif key == ord('m'): #DROIT
        tello.send_rc_control(50, 0, 0, 0)  
        tello.send_rc_control(0, 0, 0, 0) 

    #ASCENDRE DESCENDRE

    elif key == ord('w'): # DESCENDRE
        tello.send_rc_control(0, 0, -50, 0)  
        tello.send_rc_control(0, 0, 0, 0)  
    
    elif key == ord('x'): #ASCENDRE
        tello.send_rc_control(0, 0, 50, 0)  
        tello.send_rc_control(0, 0, 0, 0) 
    
    #ROTATION

    elif key == ord('q'):  # Drone rotation gauche
        tello.send_rc_control(0, 0, 0, -50)
        tello.send_rc_control(0, 0, 0, 0) 

    elif key == ord('s'):  # Drone rotation droite
        tello.send_rc_control(0, 0, 0, 50)
        tello.send_rc_control(0, 0, 0, 0) 
    elif key == ord('a'):  # Drone rotation droite
        faire_correction = True
        if erreur > 0: 
            deplacement = "gauche"
        else: 
            deplacement = "gauche"
    else: 
        tello.send_rc_control(0, 0, 0, 0) 
        # Vérification si la fenêtre est fermée
    if cv2.getWindowProperty("Camera", cv2.WND_PROP_VISIBLE) < 1:
        break

# Libération des ressources
cv2.destroyAllWindows()
tello.streamoff()
tello.end()
