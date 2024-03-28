## README.md

### 概要
このアプリケーションは、議事録を作成するためのStreamlitアプリです。ユーザーはメモから議事録を作成したり、動画から文字起こしを行うことができます。

### 主な機能
- メモから議事録作成: テキストファイルをアップロードし、会議の要点やアクションアイテムを要約する機能
- 動画から文字起こし: 動画ファイルのパスを入力し、音声をテキストに変換する機能

### 使用言語
- English
- Japanese

### 環境変数
.envを作成し、記載してください。  
- ANTHROPIC_API_KEY=sk-ant-XXXXXXXXXXXXXXXX
- AI_MODEL=claude-3-sonnet-20240229

### 処理内容
- ユーザーは処理の種類を選択し、対応するアクションを実行できます。
- メモから議事録作成を選択した場合、テキストファイルをアップロードし、要約を生成します。
- 動画から文字起こしを選択した場合、動画ファイルのパスを入力し、音声をテキストに変換します。

### 実行コマンド
```bash
# 動画格納用ディレクトリの作成
mkdir ./video/
### 変換したい動画を ./video/ に配置する。 ###

# .envファイルの作成
echo "ANTHROPIC_API_KEY=sk-ant-XXXXXXXXXXXXXXXX" >> .env
echo "`cat .env`" # 改行用
echo "AI_MODEL=claude-3-sonnet-20240229" >> .env

# コンテナのビルドと実行
docker build ./ -t mutite-genarete-app
docker compose up -d 

### localhost:8501へブラウザでアクセスする ###

### 動画変換時のPathは、./video/{対象の動画} とする ###
### 議事録作成時は、ローカルPCからアップロードする ###
```