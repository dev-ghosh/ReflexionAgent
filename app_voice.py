import os
import tempfile

import streamlit as st

from speech import transcribe_audio
from main_st import run_agent, extract_result


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Reflexion Agent",
    page_icon="🧠",
    layout="centered",
)


# ============================================================
# HEADER
# ============================================================

st.title("🧠 Reflexion Research Agent")

st.caption(
    "Ask a question by typing or speaking. "
    "The agent drafts, critiques, searches, and revises its own answer."
)


# ============================================================
# SESSION STATE
# ============================================================

if "answer" not in st.session_state:
    st.session_state["answer"] = None

if "references" not in st.session_state:
    st.session_state["references"] = []

if "critiques" not in st.session_state:
    st.session_state["critiques"] = []

# Used to put the Whisper transcription back
# into the same chat input on the next rerun.
if "pending_transcription" not in st.session_state:
    st.session_state["pending_transcription"] = None


# ============================================================
# PUT WHISPER TRANSCRIPTION INTO CHAT INPUT
# ============================================================
#
# Important:
# st.chat_input is a trigger widget.
# We therefore set its value BEFORE creating the widget.
#
# This happens after the audio has been transcribed and
# Streamlit has rerun the application.
# ============================================================

if st.session_state["pending_transcription"]:

    st.session_state["chat_input"] = (
        st.session_state["pending_transcription"]
    )

    st.session_state["pending_transcription"] = None


# ============================================================
# SINGLE CHATGPT-STYLE INPUT
# ============================================================

prompt = st.chat_input(
    "Ask anything...",
    key="chat_input",
    accept_audio=True,
    audio_sample_rate=16000,
)


# ============================================================
# HANDLE SUBMISSION
# ============================================================

if prompt is not None:

    # --------------------------------------------------------
    # CASE 1: USER USED THE MICROPHONE
    # --------------------------------------------------------

    if prompt.audio is not None:

        audio = prompt.audio

        temp_audio_path = None

        try:

            with st.spinner(
                "🎙️ Listening and converting your voice to text..."
            ):

                # --------------------------------------------
                # Save recorded audio temporarily
                # --------------------------------------------

                with tempfile.NamedTemporaryFile(
                    suffix=".wav",
                    delete=False,
                ) as temp_audio:

                    temp_audio.write(
                        audio.getvalue()
                    )

                    temp_audio_path = temp_audio.name


                # --------------------------------------------
                # Faster Whisper
                # --------------------------------------------

                transcribed_text = transcribe_audio(
                    temp_audio_path
                )


            # --------------------------------------------
            # Delete temporary audio file
            # --------------------------------------------

            if (
                temp_audio_path is not None
                and os.path.exists(temp_audio_path)
            ):

                os.remove(temp_audio_path)


            # --------------------------------------------
            # Put transcription back into SAME input
            # --------------------------------------------

            if transcribed_text:

                st.session_state[
                    "pending_transcription"
                ] = transcribed_text

                st.rerun()

            else:

                st.warning(
                    "I couldn't detect any speech "
                    "in the recording."
                )


        except Exception as e:

            # Make sure temporary file is removed
            if (
                temp_audio_path is not None
                and os.path.exists(temp_audio_path)
            ):

                os.remove(temp_audio_path)

            st.error(
                f"Transcription failed: {e}"
            )


    # --------------------------------------------------------
    # CASE 2: USER TYPED OR SUBMITTED TRANSCRIPTION
    # --------------------------------------------------------

    elif prompt.text:

        question = prompt.text.strip()

        if question:

            # --------------------------------------------
            # RUN REFLEXION AGENT
            # --------------------------------------------

            with st.spinner(
                "🧠 Thinking, searching, and revising..."
            ):

                try:

                    result = run_agent(
                        question
                    )

                    answer, references, critiques = (
                        extract_result(result)
                    )


                    # ----------------------------------------
                    # Store results
                    # ----------------------------------------

                    st.session_state["answer"] = answer

                    st.session_state["references"] = (
                        references
                    )

                    st.session_state["critiques"] = (
                        critiques
                    )


                except Exception as e:

                    st.error(
                        f"Something went wrong: {e}"
                    )

        else:

            st.warning(
                "Please enter a question."
            )


# ============================================================
# DISPLAY ANSWER
# ============================================================

if st.session_state["answer"]:

    st.divider()

    st.subheader("✅ Answer")

    st.code(
        st.session_state["answer"],
        language=None,
        wrap_lines=True,
    )


    # ========================================================
    # REFERENCES
    # ========================================================

    st.subheader("📚 References")

    if st.session_state["references"]:

        refs_text = "\n".join(
            st.session_state["references"]
        )

        st.code(
            refs_text,
            language=None,
            wrap_lines=True,
        )

    else:

        st.info(
            "No references returned."
        )


    # ========================================================
    # REFLEXION DETAILS
    # ========================================================

    with st.expander(
        "🔍 See how the agent critiqued & revised itself"
    ):

        for step in st.session_state["critiques"]:

            st.markdown(
                f"**{step['label']}**"
            )

            st.markdown(
                f"- **Missing:** "
                f"{step['missing'] or '—'}"
            )

            st.markdown(
                f"- **Superfluous:** "
                f"{step['superfluous'] or '—'}"
            )

            st.divider()