import cv2
import numpy as np
from djitellopy import Tello

# Initialisation du drone Tello
tello = Tello()
tello.connect()
tello.streamon()

# Acquisition du flux vidéo
frame_read = tello.get_frame_read()
titreFenetre = "Identification de couleur via la caméra du drone Tello"
color = 100
enlair = False

# Paramètres pour le seuil des couleurs
lo = np.array([color - 5, 100, 50])  # Limite basse
hi = np.array([color + 5, 255, 255])  # Limite haute

# Fonction pour gérer les événements de la souris
def souris(event, x, y, flags, param):
    global lo, hi, color
    if event == cv2.EVENT_LBUTTONDBLCLK:
        # Capture la valeur de couleur sur un double clic gauche
        color = imageHSV[y, x][0]
        lo[0] = color - 5
        hi[0] = color + 5
    elif event == cv2.EVENT_MOUSEWHEEL:
        # Ajuste la couleur avec la molette de la souris
        if flags > 0:
            color += 1
        else:
            color -= 1
        lo[0] = color - 5
        hi[0] = color + 5

cv2.namedWindow(titreFenetre)
cv2.setMouseCallback(titreFenetre, souris)

# Lecture de la vidéo en temps réel
while True:
    # Récupération de l'image depuis la caméra du drone
    frame = frame_read.frame
    imageHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # Conversion en HSV

    # Filtrage de la couleur
    mask = cv2.inRange(imageHSV, lo, hi)  # Crée un masque pour la couleur choisie
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    
    # Détection des contours de la zone colorée
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        # Trouve le plus grand contour
        c = max(contours, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)

        if radius > 10:  # Si le rayon est significatif
            cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 0), 2)  # Dessine un cercle autour
            cv2.putText(frame, f"Couleur: {color}", (int(x), int(y) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Affichage des fenêtres
    cv2.imshow(titreFenetre, frame)
    cv2.imshow("Masque", mask)

    # Gestion des commandes clavier
    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # Touche 'Echap' pour quitter
        break
    elif key == 32:  # Barre d'espace pour décoller/atterrir
        if enlair:
            tello.land()
        else:
            tello.takeoff()
        enlair = not enlair
    elif cv2.getWindowProperty(titreFenetre, cv2.WND_PROP_VISIBLE) < 1:
        break

# Arrêt du flux vidéo et du drone
tello.streamoff()
cv2.destroyAllWindows()
tello.end()
