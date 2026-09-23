# AI Audio Studio

独立的本地声音工作室。第一阶段实现 IndexTTS2 文字转人声、Seed-VC V2 长人声音色转换、任务状态和WAV下载。音乐与音效将在后续阶段接入。

仅可处理本人或已明确授权的声音，不得用于冒充、欺诈或未经授权的声音克隆。

## 为什么是独立仓库

声音模型与图片视频模型的PyTorch、Torchaudio、CUDA和Transformers依赖不同。两个声音模型也使用独立虚拟环境。未来需要统一入口时，让 ai_image_video_generator 调用本项目API即可，不必把依赖混在一起。

## 推荐目录

D:/AI/repos/ai_audio_studio
D:/AI/repos/index-tts
D:/AI/repos/seed-vc
D:/AI/models/IndexTTS-2
D:/AI/models/Seed-VC
D:/AI/venvs/audio-api
D:/AI/venvs/indextts
D:/AI/venvs/seed-vc

## IndexTTS2

源码：https://github.com/index-tts/index-tts
Hugging Face：https://huggingface.co/IndexTeam/IndexTTS-2
ModelScope：https://modelscope.cn/models/IndexTeam/IndexTTS-2

Windows建议使用Python 3.10。模型下载命令：

    indextts2 download --source modelscope --model-dir D:/AI/models/IndexTTS-2

模型目录至少需要 config.yaml、bpe.model、gpt.pth、s2mel.pth，官方CLI还会补齐辅助模型。

## Seed-VC V2

源码：https://github.com/Plachtaa/seed-vc
模型：https://huggingface.co/Plachta/Seed-VC/tree/main/v2

下载到 D:/AI/models/Seed-VC，最终应存在：

    D:/AI/models/Seed-VC/v2/ar_base.pth
    D:/AI/models/Seed-VC/v2/cfm_small.pth

国内可设置 HF_ENDPOINT=https://hf-mirror.com 后使用 huggingface_hub 的 snapshot_download。

## 配置与启动

复制 backend/.env.example 为 backend/.env 并修改实际路径。API环境只安装 backend/requirements.txt；IndexTTS2和Seed-VC分别按照其官方README安装到独立环境。

启动API：

    uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8001

启动前端：

    cd frontend
    npm install
    npm run dev

打开 http://localhost:5173 。

需要FFmpeg在PATH中。12GB显存建议一次只运行一个声音任务。模型文件不要提交到GitHub。

## 当前验证边界

CI验证FastAPI可以导入、React可以构建；不会下载数GB模型或执行GPU推理。首次真实生成需要在本地配置模型后验证。
