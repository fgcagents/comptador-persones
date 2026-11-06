# Validació de la primera versió

Data: 5 d’octubre de 2026.

- Codi Python compilat sense errors.
- Cinc proves automatitzades superades: màxim de vídeo sense suma, escena buida, fitxer invàlid / límit de durada, propagació d’errors sense recompte fictici i exportació / dibuix.
- Inferència real YOLO11n amb CPU sobre la fotografia d’exemple bus.jpg d’Ultralytics: 4 persones detectades i numerades. Imatge marcada revisada visualment.
- Interfície Streamlit comprovada amb AppTest: càrrega inicial, anàlisi real d’una fotografia, mètrica de 4 persones i correcció manual a 7 sense errors.
- Flux de vídeo comprovat amb AppTest i inferència real: vídeo AVI de 6 segons creat repetint la fotografia d’exemple; 12 fotogrames analitzats a 2 fps; màxim detectat 4. No es suma el total dels fotogrames.

Aquestes proves verifiquen funcionament i coherència, no constitueixen una mesura de precisió amb persones en moviment, aglomeracions o vídeos reals de l’usuari. No s’ha executat el llançador en Windows ni desplegat en un servidor extern.

Entorn de prova: Python 3.12, Streamlit 1.65.0, Ultralytics 8.4.173, OpenCV 5.0.0, Pillow 12.3.0.
