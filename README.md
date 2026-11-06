# Comptador de persones

App en català per comptar persones en fotografies i vídeos curts, executar-la al teu ordinador i revisar-ne els resultats.

## Windows

1. Instal·la Python 3.11 de https://www.python.org/downloads/ i activa «Add Python to PATH».
2. Descomprimeix tot el ZIP en una carpeta.
3. Executa `iniciar_windows.bat` amb doble clic. La primera instal·lació pot trigar diversos minuts i necessita Internet.
4. S’obrirà l’app al navegador. Si no s’obre, visita http://localhost:8501.
5. Per aturar-la, prem Ctrl+C a la consola.

El model `yolo11n.pt` ja està inclòs. No necessita un token de Hugging Face ni una GPU. L’espai d’instal·lació depèn de les versions de PyTorch que descarregui pip i pot ser de diversos GB.

## Linux / macOS

Amb Python 3.11 o 3.12 instal·lat:

```bash
bash iniciar.sh
```

Alternativa manual, des de la carpeta del projecte:

```bash
python -m venv .venv
# Activa l’entorn virtual: .venv\Scripts\activate (Windows)
# o: source .venv/bin/activate (Linux/macOS)
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Ús

- Fotografia: JPG, PNG o WEBP. Prem «Comptar persones» i revisa els requadres numerats.
- Vídeo: MP4, MOV, AVI o MKV, fins a 10 segons; recomanat 5–6 segons. La compatibilitat depèn del còdec. Si falla, converteix-lo a MP4/H.264.
- Màxim 50 MB per fitxer. Fotografies de fins a 40 megapíxels; es redueixen fins a 1600 px per costat per processar-les.
- Per defecte s’analitzen 8 fotogrames per segon. Pots triar 2, 4, 8 o 12.
- El resultat del vídeo és el màxim detectat en els fotogrames analitzats. La selecció inicial mostra el fotograma del màxim; pots revisar els altres.
- «Recompte revisat» permet corregir el total. No modifica els requadres.
- Descarrega el CSV amb el total automàtic, el revisat i els recomptes per fotograma. També pots descarregar la fotografia o un fotograma marcat.
- Si canvies el fitxer o els paràmetres, torna a prémer «Comptar persones».

## Interpretació

No suma fotogrames ni compta persones úniques, ni entrades/sortides. El màxim observat pot diferir del nombre real si una persona queda tapada o apareix entre dos fotogrames analitzats. La confiança mínima controla el filtre de deteccions; reduir-la pot augmentar tant les deteccions com els falsos positius. La precisió s’ha de valorar amb les teves imatges representatives.

## Processament i canvis respecte del codi original

S’ha simplificat el flux de càrrega, detecció i dibuix del codi original. El model NVIDIA LocateAnything-3B, Hugging Face ZeroGPU i la interfície HTML externa s’han substituït per YOLO11n i una interfície Streamlit completa. S’han eliminat els resultats ficticis de fallback i la pujada d’imatges a datasets de Hugging Face.

L’app processa els fitxers a l’ordinador o servidor on s’executa. Els vídeos temporals s’esborren en acabar; els resultats resten en memòria de sessió. Les descàrregues que decideixis guardar són persistents. Si l’allotges en un servidor, els fitxers es carregaran a aquell servidor. Aquest paquet no inclou desplegament ni autenticació.

## Validació

Consulta `VALIDACIO.md`. Pots executar les proves amb:

```bash
python -m unittest discover -v
```

## Fonts i dependències

- YOLO11: https://docs.ultralytics.com/models/yolo11/
- Paràmetres d’inferència: https://docs.ultralytics.com/modes/predict/
- Streamlit: https://docs.streamlit.io/

Ultralytics i els seus models tenen les condicions AGPL-3.0 / Enterprise del proveïdor: https://www.ultralytics.com/license. El model inclòs prové de https://github.com/ultralytics/assets/releases/download/v8.4.0/yolo11n.pt. Les altres dependències mantenen les seves llicències respectives.
