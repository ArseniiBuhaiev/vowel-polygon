from processor import *
import streamlit as st
from random import choice
import pandas as pd
# import pymorphy3

if "all_polygons" not in st.session_state or len(st.session_state.all_polygons) == 1:
    a_ish = Sound("а", 750, 1200)
    e_ish = Sound("е", 520, 1630)
    y_ish = Sound("и", 350, 2100)
    i_ish = Sound("і", 280, 2270)
    o_ish = Sound("о", 450, 750)
    u_ish = Sound("у", 350, 600)

    ish = FormantPolygon(speaker="За Іщенком", vowels=[a_ish, e_ish, y_ish, i_ish, u_ish, o_ish])
    st.session_state.all_polygons = [ish]

if "file_uploader_key" not in st.session_state:
    st.session_state.file_uploader_key = 0

if "norm_method" not in st.session_state:
    st.session_state.norm_method = "Hz"

st.set_page_config(page_title="Формантний аналіз",
                   layout="wide",
                   menu_items={
                       'About': "Застосунок для побудови формантних полігонів голосних та їхнього порівняння між собою."
                   })

st.header("Лабораторія фонетики", text_alignment="center", anchor=False)

about, polygon_graph, analysis = st.tabs(["Про проєкт", "Введення даних", "Аналіз"])

with about:
    st.title("Формантний аналіз", text_alignment="center", anchor=False)
    st.markdown("---")
    l_spacer, intro, r_spacer = st.columns([1,4,1])
    with intro:
        st.markdown("""
Значення F1 та F2 голосних звуків дають важливу інформацію про індивідуальні особливості мовлення. Формантний аналіз дозволяє порівнювати ці особливості між мовцями для ідентифікації особи на записі.
Цей проєкт зосереджується на цій методиці. Кінцева мета -- створити інструмент, що автоматично виконуватиме цю роботу від початку (сегментації голосних, їхньої параметризації) і до кінця (порівняльний аналіз формантних полігонів).
Інструмент дозволяє:
- **Нормалізувати дані**: Нормалізація "сирих" показників у Гц через *Z-score за методом Лобанова*, або у *шкалу Bark за формулою Траунмюллера* для психоакустичної трансформації даних про голосні.
- **Обраховувати площі полігонів**: Один зі способів виокремлення індивідуальних параметрів мовлення дикторів, що допомагає в автоматичному порівнянні. Площа обраховується за формулою Гаусса (алгоритм шнурування).
- **Обраховувати центроїди полігонів**: Математично знайти "центр маси" простору голосних мовців для подальшого обчислення відстані між ними.
- **Обраховувати подібність полігонів**: Порівняння наскільки вимова голосних між мовцями збігається та наскільки відхиляється від еталону на основі розрахунку подібності багатокутників за Прокрустовим аналізом та відстанню Фреше.
- **Отримати оцінку, що мовець той самий**: Ґрунтуючись на всіх обрахунках, програма самостійно виносить вердикт чи належать полігони одній особі.
- **Додавати до 2 мовців**: З метою визначення невідомого диктора за наявності підозрюваного, можна порівнювати формантні полігони двох людей на записах.
- **Зберігати дані та повторно їх використовувати**: Для полегшення роботи, достатньо один раз вручну ввести дані і отримати зручний файл у форматі .json.
- **Керувати візуалізацією**: Вісі можна міняти місцями та інвертувати, аби досягти бажаного вигляду графіка.
    """.strip())

with polygon_graph:
    l_spacer, col1, col2, col3, r_spacer = st.columns([1, 3, 3, 2, 1])

    with open("names.txt", "r", encoding="utf-8") as f:
        names = [name for name in f]

    with col1:
        st.header("Додати мовця",  text_alignment="center", anchor=False)

        l_spacer, content, r_spacer = st.columns([1,8,1])

        with content:
            with st.form("speaker_form", clear_on_submit=True):
                speaker = st.text_input("Ім'я мовця", key="speaker_input", placeholder=choice(names))

                vowel_labels = ["а", "е", "и", "і", "у", "о"]

                for vwl in vowel_labels:
                    vwl_col, f1_col, f2_col = st.columns([1, 3, 3])

                    with vwl_col:
                        st.markdown(f"<h3 style='text-align: center; margin-top: 25px; font-size: 18px'>{vwl.upper()}</h3>", unsafe_allow_html=True)
                    with f1_col:
                        f1 = st.number_input(f"F1", key=f"f1_{vwl}", step=50)
                    with f2_col:
                        f2 = st.number_input(f"F2", key=f"f2_{vwl}", step=50)               

                submit_button = st.form_submit_button("Створити мовця", use_container_width=True)

                if submit_button:
                    if len(st.session_state.all_polygons) < 3:
                        if st.session_state.speaker_input:
                            vowels = []
                            for vwl in vowel_labels:
                                f1_val = st.session_state[f"f1_{vwl}"]
                                f2_val = st.session_state[f"f2_{vwl}"]
                                vowels.append(Sound(vwl, f1_val, f2_val))

                            polygon = FormantPolygon(speaker.strip().title(), vowels)
                            st.session_state.all_polygons.append(polygon)

                            st.toast(f"Мовця {speaker} додано!", icon="✅")
                            st.rerun()
                        else:
                            st.toast("Введіть ім'я мовця.", icon="⚠️")
                    else:
                        st.toast("Максимальна кількість мовців.", icon="⚠️")

            uploaded_file = st.file_uploader("Завантажити з JSON", type=".json", max_upload_size=1, key=f"uploader_{st.session_state.file_uploader_key}")

            if uploaded_file is not None:
                try:
                    data = json.load(uploaded_file)
                    new_polygon = FormantPolygon.from_dict(data)
                    if not any(p.speaker == new_polygon.speaker for p in st.session_state.all_polygons):
                        st.session_state.all_polygons.append(new_polygon)
                        st.toast(f"Мовця {new_polygon.speaker} додано!")

                        st.session_state.file_uploader_key += 1
                        st.rerun()
                    else:
                        st.toast("Мовець уже існує.", icon="⚠️")
                        st.session_state.file_uploader_key += 1

                except Exception as e:
                    st.warning(f"Помилка при читанні файлу: {e}.")

    with col3:
        st.header("Налаштування графіка", text_alignment="center", anchor=False)
        l_spacer, settings, r_spacer = st.columns([1,3,1])
        with settings:
            norm_radio = st.radio(
                label="Нормалізація",
                options=["Hz", "Z-score", "Bark"],
                key="norm_method",
                help="""**Hz**: Сирі дані без нормалізації  
                **Z-score (метод Лобанова)**: Нормалізація за стандартним відхиленням  
                **Bark**: психоакустична трансформація"""
            )

            st.markdown("---")
            st.markdown("Вісі")
            swap_axes = st.checkbox("Поміняти F1 та F2 місцями", value=False)
            invert_f1 = st.checkbox("Інверсія F1", value=False)

    with col2:
        st.header("Візуалізація", text_alignment="center", anchor=False)

        if len(st.session_state.all_polygons) > 1:
            vowel_sets = [set(vowel.label for vowel in polygon.vowels) for polygon in st.session_state.all_polygons[1:]]

            target_vowels = set.intersection(*vowel_sets)

            for polygon in st.session_state.all_polygons:
                polygon.filter_vowels(target_vowels)

        if st.session_state.all_polygons:
            colors = ["#000000", "#0011FFFF", "#FF0000"]
            fig, ax = plt.subplots(figsize=(6, 6))

            for i, poly in enumerate(st.session_state.all_polygons):
                norm_method = st.session_state.norm_method
                
                if norm_method == "Hz":
                    offset = 15
                elif norm_method == "Bark":
                    poly = NormalizedPolygon(poly, method="Bark")
                    norm_method = poly.method
                    offset = 0.1
                elif norm_method == "Z-score":
                    poly = NormalizedPolygon(poly, method="Z-score")
                    norm_method = poly.method
                    offset = 0.03
                
                if not swap_axes:
                    xpoints, ypoints = poly.get_x_y()
                    ax.set_xlabel(f"F1 ({norm_method})", fontsize=9)
                    ax.set_ylabel(f"F2 ({norm_method})", fontsize=9)
                else:
                    ypoints, xpoints = poly.get_x_y()
                    ax.set_xlabel("F2 (Hz)", fontsize=9)
                    ax.set_ylabel("F1 (Hz)", fontsize=9)
                
                vowels = [vwl.label for vwl in poly.vowels]
                plgn = ax.fill(xpoints, ypoints, "#FFFFFF00", label=poly.speaker, edgecolor=colors[i])

                ax.scatter(xpoints, ypoints, s=5, color=colors[i])
                for i, vwl in enumerate(poly.vowels):
                    plt.text(xpoints[i], ypoints[i] + offset, vwl.label.upper(), fontsize=8)

            if invert_f1:
                if not swap_axes:
                    ax.invert_xaxis()
                else:
                    ax.invert_yaxis()

            ax.grid(True, alpha=0.3)
            ax.legend(loc="upper center", ncol=3, bbox_to_anchor=(0.5, -0.1))
            ax.set_title("Формантні полігони мовців")
            
            x_limits = ax.get_xlim()
            y_limits = ax.get_ylim()
            
            st.pyplot(fig)

            for idx, poly in enumerate(st.session_state.all_polygons):
                with st.expander(f"{poly.speaker}" if idx > 0 else f"Еталон (за Іщенком)"):
                    header_col1, header_col2, header_col3 = st.columns([1, 2, 2])
                    header_col1.write("**Звук**")
                    header_col2.write("**F1 (Hz)**")
                    header_col3.write("**F2 (Hz)**")

                    for v in poly.vowels:
                        v_col, f1_val, f2_val = st.columns([1, 2, 2])
                        v_col.write(f"**{v.label.upper()}**")
                        f1_val.write(str(v.f1))
                        f2_val.write(str(v.f2))

                    if idx > 0:
                        delete_col, download_col = st.columns([1,1])
                        with delete_col:
                            if st.button(f"Видалити {poly.speaker}", key=f"del_{idx}", use_container_width=True):
                                st.session_state.all_polygons.pop(idx)
                                st.rerun()
                        with download_col:
                            json_data = json.dumps(poly.save_to_json(), ensure_ascii=False, indent=4)

                            if st.download_button(
                                label="Зберегти JSON",
                                file_name=f"{poly.speaker}_formants.json",
                                mime="application/json",
                                data=json_data,
                                key=f"dl_btn_{poly.speaker}",
                                use_container_width=True
                            ):
                                st.toast(f"Дані про {poly.speaker} збережено.", icon="💾")

            if st.button("Очистити список", use_container_width=True):
                st.session_state.all_polygons = st.session_state.all_polygons[:1]
                st.rerun()

with analysis:
    if len(st.session_state.all_polygons) < 2:
        st.markdown("Відсутні дані для аналізу.", text_alignment="center")
    elif norm_method == "Hz":
        st.markdown("Аналіз можливий лише для нормалізованих даних.", text_alignment="center")
    else:
        st.header("Аналіз", text_alignment="center", anchor=False)

        data, text = st.columns([4,4])
        with data:
            subjects = st.session_state.all_polygons[1:]
            ish = st.session_state.all_polygons[0]
    
            l_s, table, r_s = st.columns([1,4,1])
            with table:
                st.table(
                    {
                        "Мовець": [polygon.speaker for polygon in subjects],
                        "Координати центроїда": [f"{cx:.2f}, {cy:.2f}" for polygon in subjects for cx, cy in [polygon.get_centroid(st.session_state.norm_method)]],
                        "Площа формантного полігона": [f"{polygon.get_area(norm_method):.2f}" for polygon in subjects],
                        "Відхилення від еталону": [f"{get_deviation(polygon, ish):.2f}" for polygon in subjects],
                    }
                )
        
            colors = ["#000000", "#0011FFFF", "#FF0000"]
            fig_c, ax_c = plt.subplots(figsize=(6, 6))
    
            l_spacer, centroid_plot, r_spacer = st.columns([1, 3, 1])
            with centroid_plot:
                for i, poly in enumerate(st.session_state.all_polygons):
                    if i > 0:
                        if norm_method == "Hz":
                            offset = 15
                        elif norm_method == "Bark":
                            poly = NormalizedPolygon(poly, method="Bark")
                            norm_method = poly.method
                            offset = 0.004
                        elif norm_method == "Z-score":
                            poly = NormalizedPolygon(poly, method="Z-score")
                            norm_method = poly.method
                            offset = 0.03
    
                        if not swap_axes:
                            xpoints, ypoints = poly.get_centroid(norm_method)
                            ax_c.set_xlabel(f"F1 ({norm_method})", fontsize=9)
                            ax_c.set_ylabel(f"F2 ({norm_method})", fontsize=9)
                        else:
                            ypoints, xpoints = poly.get_centroid(norm_method)
                            ax_c.set_xlabel(f"F2 ({norm_method})", fontsize=9)
                            ax_c.set_ylabel(f"F1 ({norm_method})", fontsize=9)
    
                        ax_c.scatter(xpoints, ypoints, s=30, marker="x", color=colors[i], label=poly.speaker)
                
                if invert_f1:
                    if not swap_axes:
                        ax.invert_xaxis()
                    else:
                        ax.invert_yaxis()
                
                ax_c.legend(loc="upper center", ncol=3, bbox_to_anchor=(0.5, -0.1))
                ax_c.grid(True, alpha=0.3)
                ax_c.set_xlim(x_limits)
                ax_c.set_ylim(y_limits)
                ax_c.set_title("Центроїди мовців")
    
                st.pyplot(fig_c)
    
            if len(st.session_state.all_polygons) > 2:
                c_d = centroid_distance(subjects[0].get_centroid(norm_method), subjects[1].get_centroid(norm_method))
                sim = 1 - get_deviation(*subjects)
                a_dif = abs(subjects[0].get_area(norm_method) - subjects[1].get_area(norm_method))
                
                comparative_df = pd.DataFrame(
                    {
                        "Відстань між центроїдами": [f"{c_d:.2f}"],
                        "Подібність полігонів мовців": f"{sim*100:.2f}%",
                        "Різниця площ полігонів": f"{a_dif:.2f}"
                    }
                )
                
                l_s, table, r_s = st.columns([1,4,1])
                with table:
                    st.table(comparative_df.T)

        with text:
#             if len(st.session_state.all_polygons) > 2:
# #                 morph = pymorphy3.MorphAnalyzer(lang='uk')

# #                 st.header("Висновок", text_alignment="center", anchor=False)
# #                 st.markdown(
# #                 """

# # """
# #                 )
            
            st.header("Довідка", text_alignment="center", anchor=False)
            st.markdown(
                """
- *Центроїд* -- центральна точка многокутника, яку використовують для поєднання графічної та атрибутивної інформації.
- *Формула площі Гаусса* -- формула визначення площі простого багатокутника, вершини якого задано декартовими координатами на площині.
- *Відстань Фреше* -- міра подібності кривих, що враховує число і порядок точок уздовж кривих.
- *Подібність полігонів мовців* -- міра подібності формантних полігонів за відстанню Фреше.
- *Відхилення від еталону* -- міра відхилення формантних полігонів від формантного полігона за О. Іщенком за відстанню Фреше.
"""
            )