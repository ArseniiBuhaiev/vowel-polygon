from processor import *
import streamlit as st
from random import choice

if "all_polygons" not in st.session_state:
    a_ish = Sound("а", 750, 1200)
    e_ish = Sound("е", 520, 1630)
    y_ish = Sound("и", 350, 2100)
    i_ish = Sound("і", 280, 2270)
    o_ish = Sound("о", 450, 750)
    u_ish = Sound("у", 350, 600)

    ish = FormantPolygon(speaker="За Іщенком", vowels=[a_ish, e_ish, y_ish, i_ish, u_ish, o_ish])
    st.session_state.all_polygons = [ish]

st.set_page_config(page_title="Генератор формантних полігонів (трикутників)",
                   layout="wide",
                   menu_items={
                       'About': "Застосунок для побудови формантних полігонів голосних та порівняння з еталоном та між собою."
                   })
st.title("Генератор формантних полігонів".upper(), text_alignment="center", anchor=False)

l_spacer, col1, col2, right_spacer = st.columns([1, 3, 3, 1])

with open("names.txt", "r", encoding="utf-8") as f:
    names = [name for name in f]

with st.sidebar:
    st.header("Налаштування графіка")
    swap_axes = st.checkbox("Поміняти F1 та F2 місцями", value = False)
    invert = st.checkbox("Інверсія F1", value=False)

with col1:
    st.header("Додати мовця",  text_alignment="center", anchor=False)

    left_spacer, content, right_spacer = st.columns([1,8,1])

    with content:
        with st.form("speaker_form", clear_on_submit=True):
            speaker = st.text_input("Ім'я мовця", key="speaker_input", placeholder=choice(names))

            vowel_names = ["а", "е", "и", "і", "у", "о"]

            for vwl in vowel_names:
                vwl_col, f1_col, f2_col = st.columns([1, 3, 3])

                with vwl_col:
                    st.markdown(f"<h3 style='text-align: center; margin-top: 25px; font-size: 18px'>{vwl.upper()}</h3>", unsafe_allow_html=True)
                with f1_col:
                    f1 = st.number_input(f"F1", key=f"f1_{vwl}", step=50)
                with f2_col:
                    f2 = st.number_input(f"F2", key=f"f2_{vwl}", step=50)               

            submit_button = st.form_submit_button("Додати мовця", use_container_width=True)

            if submit_button:
                if st.session_state.speaker_input.strip().title():
                    vowels = []
                    for vwl in vowel_names:
                        f1_val = st.session_state[f"f1_{vwl}"]
                        f2_val = st.session_state[f"f2_{vwl}"]
                        vowels.append(Sound(vwl, f1_val, f2_val))

                    polygon = FormantPolygon(speaker, vowels)
                    st.session_state.all_polygons.append(polygon)

                    st.success(f"Мовця {speaker} додано!")
                    st.rerun()
                else:
                    st.error("Введіть ім'я мовця!")

        if st.button("Очистити список", use_container_width=True):
            st.session_state.all_polygons = st.session_state.all_polygons[:1]
            st.rerun()

        if st.session_state.all_polygons:
            for idx, poly in enumerate(st.session_state.all_polygons):
                with st.expander(f"👤 {poly.speaker}"):
                    header_col1, header_col2, header_col3 = st.columns([1, 2, 2])
                    header_col1.write("**Звук**")
                    header_col2.write("**F1 (Hz)**")
                    header_col3.write("**F2 (Hz)**")
                    
                    for v in poly.vowels[:-1]:
                        v_col, f1_val, f2_val = st.columns([1, 2, 2])
                        v_col.write(f"**{v.name.upper()}**")
                        f1_val.write(str(v.f1))
                        f2_val.write(str(v.f2))
                    
                    if idx > 0:
                        if st.button(f"Видалити {poly.speaker}", key=f"del_{idx}"):
                            st.session_state.all_polygons.pop(idx)
                            st.rerun()
        else:
            st.info("Список порожній")

with col2:
    st.header("Візуалізація", text_alignment="center", anchor=False)

    if st.session_state.all_polygons:
        fig, ax = plt.subplots(figsize=(6, 6))
        colors = ["#FF5E00", "#09FF00FF", "#FF0000", "#FFFB00", "#1100FF",
                  "#FF0095", "#9900FF", "#FF5100", "#6453FF", "#161616"]
        
        for i, poly in enumerate(st.session_state.all_polygons):
            if not swap_axes:
                xpoints, ypoints = poly.get_x_y()
                ax.set_xlabel("F1", fontsize=9)
                ax.set_ylabel("F2", fontsize=9)
            else:
                ypoints, xpoints = poly.get_x_y()
                ax.set_xlabel("F2", fontsize=9)
                ax.set_ylabel("F1", fontsize=9)
            vowels = [vwl.name for vwl in poly.vowels]
            plgn = ax.fill(xpoints, ypoints, "#FFFFFF00", label=poly.speaker, edgecolor=colors[i])
            ax.scatter(xpoints, ypoints, s=5)
            for i, vwl in enumerate(poly.vowels):
                plt.text(xpoints[i], ypoints[i] + 15, vwl.name.upper(), fontsize=8)
        
        if invert:
            if not swap_axes:
                ax.invert_xaxis()
            else:
                ax.invert_yaxis()
        ax.grid(True, alpha=0.3)
        ax.legend(loc="lower right")
        st.pyplot(fig)