# AI Audio Studio

本地声音工作室，支持 IndexTTS2 参考音频文字转人声、Seed-VC V2 音色转换，以及通过现有 ComfyUI 生成描述音色、音乐和音效。

仅可处理本人或已明确授权的声音，不得用于冒充、欺诈或未经授权的声音克隆。

## 为什么是独立仓库

声音模型与图片视频模型的PyTorch、Torchaudio、CUDA和Transformers依赖不同，因此声音模型使用独立虚拟环境。ComfyUI 保持独立运行，本项目后端通过 ComfyUI HTTP API 提交工作流和取回结果，不会把两边的依赖混在一起。

## 推荐目录

D:/AI/repos/ai_audio_studio
D:/AI/repos/index-tts
D:/AI/repos/seed-vc
D:/AI/models/IndexTTS-2
D:/AI/models/Seed-VC
D:/AI/venvs/audio-api
D:/AI/venvs/indextts
D:/AI/venvs/seed-vc
D:/program/comfyUI/ComfyUI_windows_portable_nvidia/ComfyUI_windows_portable/ComfyUI

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

建议在 Windows PowerShell 中使用 Python 3.10。项目 API、IndexTTS2 和 Seed-VC 使用三个独立环境，避免 PyTorch、CUDA 和 Transformers 版本互相冲突。

首次配置项目 API 环境（在仓库根目录执行）：

    D:/AI/Python310/python.exe -m virtualenv .venv
    ./.venv/Scripts/python.exe -m pip install -r backend/requirements.txt

复制 `backend/.env.example` 为 `backend/.env`，并按本机实际路径修改。后端会固定读取该文件，不受启动目录影响。IndexTTS2 和 Seed-VC 分别按照各自官方 README 安装到独立环境。

启动API：

    ./.venv/Scripts/python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8002

另开一个 PowerShell 窗口启动前端：

    cd frontend
    npm install
    npm run dev

打开 http://127.0.0.1:5179 。开发服务器会把 `/api` 请求代理到 `http://127.0.0.1:8002`。如需使用其他前端端口，可设置 `PORT`；如需使用其他后端端口，可设置 `DENNY_BACKEND_PORT`。

后续启动时不需要再次安装依赖，只需分别运行上面的 API 和前端启动命令。

需要FFmpeg在PATH中。12GB显存建议一次只运行一个声音任务。模型文件不要提交到GitHub。

## ComfyUI 人声、音乐、音效与音频分离

本项目默认连接 `http://127.0.0.1:8188`，ComfyUI 根目录默认为：

    D:/program/comfyUI/ComfyUI_windows_portable_nvidia/ComfyUI_windows_portable/ComfyUI

如安装位置不同，可在 `backend/.env` 设置 `COMFYUI_URL` 和 `COMFYUI_ROOT`。前端提供提示词生成人声、音乐和音效页签。人声由现有 `qwen3-tts-comfyui` 的 VoiceDesign 节点生成；音乐和音效由 ComfyUI 内置 Stable Audio 3 Small 工作流生成。Small Music 和 Small SFX 的单次生成时长均为 1–120 秒（最长 2 分钟）；时间越长，生成通常越慢、显存占用越高。音乐与音效各用一个检查点，并共享 T5Gemma 文本编码器。工作流输出 FLAC，并将结果回传到本项目的输出目录。

“音频分离”页签通过已有的 `audio-separation-nodes-comfyui` 节点处理上传的歌曲，输出人声、合并伴奏，以及贝斯、鼓、其他伴奏四条来源轨。节点使用 HTDemucs/MUSDB+ 预训练模型；第一次运行时 ComfyUI 可能需要自动下载其权重。这里的“其他伴奏”不是独立音效轨，环境音或音效不保证能与乐器分开；当前主要保证人声与伴奏的分离。模型分离结果可能残留串音，质量取决于输入混音。

Stable Audio 权重需要先在 Hugging Face 登录并接受 Stability AI Community License 和 Gemma 使用条款；本项目不会代替用户接受条款。接受后下载以下模型并放置到 portable ComfyUI 对应目录：

- [Stable Audio 3 Small Music](https://huggingface.co/stabilityai/stable-audio-3-small-music) → `ComfyUI/models/checkpoints/stable_audio_3_small_music.safetensors`
- [Stable Audio 3 Small SFX](https://huggingface.co/stabilityai/stable-audio-3-small-sfx) → `ComfyUI/models/checkpoints/stable_audio_3_small_sfx.safetensors`
- [T5Gemma B-B UL2](https://huggingface.co/google/t5gemma-b-b-ul2) → `ComfyUI/models/text_encoders/t5gemma_b_b_ul2.safetensors`

两个 Small 检查点各约 2.27 GB，共享编码器约 1.19 GB。完成下载后重启 ComfyUI 以刷新模型列表，再从本项目提交任务。

## 当前验证边界

CI验证FastAPI可以导入、React可以构建；不会下载数GB模型或执行GPU推理。首次真实生成/分离需要在本地配置模型后验证。
