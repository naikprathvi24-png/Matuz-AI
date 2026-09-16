import streamlit as st
import fitz

from auth import create_user, login_user

from chat_history import (
    create_chat,
    save_message,
    get_user_chats,
    get_chat_messages,
    chat_belongs_to_user,
    delete_chat,
)

from utils.api import (
    get_ai_response,
    get_image_response,
    transcribe_audio,
)

from utils.text_cleaner import clean_text
from utils.prompts import summary_prompt
from utils.file_parser import extract_text
# ============================================================
# Matuz AI – Intelligent Study Assistant
# Copyright © 2026 Prathvi Naik. All Rights Reserved.
# ============================================================


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Matuz AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# LOAD CSS
# ============================================================

try:
    with open(
        "styles/style.css",
        "r",
        encoding="utf-8",
    ) as f:
        css = f.read()

    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True,
    )

except FileNotFoundError:
    pass


# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "logged_in": False,
    "user": None,
    "show_signup": False,
    "current_chat_id": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# LOGIN / SIGNUP
# ============================================================

if not st.session_state.logged_in:

    # --------------------------------------------------------
    # LOGIN / SIGNUP HEADER
    # --------------------------------------------------------

    st.markdown(
    """
    <div class="login-container">
        <div class="login-logo">🧠</div>
        <h1>Matuz AI</h1>
        <p>Your AI-powered study assistant</p>
    </div>
    """,
    unsafe_allow_html=True
)

    # --------------------------------------------------------
    # LOGIN
    # --------------------------------------------------------

    if not st.session_state.show_signup:

        st.markdown("### 🔐 Login")

        email = st.text_input(
            "Email",
            placeholder="Enter your email",
            key="login_email",
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="login_password",
        )

        if st.button(
            "Login",
            type="primary",
            use_container_width=True,
            key="login_button",
        ):

            if not email or not password:

                st.warning(
                    "Please enter your email and password."
                )

            else:

                success, user = login_user(
                    email,
                    password,
                )

                if success:

                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.session_state.current_chat_id = None

                    st.rerun()

                else:

                    st.error(
                        "Invalid email or password."
                    )

        st.divider()

        st.write(
            "Don't have an account?"
        )

        if st.button(
            "Create Account",
            use_container_width=True,
            key="open_signup",
        ):

            st.session_state.show_signup = True

            st.rerun()

    # --------------------------------------------------------
    # SIGNUP
    # --------------------------------------------------------

    else:

        st.markdown("### 📝 Create Account")

        name = st.text_input(
            "Full Name",
            placeholder="Enter your name",
            key="signup_name",
        )

        email = st.text_input(
            "Email",
            placeholder="Enter your email",
            key="signup_email",
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Create a password",
            key="signup_password",
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="Re-enter your password",
            key="signup_confirm_password",
        )

        if st.button(
            "Create Account",
            type="primary",
            use_container_width=True,
            key="create_account",
        ):

            if not name or not email or not password:

                st.warning(
                    "Please fill in all fields."
                )

            elif len(password) < 6:

                st.warning(
                    "Password must contain at least 6 characters."
                )

            elif password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            else:

                success, message = create_user(
                    name,
                    email,
                    password,
                )

                if success:

                    st.success(
                        "Account created successfully! Please login."
                    )

                    st.session_state.show_signup = False

                    st.rerun()

                else:

                    st.error(message)

        st.divider()

        if st.button(
            "← Back to Login",
            use_container_width=True,
            key="back_to_login",
        ):

            st.session_state.show_signup = False

            st.rerun()

    st.stop()


# ============================================================
# USER
# ============================================================

user = st.session_state.user
user_id = user["id"]


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-logo">

            <div class="sidebar-icon">
                🧠
            </div>

            <div>

                <div class="sidebar-title">
                    AI Notes
                </div>

                <div class="sidebar-subtitle">
                    Study Assistant
                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # --------------------------------------------------------
    # NEW CHAT
    # --------------------------------------------------------

    if st.button(
        "＋ New Chat",
        use_container_width=True,
        key="new_chat",
    ):

        st.session_state.current_chat_id = None

        st.rerun()

    st.markdown(
        "### 💬 Previous Chats"
    )

    chats = get_user_chats(user_id)

    if not chats:

        st.caption(
            "Your conversations will appear here."
        )

    else:

        for chat in chats:

            chat_id = chat[0]
            title = chat[1]

            col1, col2 = st.columns(
                [5, 1]
            )

            with col1:

                if st.button(
                    title,
                    key=f"chat_{chat_id}",
                    use_container_width=True,
                ):

                    if chat_belongs_to_user(
                        chat_id,
                        user_id,
                    ):

                        st.session_state.current_chat_id = chat_id

                        st.rerun()

            with col2:

                if st.button(
                    "🗑️",
                    key=f"delete_{chat_id}",
                ):

                    delete_chat(
                        chat_id,
                        user_id,
                    )

                    if (
                        st.session_state.current_chat_id
                        == chat_id
                    ):

                        st.session_state.current_chat_id = None

                    st.rerun()

    st.divider()

    # --------------------------------------------------------
    # USER CARD
    # --------------------------------------------------------

    st.markdown(
        f"""
        <div class="user-card">

            <strong>
                👤 {user["name"]}
            </strong>

            <br>

            <small>
                {user["email"]}
            </small>

        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # LOGOUT
    # --------------------------------------------------------

    if st.button(
        "🚪 Logout",
        use_container_width=True,
        key="logout",
    ):

        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.current_chat_id = None

        st.rerun()


# ============================================================
# MAIN HEADER
# ============================================================

st.markdown(
    '<div class="main-header"><h1>🧠 Matuz AI</h1><p>Ask questions, summarize notes, upload files, analyze images or use your voice.</p></div>',
    unsafe_allow_html=True
)


# ============================================================
# CURRENT CHAT
# ============================================================

current_chat_id = st.session_state.current_chat_id

if current_chat_id is not None:

    if chat_belongs_to_user(
        current_chat_id,
        user_id,
    ):

        messages = get_chat_messages(
            current_chat_id
        )

        for role, content in messages:

            if role == "user":

                with st.chat_message("user"):

                    st.markdown(content)

            else:

                with st.chat_message("assistant"):

                    st.markdown(content)


# ============================================================
# WELCOME SCREEN
# ============================================================

# ============================================================
# WELCOME SCREEN
# ============================================================

if current_chat_id is None:

    st.markdown(
        '<div class="hero-section">'
        '<div class="hero-icon">🧠</div>'
        '<h1>How can I help you study?</h1>'
        '<p>Your intelligent study companion for notes, documents, images and voice.</p>'
        '<div class="feature-grid">'

        '<div class="feature-card">'
        '<div class="feature-icon">📚</div>'
        '<div class="feature-title">Summarize</div>'
        '<div class="feature-text">Turn lengthy notes into clear, easy-to-revise summaries.</div>'
        '</div>'

        '<div class="feature-card">'
        '<div class="feature-icon">✨</div>'
        '<div class="feature-title">Learn Smarter</div>'
        '<div class="feature-text">Understand difficult concepts with simple explanations.</div>'
        '</div>'

        '<div class="feature-card">'
        '<div class="feature-icon">🖼️</div>'
        '<div class="feature-title">Analyze Images</div>'
        '<div class="feature-text">Upload notes, diagrams and study images for AI analysis.</div>'
        '</div>'

        '<div class="feature-card">'
        '<div class="feature-icon">🎙️</div>'
        '<div class="feature-title">Use Your Voice</div>'
        '<div class="feature-text">Ask questions naturally using your microphone.</div>'
        '</div>'

        '</div>'
        '</div>',
        unsafe_allow_html=True
    )


# ============================================================
# CHAT COMPOSER
# ============================================================

col_plus, col_message, col_voice, col_send = st.columns(
    [0.7, 7.8, 1.0, 1.0],
    vertical_alignment="center",
)


# ============================================================
# FILE ATTACHMENT
# ============================================================

uploaded_files = []

with col_plus:

    with st.popover(
        "＋",
        use_container_width=True,
    ):

        st.markdown(
            "### 📎 Add files"
        )

        uploaded_files = st.file_uploader(
            "Upload study material",
            type=[
                "pdf",
                "docx",
                "txt",
                "png",
                "jpg",
                "jpeg",
                "webp",
            ],
            accept_multiple_files=True,
            key="composer_files",
        )

        if uploaded_files:

            st.caption(
                f"{len(uploaded_files)} file(s) selected"
            )


# ============================================================
# TEXT MESSAGE
# ============================================================

with col_message:

    user_text = st.text_input(
        "",
        placeholder="Message Matuz AI...",
        label_visibility="collapsed",
        key="composer_message",
    )


# ============================================================
# VOICE RECORDER
# ============================================================

with col_voice:

    with st.popover(
        "🎙️",
        use_container_width=True,
    ):

        st.markdown(
            """
            <div class="voice-panel-title">
                🎙️ Voice Recorder
            </div>

            <div class="voice-panel-description">
                Record your question and it will be
                automatically transcribed.
            </div>
            """,
            unsafe_allow_html=True,
        )

        audio_data = st.audio_input(
            "Record your voice",
            key="voice_recorder",
        )

        if audio_data is not None:

            st.success(
                "Recording captured."
            )

            if st.button(
                "🎙️ Transcribe & Ask AI",
                use_container_width=True,
                type="primary",
                key="transcribe_voice",
            ):

                try:

                    with st.spinner(
                        "🎙️ Transcribing your voice..."
                    ):

                        audio_bytes = audio_data.getvalue()

                        transcribed_text = transcribe_audio(
                            audio_bytes
                        )

                    if not transcribed_text:

                        st.error(
                            "I couldn't understand the recording. "
                            "Please try again."
                        )

                    else:

                        transcribed_text = str(
                            transcribed_text
                        ).strip()

                        # ------------------------------------
                        # CREATE CHAT
                        # ------------------------------------

                        if current_chat_id is None:

                            title = transcribed_text[:50]

                            if len(transcribed_text) > 50:
                                title += "..."

                            current_chat_id = create_chat(
                                user_id,
                                title or "Voice Chat",
                            )

                            st.session_state.current_chat_id = (
                                current_chat_id
                            )

                        # ------------------------------------
                        # SAVE USER MESSAGE
                        # ------------------------------------

                        voice_display = (
                            "🎙️ **Voice message**\n\n"
                            + transcribed_text
                        )

                        save_message(
                            current_chat_id,
                            "user",
                            transcribed_text,
                        )

                        # ------------------------------------
                        # AI RESPONSE
                        # ------------------------------------

                        with st.spinner(
                            "🧠 Thinking..."
                        ):

                            voice_response = get_ai_response(
                                transcribed_text
                            )

                        if voice_response:

                            save_message(
                                current_chat_id,
                                "assistant",
                                voice_response,
                            )

                        st.rerun()

                except Exception as e:

                    st.error(
                        "Voice processing failed: "
                        f"{type(e).__name__}: {e}"
                    )


# ============================================================
# SEND BUTTON
# ============================================================

with col_send:

    send_clicked = st.button(
        "↑",
        use_container_width=True,
        type="primary",
        key="send_message",
    )


# ============================================================
# PROCESS NORMAL MESSAGE
# ============================================================

if send_clicked:

    user_text = (
        user_text or ""
    ).strip()

    uploaded_files = (
        uploaded_files or []
    )

    # --------------------------------------------------------
    # VALIDATE
    # --------------------------------------------------------

    if not user_text and not uploaded_files:

        st.warning(
            "Please enter a message, attach a file, "
            "or use the voice recorder."
        )

        st.stop()

    # --------------------------------------------------------
    # CREATE CHAT
    # --------------------------------------------------------

    if current_chat_id is None:

        title_source = user_text

        if not title_source and uploaded_files:

            title_source = uploaded_files[0].name

        title = (
            title_source
            .replace("\n", " ")
            .strip()
        )

        if len(title) > 50:

            title = title[:50] + "..."

        current_chat_id = create_chat(
            user_id,
            title or "New Chat",
        )

        st.session_state.current_chat_id = (
            current_chat_id
        )

    # --------------------------------------------------------
    # FILE CATEGORIES
    # --------------------------------------------------------

    display_message = user_text

    document_texts = []
    image_files = []
    pdf_files = []

    # --------------------------------------------------------
    # PROCESS FILES
    # --------------------------------------------------------

    for uploaded_file in uploaded_files:

        filename = uploaded_file.name

        extension = (
            filename.lower()
            .split(".")[-1]
        )

        # --------------------------------------------
        # IMAGE
        # --------------------------------------------

        if extension in [
            "png",
            "jpg",
            "jpeg",
            "webp",
        ]:

            image_files.append(
                uploaded_file
            )

        # --------------------------------------------
        # PDF
        # --------------------------------------------

        elif extension == "pdf":

            pdf_files.append(
                uploaded_file
            )

        # --------------------------------------------
        # DOCX / TXT
        # --------------------------------------------

        elif extension in [
            "docx",
            "txt",
        ]:

            try:

                with st.spinner(
                    f"📖 Reading {filename}..."
                ):

                    extracted = extract_text(
                        uploaded_file
                    )

                if extracted and extracted.strip():

                    document_texts.append(
                        f"\n\n--- {filename} ---\n\n"
                        f"{extracted}"
                    )

                else:

                    st.warning(
                        f"No readable text found in {filename}."
                    )

            except Exception as e:

                st.error(
                    f"Could not read {filename}: {e}"
                )

    # --------------------------------------------------------
    # DISPLAY USER MESSAGE
    # --------------------------------------------------------

    if uploaded_files:

        file_names = "\n".join(
            f"📎 {file.name}"
            for file in uploaded_files
        )

        if display_message:

            display_message += (
                "\n\n" + file_names
            )

        else:

            display_message = file_names

    with st.chat_message("user"):

        st.markdown(
            display_message
        )

    # --------------------------------------------------------
    # SAVE USER MESSAGE
    # --------------------------------------------------------

    save_message(
        current_chat_id,
        "user",
        display_message,
    )

    # ========================================================
    # AI PROCESSING
    # ========================================================

    response = ""

    # ========================================================
    # IMAGE
    # ========================================================

    if image_files:

        image = image_files[0]

        image_prompt = user_text

        if not image_prompt:

            image_prompt = (
                "Analyze this image as study material. "
                "Read all visible text carefully. "
                "Identify important concepts, definitions, "
                "examples, formulas, diagrams and key points. "
                "Explain the content clearly for a student."
            )

        with st.spinner(
            "🖼️ Analyzing image..."
        ):

            response = get_image_response(
                image_prompt,
                image.getvalue(),
                image.type,
            )

    # ========================================================
    # PDF
    # ========================================================

    elif pdf_files:

        pdf_page_results = []

        for pdf_file in pdf_files:

            filename = pdf_file.name

            try:

                with st.spinner(
                    f"📄 Opening {filename}..."
                ):

                    pdf_document = fitz.open(
                        stream=pdf_file.getvalue(),
                        filetype="pdf",
                    )

                total_pages = len(
                    pdf_document
                )

                if total_pages == 0:

                    st.warning(
                        f"{filename} contains no pages."
                    )

                    pdf_document.close()

                    continue

                st.info(
                    f"📄 Found {total_pages} page(s) in {filename}"
                )

                # --------------------------------------------
                # ANALYZE EACH PAGE
                # --------------------------------------------

                for page_number in range(
                    total_pages
                ):

                    page = pdf_document[
                        page_number
                    ]

                    with st.spinner(
                        f"🧠 Analyzing page "
                        f"{page_number + 1} "
                        f"of {total_pages}..."
                    ):

                        pix = page.get_pixmap(
                            matrix=fitz.Matrix(
                                1.5,
                                1.5,
                            ),
                            alpha=False,
                        )

                        page_image = pix.tobytes(
                            "jpeg"
                        )

                        if user_text:

                            page_prompt = user_text

                        else:

                            page_prompt = (
                                "Analyze this PDF page "
                                "as study material. "
                                "Read all visible text carefully. "
                                "Extract important concepts, "
                                "definitions, examples, formulas, "
                                "diagrams and key points. "
                                "Explain the page clearly "
                                "for a student."
                            )

                        page_response = get_image_response(
                            page_prompt,
                            page_image,
                            "image/jpeg",
                        )

                        if page_response:

                            if not page_response.startswith(
                                "❌"
                            ):

                                pdf_page_results.append(
                                    f"### Page {page_number + 1}\n\n"
                                    f"{page_response}"
                                )

                            else:

                                st.warning(
                                    f"Page {page_number + 1} "
                                    f"could not be analyzed."
                                )

                pdf_document.close()

            except Exception as e:

                st.error(
                    f"Could not analyze PDF {filename}: "
                    f"{type(e).__name__}: {e}"
                )

        # --------------------------------------------
        # FINAL PDF RESPONSE
        # --------------------------------------------

        if pdf_page_results:

            response = (
                "## 📄 PDF Analysis\n\n"
                + "\n\n".join(
                    pdf_page_results
                )
            )

        else:

            response = (
                "❌ I could not analyze any pages "
                "from this PDF."
            )

    # ========================================================
    # DOCX / TXT
    # ========================================================

    elif document_texts:

        combined_documents = "".join(
            document_texts
        )

        max_chars = 24000

        if len(combined_documents) > max_chars:

            combined_documents = (
                combined_documents[:max_chars]
            )

            st.info(
                "📄 This document is very large. "
                "The first portion is being analyzed "
                "to stay within the AI request limit."
            )

        final_notes = (
            user_text
            + "\n\n"
            + combined_documents
        ).strip()

        cleaned_text = clean_text(
            final_notes
        )

        prompt = summary_prompt(
            cleaned_text
        )

        with st.spinner(
            "📖 Reading your study material..."
        ):

            response = get_ai_response(
                prompt
            )

    # ========================================================
    # NORMAL TEXT
    # ========================================================

    elif user_text:

        with st.spinner(
            "🧠 Thinking..."
        ):

            response = get_ai_response(
                user_text
            )

    # ========================================================
    # NO CONTENT
    # ========================================================

    else:

        response = (
            "Please provide some text or "
            "attach a supported file."
        )

    # ========================================================
    # SAVE AI RESPONSE
    # ========================================================

    if response:

        save_message(
            current_chat_id,
            "assistant",
            response,
        )

        with st.chat_message("assistant"):

            st.markdown(
                response
            )

        st.rerun()