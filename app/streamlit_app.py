import os
import io
from moviepy.editor import VideoFileClip
from faster_whisper import WhisperModel
import anthropic
import streamlit as st

import settings

def convert_text_to_minutes(uploaded_file, selected_langage, claude_api_key, claude_model):
    whisper_dir = "whisper-text"
    if not os.path.exists(whisper_dir):
        os.makedirs(whisper_dir)
    whisper_file_path = os.path.join(whisper_dir, "whisper-output.txt")

    minutes_dir = "minutes-text"
    if not os.path.exists(minutes_dir):
        os.makedirs(minutes_dir)
    minutes_file_path = os.path.join(minutes_dir, "minutes-output.txt")

    decoded_text = uploaded_file.getvalue().decode("utf-8")

    client = anthropic.Anthropic(api_key=claude_api_key)

    minutes_prompt ='Please reply in '\
        + selected_langage +\
        '. Your task is to review the provided meeting notes and create a concise summary that captures the essential information,'\
        'focusing on key takeaways and action items assigned to specific individuals or departments during the meeting.'\
        'Use clear and professional language, and organize the summary in a logical manner using appropriate formatting such as headings, subheadings, and bullet points.'\
        "Ensure that the summary is easy to understand and provides a comprehensive but succinct overview of the meeting's content,"\
        "with a particular focus on clearly indicating who is responsible for each action item."

    message = client.messages.create(
        model=claude_model,
        max_tokens=4000,
        temperature=0.5,
        system=minutes_prompt,
        messages=[{"role": "user", "content": [{"type": "text", "text": "Meeting notes:" + decoded_text}]}]
    )
    
    generated_content = message.content[0].text
    st.write(generated_content)
    with open(minutes_file_path, "w") as f:
        f.write(generated_content)

def convert_movie_to_text(video_path):
    audio_dir = "tmp-sound"
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)
    output_audio_path = os.path.join(audio_dir, "temp_audio.mp3")

    video = VideoFileClip(video_path)
    video.audio.write_audiofile(output_audio_path)

    model_size = "large-v3"
    model = WhisperModel(model_size, device="cpu", compute_type="int8")

    segments, info = model.transcribe(
        output_audio_path,
        language="ja",
        beam_size=3,
        best_of=3,
        temperature=0,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=500),
    )

    print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

    for segment in segments:
        print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))

    segments = list(segments)

    st.write(segments)
    return segments

def display_chat_messages(messages, ai_model):
    full_response = ""
    with client.messages.stream(
        max_tokens=1024,
        messages=[{"role": m["role"], "content": m["content"]} for m in messages],
        model=ai_model,
    ) as stream:
        for text in stream.text_stream:
            full_response += str(text) if text is not None else ""
        return full_response

if "ai_model" not in st.session_state:
    st.session_state["ai_model"] = settings.AI_MODEL

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

st.set_page_config(
    page_title="議事録作成アプリ", 
    page_icon='icon.png',
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("議事録作成アプリ")

st.sidebar.markdown("# 処理内容")
option = st.sidebar.selectbox(
    "処理の種類を選択してください", ["メモから議事録作成", "動画から文字起こし"]
)

if option == "メモから議事録作成":
    st.sidebar.markdown("# メモから議事録作成")
    uploaded_file = st.sidebar.file_uploader("テキストファイルをアップロードしてください。", type="txt")
    langage_options = ["English", "Japanese"]
    selected_langage = st.sidebar.radio("select langage", langage_options)
    if st.sidebar.button("Generate"):
        st.markdown("## メモから議事録作成")
        with st.spinner("Generating..."):
            convert_text_to_minutes(uploaded_file, selected_langage, settings.ANTHROPIC_API_KEY, st.session_state["ai_model"])

elif option == "動画から文字起こし":
    st.sidebar.markdown("# 動画から文字起こし")
    video_path = st.sidebar.text_input('文字起こしをしたい動画のPathを入力してください。')
    if st.sidebar.button("Generate"):
        st.markdown("## 動画から文字起こし")
        with st.spinner("Generating..."):
            convert_movie_to_text(video_path)

if prompt := st.chat_input("何でも聞いてください。"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        full_response = display_chat_messages(st.session_state.messages, st.session_state["ai_model"])
        st.markdown(full_response)