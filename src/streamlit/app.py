import streamlit as st
import pathlib
import sys
import io
import cv2
import numpy as np

# To load our custom model functions
path = pathlib.Path("../models").resolve()
sys.path.insert(0, str(path))
path = pathlib.Path("..").resolve()
sys.path.insert(0, str(path))

# clean for reloading scriptwithout spamming sys.path insert
sys.path = list(dict.fromkeys(sys.path))

from model_functions import load_model, keras_predict_model, get_predict_value
from data_functions import load_resize_img_from_buffer
from plot_functions import make_gradcam_heatmap, overlay_heatmap_on_array

# App config:
model_save_path="../../models/EfficientNetB4_masked-Covid-19_masked-91.45.keras"
seg_model_save_path="../../models/unet-0.98.keras"

a = """
button_launch_predict = st.empty()
button_launch_grad_cam = st.empty()
"""
if "button_launch_predict" not in st.session_state:
    st.session_state.button_launch_predict = False
if "button_launch_grad_cam" not in st.session_state:
    st.session_state.button_launch_grad_cam = False

def onClick_launch_predict():
    st.session_state.click = True

def onClick_launch_grad_cam():
    st.session_state.click = True

# import custom Navigation bar
from modules.nav import Navbar
Navbar()

st.title("Application de classification de Radiographie Pulmonaire")

help_tooltip = """La prédiction est effectué par le model de deep-learning **EfficientNetB4**. 
Ce model est entrainé pour classifier l'image parmis les 4 possibilité suivantes: "sain", "atteint du  Covid", "de pneumonie" ou "d'opacité pulmonaire".

Plus d'information dans la partie "Contexte" et "modélisation".
"""

context_text = """
<div style="text-align: justify;">

Cette aplication permet la prédiction de l'état d'un patient à partir image de radiographie pulmonaire.

</div>"""
st.markdown(context_text, unsafe_allow_html=True, help=help_tooltip)


context_text_2 = """
<div style="text-align: justify;">
Le fichier à uploader peut être une image au format "png", "jpg", ou un dossier au format "zip" pour prédire un ensemble directement.

Des exemples sont fournis ci-dessous pour pouvoir tester l'application.

</div>"""
st.markdown(context_text_2, unsafe_allow_html=True)

uploaded_file = st.file_uploader("Fichier ou dossier à prédire:", type=['png', 'jpg', 'zip'])
if uploaded_file is not None:
    f_type = uploaded_file.type.split("/")[-1]
    if f_type in ['png', 'jpg']:
        # si png, jpg

        img_original_array, img = load_resize_img_from_buffer(uploaded_file)
        st.image(img, caption="Image loaded after re-sizing", use_container_width=False)

        masked_value = st.selectbox("Est-ce que l'image est masqué ? (Ne présente que les poumons et pas le coeur, foie et autre marquage)*",
                                    ("Oui", "Non"))
        masked_value = True if masked_value == "Oui" else False

        left, middle, right = st.columns(3)
        if middle.button("Démarrer la prediction", icon="🚀", on_click=onClick_launch_predict):
            with st.status("Prediction en cours...", expanded=True):

                if not masked_value:
                    st.write("Masquage à faire...")
                    st.write("Chargement du model de segmentation...")
                    # load model
                    seg_model = load_model(seg_model_save_path)


                st.write("Chargement du model de prediction...")
                # load model
                model = load_model(model_save_path)

                # make predict
                st.write("Prédiction...")
                pred = keras_predict_model(model, img)

                # Interpret prediction
                st.write("Interpretation...")
                pred = get_predict_value(pred)

                st.write("Prédiction fini.")

            st.success("Prédiction effectué")

            st.text(f" L'image est classé comme: {pred}")

            # make gradcam
            layer_name = st.selectbox("Choix de la layer à visualiser (Trié dans l'ordre: première, milieu, dernière):",
                                        ("stem_conv", "block4f_expand_conv", "top_conv"))
            
            #if st.button("Dessiner le Grad-CAM", icon="🚀", on_click=onClick_launch_grad_cam):
            efficientnet = model.get_layer("efficientnetb4")
            heatmap = make_gradcam_heatmap(img, efficientnet, layer_name)

            # Overlay the heatmap on the original image
            overlay = overlay_heatmap_on_array(heatmap, img_original_array, alpha=0.4)

            st.image(overlay, caption="Grad-CAM Applied:", use_container_width=False)


    elif f_type == "zip":
        # si zip prediction sur folder, retour que d'un df avec name / prediction
        print("A folder to process")


    else:
        raise TypeError("Wrong file type submitted (not 'png', 'jpg' or 'zip')")
        

