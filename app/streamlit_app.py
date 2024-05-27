import os
import io
from moviepy.editor import VideoFileClip
import whisper
import anthropic
from openai import OpenAI
import streamlit as st
import platform
import subprocess

import settings

def convert_text_to_minutes(uploaded_file, selected_langage, ai_api_key, ai_model):
    whisper_dir = "whisper-text"
    if not os.path.exists(whisper_dir):
        os.makedirs(whisper_dir)
    whisper_file_path = os.path.join(whisper_dir, "whisper-output.txt")

    minutes_dir = "minutes-text"
    if not os.path.exists(minutes_dir):
        os.makedirs(minutes_dir)
    minutes_file_path = os.path.join(minutes_dir, "minutes-output.txt")
    
    if uploaded_file == "./tmp-video/temp_text.txt":
        with open(uploaded_file, 'r', encoding='utf-8') as file:
            decoded_text = file.read()
    else:
        decoded_text = uploaded_file.getvalue().decode("utf-8")

    minutes_prompt ='Please reply in '\
        + selected_langage +\
        '. Your task is to review the provided meeting notes and create a concise summary that captures the essential information,'\
        'focusing on key takeaways and action items assigned to specific individuals or departments during the meeting.'\
        'Use clear and professional language, and organize the summary in a logical manner using appropriate formatting such as headings, subheadings, and bullet points.'\
        'If technical conversations were held, describe them in detail and in a manner that is easy for anyone to understand.'\
        "Ensure that the summary is easy to understand and provides a comprehensive but succinct overview of the meeting's content,"\
        "with a particular focus on clearly indicating who is responsible for each action item."

    if ai_option == "ChatGPT":
        client = OpenAI(api_key=ai_api_key)
        completion = client.chat.completions.create(
            model=ai_model,
            messages=[
                {"role": "system", "content": minutes_prompt},
                {"role": "user", "content": "Meeting notes:" + decoded_text}
            ]
        )
        generated_content = str(completion.choices[0].message.content)
        st.write(generated_content)
        with open(minutes_file_path, "w") as f:
            f.write(generated_content)
    elif ai_option == "Claude":
        client = anthropic.Anthropic(api_key=ai_api_key)
        message = client.messages.create(
            model=ai_model,
            max_tokens=4000,
            temperature=0.5,
            system=minutes_prompt,
            messages=[{"role": "user", "content": [{"type": "text", "text": "Meeting notes:" + decoded_text}]}]
        )
        generated_content = message.content[0].text
        st.write(generated_content)
        with open(minutes_file_path, "w") as f:
            f.write(generated_content)

def convert_movie_to_text():
    # 現在のディレクトリ内のすべてのmp4ファイルを取得
    video_dir = "tmp-video"
    if not os.path.exists(video_dir):
        os.makedirs(video_dir)
    mp4_files = [file for file in os.listdir(video_dir) if file.endswith('.mp4')]

    audio_dir = "tmp-sound"
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)
    output_audio_path = os.path.join(audio_dir, "temp_audio.mp3")
    
    text_dir = "tmp-text"
    if not os.path.exists(text_dir):
        os.makedirs(text_dir)
    output_text_path = os.path.join(text_dir, "temp_text.txt")

    # テキストを格納するリスト
    text_lines = []

    # mp4ファイルを読み込み、データをテキストとして結合
    for file in mp4_files:
        mp4file_path = "./" + video_dir + "/" + file
        print(mp4file_path)
        video = VideoFileClip(mp4file_path)
        video.audio.write_audiofile(output_audio_path)

        model = whisper.load_model("small")
        result = model.transcribe(output_audio_path, verbose=True, language="ja")
        result["text"] = result["text"].replace(" ", "\n")

        st.write(result["text"])

        # ファイルの内容を追加
        text_lines.append(result["text"])
        # 区切りを追加
        text_lines.append("\n")

    # リストを結合して1つの文字列にする
    whisper_text = ''.join(text_lines)

    with open(output_text_path, "w") as f:
        f.write(whisper_text)

    return whisper_text

# def display_chat_messages(messages, ai_model):
#     full_response = ""
#     with client.messages.stream(
#         max_tokens=1024,
#         messages=[{"role": m["role"], "content": m["content"]} for m in messages],
#         model=ai_model,
#     ) as stream:
#         for text in stream.text_stream:
#             full_response += str(text) if text is not None else ""
#         return full_response

def split_movie(video_name):
    input_video_dir = "video"
    if not os.path.exists(input_video_dir):
        os.makedirs(input_video_dir)
    output_video_dir = "tmp-video"
    if not os.path.exists(output_video_dir):
        os.makedirs(output_video_dir)
    command = "ffmpeg -i "+ input_video_dir + "/" + video_name + " -c copy -map 0 -segment_time 600 -f segment -reset_timestamps 1 ./"+ output_video_dir +"/output_%03d.mp4"
    if platform.system() == 'Darwin':
        try:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            print("Command executed successfully:")
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print("Error executing command:")
            print(e.stderr)
    else:
        print("This script is not running on a Mac.") 

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

st.sidebar.markdown("## AIの選択")
ai_option = st.sidebar.selectbox(
    "AIの種類を選択してください", ["ChatGPT", "Claude"]
)
st.session_state["api_key"] = st.sidebar.text_input('API Keyを入力してください。', type="password")
model_option = st.sidebar.text_input('モデルの種類を入力してください。')

if ai_option == "ChatGPT":
    url = "https://platform.openai.com/docs/models/models"
    st.sidebar.markdown("[ChatGPT AI Models List](%s)" % url)

if ai_option == "Claude":
    url = "https://docs.anthropic.com/claude/docs/models-overview"
    st.sidebar.markdown("[Claude AI Models List](%s)" % url)
    
st.session_state["ai_model"] = model_option

if st.session_state["ai_model"] == model_option:
    st.sidebar.markdown("## 処理内容")
    option = st.sidebar.selectbox(
        "処理の種類を選択してください", ["議事録作成", "動画の分割", "動画から文字起こし", "メモから議事録作成"]
    )

if option == "議事録作成":
    st.sidebar.markdown("## 議事録作成")
    video_name = st.sidebar.text_input('分割したい動画の名前を入力してください。')
    langage_options = ["Japanese", "English"]
    selected_langage = st.sidebar.radio("select langage", langage_options)
    if st.sidebar.button("Generate"):
        st.markdown("### 議事録作成")
        with st.spinner("Generating..."):
            split_movie(video_name)
            convert_movie_to_text()
            convert_text_to_minutes("./tmp-video/temp_text.txt", selected_langage, st.session_state["api_key"], st.session_state["ai_model"])

elif option == "動画から文字起こし":
    st.sidebar.markdown("## 動画から文字起こし")
    video_path = st.sidebar.text_input('文字起こしをしたい動画のPathを入力してください。')
    if st.sidebar.button("Generate"):
        st.markdown("### 動画から文字起こし")
        with st.spinner("Generating..."):
            convert_movie_to_text()

elif option == "動画の分割":
    st.sidebar.markdown("## 動画の分割")
    video_name = st.sidebar.text_input('分割したい動画の名前を入力してください。')
    if st.sidebar.button("Generate"):
        st.markdown("### 動画の分割")
        with st.spinner("Generating..."):
            split_movie(video_name)

elif option == "メモから議事録作成":
    st.sidebar.markdown("## メモから議事録作成")
    uploaded_file = st.sidebar.file_uploader("テキストファイルをアップロードしてください。", type="txt")
    langage_options = ["Japanese", "English"]
    selected_langage = st.sidebar.radio("select langage", langage_options)
    if st.sidebar.button("Generate"):
        st.markdown("### メモから議事録作成")
        with st.spinner("Generating..."):
            convert_text_to_minutes(uploaded_file, selected_langage, st.session_state["api_key"], st.session_state["ai_model"])





# if prompt := st.chat_input("何でも聞いてください。"):
#     st.session_state.messages.append({"role": "user", "content": prompt})
#     with st.chat_message("user"):
#         st.markdown(prompt)

#     with st.chat_message("assistant"):
#         full_response = display_chat_messages(st.session_state.messages, st.session_state["ai_model"])
#         st.markdown(full_response)