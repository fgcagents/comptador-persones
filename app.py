import hashlib
import io
from pathlib import Path
import tempfile
import threading

import pandas as pd
import streamlit as st
from PIL import Image, UnidentifiedImageError
from core import prepare_image, detect_people, annotate, image_bytes, analyse_video, export_csv

st.set_page_config(page_title='Comptador de persones', page_icon='👥', layout='wide')
st.title('Comptador de persones')
st.write('Carrega una fotografia o un vídeo de 5–6 segons i revisa el recompte.')
st.caption('El vídeo mostra el màxim detectat en els fotogrames analitzats. No compta persones úniques ni entrades i sortides.')

@st.cache_resource
def load_detector():
    from ultralytics import YOLO
    return YOLO(str(Path(__file__).with_name('yolo11n.pt'))), threading.Lock()

with st.sidebar:
    st.header('Configuració')
    confidence = st.slider('Confiança mínima', 0.10, 0.90, 0.35, 0.05,
                           help='Baixar-la pot detectar més persones però també generar falsos positius.')
    sample_fps = st.select_slider('Fotogrames analitzats per segon', options=[2, 4, 8, 12], value=8)
    st.caption('Un valor més alt analitza més instants i triga més temps.')
    st.info('Processament a l’ordinador o servidor on executes l’app. L’app no envia les imatges a serveis de detecció externs.')
    st.caption('El model està inclòs al paquet. La instal·lació de dependències necessita Internet.')
    if st.button('Esborrar el resultat'):
        st.session_state.pop('result', None)
        st.rerun()

upload = st.file_uploader('Fotografia o vídeo', type=['jpg', 'jpeg', 'png', 'webp', 'mp4', 'mov', 'avi', 'mkv'])
if upload is None:
    st.info('Selecciona un fitxer per començar. Màxim: 50 MB i 10 segons de vídeo.')
    st.stop()
if upload.size > 50 * 1024 * 1024:
    st.error('El fitxer supera els 50 MB.')
    st.stop()
raw = upload.getvalue()
suffix = Path(upload.name).suffix.lower()
is_video = suffix in {'.mp4', '.mov', '.avi', '.mkv'}
signature = hashlib.sha256(raw + repr((confidence, sample_fps)).encode()).hexdigest()
if st.session_state.get('result', {}).get('signature') != signature:
    st.session_state.pop('result', None)

if st.button('Comptar persones', type='primary'):
    st.session_state.pop('result', None)
    try:
        with st.spinner('Carregant el model i analitzant…'):
            model, lock = load_detector()
            def detector(image):
                with lock:
                    return detect_people(model, image, confidence)
            if is_video:
                progress = st.progress(0.0, text='Analitzant el vídeo…')
                with tempfile.TemporaryDirectory(prefix='persones_') as directory:
                    path = Path(directory) / ('input' + suffix)
                    path.write_bytes(raw)
                    result = analyse_video(path, detector, sample_fps, progress=progress.progress)
                result['kind'] = 'video'
            else:
                with Image.open(io.BytesIO(raw)) as source:
                    if source.width * source.height > 40_000_000:
                        raise ValueError('La fotografia supera els 40 megapíxels. Redueix-ne la mida.')
                    image = prepare_image(source)
                detections = detector(image)
                result = {'kind': 'foto', 'maximum': len(detections),
                          'image': image_bytes(annotate(image, detections))}
            result['signature'] = signature
            st.session_state['result'] = result
    except (ValueError, UnidentifiedImageError, Image.DecompressionBombError) as exc:
        st.error(str(exc))
    except Exception as exc:
        st.error('No s’ha pogut completar l’anàlisi. No hi ha cap recompte vàlid. Comprova les dependències i la descàrrega del model.')
        with st.expander('Detall tècnic'):
            st.code(f'{type(exc).__name__}: {exc}')

result = st.session_state.get('result')
if result:
    left, right = st.columns([3, 1])
    with right:
        st.metric('Màxim detectat' if is_video else 'Persones detectades', result['maximum'])
        corrected = st.number_input('Recompte revisat', min_value=0, value=int(result['maximum']),
                                    step=1, key='corrected_' + signature,
                                    help='Modifica’l després de revisar visualment les deteccions.')
        st.caption('La correcció modifica el total exportat; no modifica els requadres.')
        if is_video:
            st.write(f"Durada: {result['duration']:.2f} s · {len(result['frames'])} fotogrames analitzats")
        rows = result['frames'] if is_video else [{'count': result['maximum']}]
        st.download_button('Descarregar recompte CSV',
                           export_csv(upload.name, result['kind'], rows, result['maximum'], corrected),
                           'recompte_persones.csv', 'text/csv')
    with left:
        if is_video:
            frames = result['frames']
            selected = st.select_slider('Revisa els fotogrames', options=list(range(len(frames))),
                                        value=result['peak_index'],
                                        format_func=lambda i: f"{frames[i]['second']:.2f} s · {frames[i]['count']} persones",
                                        key='frame_' + signature)
            st.image(frames[selected]['image'], caption='Fotograma analitzat amb persones numerades', width='stretch')
            st.line_chart(pd.DataFrame({'Segon': [f['second'] for f in frames],
                                       'Persones': [f['count'] for f in frames]}).set_index('Segon'))
            st.download_button('Descarregar aquest fotograma', frames[selected]['image'], 'fotograma_persones.jpg', 'image/jpeg')
        else:
            st.image(result['image'], caption='Persones numerades per revisar el recompte', width='stretch')
            st.download_button('Descarregar imatge marcada', result['image'], 'persones_detectades.png', 'image/png')
    st.warning('Revisa les deteccions: persones tapades, reflexos o poca llum poden alterar el recompte. En vídeo el màxim és només el màxim detectat entre els fotogrames analitzats.')
