import cv2
import numpy as np
from djitellopy import Tello #Importation de l'object tello depuis la bibiliotheque djitellopy

# Variables globales pour la gestion des couleurs
color = 100
lo = np.array([color - 5, 100, 50])
hi = np.array([color + 5, 255, 255])

# Fonction de rappel pour la souris
def souris(event, x, y, flags, param):
    global color, lo, hi
    if event == cv2.EVENT_LBUTTONDBLCLK:
        # Récupère la couleur au pixel (x, y) en HSV
        color = image[y, x, 0]
        lo = np.array([color - 5, 100, 50])
        hi = np.array([color + 5, 255, 255])

# Initialisation de la capture vidéo

tello = Tello() # Initialization de l'object tello via son contructeur
tello.connect() # Connection  le drone via Wi-fi
tello.streamon() # Instruction permetant d'établir la transmission vidéo avec le drone
frame_read = tello.get_frame_read()
frame = frame_read.frame # Obtien le dernier frame transmit par le drone
cv2.namedWindow('Camera')
cv2.setMouseCallback('Camera', souris)

while True:
    frame = frame_read.frame

    # Conversion en HSV
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(image, lo, hi)

    # Traitement du masque
    mask = cv2.erode(mask, None, iterations=1)
    mask = cv2.dilate(mask, None, iterations=1)
    
    # Recherche des contours
    elements = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    
    if len(elements) > 0:
        # Plus grand contour
        c = max(elements, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        
        if radius > 10:
            # Dessin du cercle jaune
            cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
            
            # Affichage de la position et taille du cercle
            text = f"Position: ({int(x - frame.shape[1]//2)}, {int(y - frame.shape[0]//2)}) | Taille: {int(radius)}"
            cv2.putText(frame, text, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    # Affichage de l'image brute avec l'objet détecté
    cv2.imshow('Camera', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    

cap.release()
cv2.destroyAllWindows()