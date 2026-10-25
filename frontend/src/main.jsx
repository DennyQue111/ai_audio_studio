import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Mic2, AudioWaveform, Download, Music2, Sparkles, Volume2 } from 'lucide-react';
import './style.css';
const A = '/api';
function App() {
  const [tab, setTab] = useState('tts'),
    [models, setModels] = useState(),
    [job, setJob] = useState();
  useEffect(() => {
    fetch(A + '/models')
      .then((r) => r.json())
      .then(setModels);
  }, []);
  function poll(id) {
    fetch(A + '/jobs/' + id)
      .then((r) => r.json())
      .then((x) => {
        setJob(x);
        if (x.status === 'queued' || x.status === 'running') setTimeout(() => poll(id), 1200);
      });
  }
  async function send(e, url) {
    e.preventDefault();
    setJob({ message: '上传中' });
    let r = await fetch(A + url, { method: 'POST', body: new FormData(e.currentTarget) }),
      x = await r.json();
    if (!r.ok) return setJob({ status: 'failed', error: x.detail });
    poll(x.job_id);
  }
  return (
    <main>
      <header>
        <h1>AI Audio Studio</h1>
        <p>本地人声、音乐与音效生成</p>
      </header>
      <div className="models">
        {['indextts2', 'seed_vc'].map((k) => (
          <div key={k} className={models?.[k]?.ready ? 'ok' : 'bad'}>
            <b>{k}</b>
            <span>{models?.[k]?.ready ? '已就绪' : '未配置'}</span>
            <small>{models?.[k]?.models}</small>
          </div>
        ))}
        <div className={models?.comfyui?.online ? 'ok' : 'bad'}>
          <b>ComfyUI</b>
          <span>{models?.comfyui?.online ? '已连接' : '未连接'}</span>
          <small>
            {models?.comfyui?.qwen_voice_design_ready ? '人声已就绪' : '人声未就绪'}
            {' · '}
            {models?.comfyui?.stable_audio_music_ready ? '音乐已就绪' : '音乐待配置'}
            {' · '}
            {models?.comfyui?.stable_audio_sfx_ready ? '音效已就绪' : '音效待配置'}
            {' · '}
            {models?.comfyui?.audio_separation_ready ? '音频分离已就绪' : '音频分离节点未就绪'}
          </small>
        </div>
      </div>
      <nav>
        <button onClick={() => setTab('tts')} className={tab === 'tts' ? 'on' : ''}>
          <Mic2 />
          文字转人声
        </button>
        <button onClick={() => setTab('vc')} className={tab === 'vc' ? 'on' : ''}>
          <AudioWaveform />
          音色转换
        </button>
        <button
          onClick={() => setTab('voice_design')}
          className={tab === 'voice_design' ? 'on' : ''}
        >
          <Sparkles />
          提示词生成人声
        </button>
        <button onClick={() => setTab('music')} className={tab === 'music' ? 'on' : ''}>
          <Music2 />
          提示词生成音乐
        </button>
        <button onClick={() => setTab('sfx')} className={tab === 'sfx' ? 'on' : ''}>
          <Volume2 />
          提示词生成音效
        </button>
        <button onClick={() => setTab('separation')} className={tab === 'separation' ? 'on' : ''}>
          <AudioWaveform />
          音频分离
        </button>
      </nav>
      {tab === 'tts' ? (
        <form onSubmit={(e) => send(e, '/tts')}>
          <h2>使用参考声音朗读</h2>
          <textarea name="text" required rows="8" placeholder="输入文字" />
          <input name="emotion_text" placeholder="情绪描述，可选" />
          <label>
            本人或已授权的参考音频
            <input type="file" name="voice" accept="audio/*" required />
          </label>
          <button className="go">开始生成</button>
        </form>
      ) : tab === 'voice_design' ? (
        <form onSubmit={(e) => send(e, '/generate/voice-design')}>
          <h2>根据提示词设计人声</h2>
          <label>
            需要朗读的内容
            <textarea name="text" required rows="4" placeholder="输入要合成的台词或旁白" />
          </label>
          <label>
            人声提示词
            <textarea
              name="voice_description"
              required
              rows="5"
              placeholder="描述音色、年龄感、语气、情绪和说话节奏，例如：年轻的成年女性，温柔亲切，普通话清晰自然，语速舒缓"
            />
          </label>
          <button className="go">生成试听人声</button>
        </form>
      ) : tab === 'music' ? (
        <form onSubmit={(e) => send(e, '/generate/music')}>
          <h2>根据提示词生成音乐</h2>
          <textarea
            name="prompt"
            required
            rows="6"
            placeholder="例如：温暖舒缓的电影感钢琴与弦乐，渐进铺陈，无人声。英文提示词通常更稳定。"
          />
          <label>
            时长（秒，1–120）
            <input type="number" name="duration" min="1" max="120" defaultValue="15" required />
          </label>
          <small>Stable Audio 3 Small 最长支持 120 秒；较长音频会增加生成时间和显存占用。</small>
          <button className="go">生成音乐</button>
        </form>
      ) : tab === 'sfx' ? (
        <form onSubmit={(e) => send(e, '/generate/sfx')}>
          <h2>根据提示词生成音效</h2>
          <textarea
            name="prompt"
            required
            rows="6"
            placeholder="例如：清脆的玻璃风铃轻响，带一点空灵的闪光质感，随后自然淡出；无音乐、无人声。"
          />
          <label>
            时长（秒，1–120）
            <input type="number" name="duration" min="1" max="120" defaultValue="15" required />
          </label>
          <button className="go">生成音效</button>
        </form>
      ) : tab === 'separation' ? (
        <form onSubmit={(e) => send(e, '/audio-separation')}>
          <h2>分离人声与伴奏</h2>
          <label>
            上传歌曲或混合音频
            <input type="file" name="audio" accept="audio/*,.wav,.mp3,.flac,.m4a,.ogg" required />
          </label>
          <small>
            输出人声、合并伴奏，以及贝斯、鼓、其他伴奏三条分轨。此模型不是专门的音效分离器，环境声/音效可能混在其他伴奏或人声里。
          </small>
          <button className="go">开始分离</button>
        </form>
      ) : (
        <form onSubmit={(e) => send(e, '/voice-conversion')}>
          <h2>长人声音色转换</h2>
          <label>
            原始人声
            <input type="file" name="source" accept="audio/*" required />
          </label>
          <label>
            本人或已授权的参考声音
            <input type="file" name="reference" accept="audio/*" required />
          </label>
          <button className="go">开始转换</button>
        </form>
      )}
      {job && (
        <aside>
          <b>{job.message}</b>
          {job.error && <pre>{job.error}</pre>}
          {job.outputs?.map((output) => {
            const labels = {
              vocals: '人声',
              instrumental: '伴奏（合并）',
              bass: '贝斯',
              drums: '鼓组',
              other: '其他伴奏',
            };
            return (
              <div className="stem" key={output.name}>
                <b>{labels[output.name] || output.name}</b>
                <audio controls src={output.download} />
                <a href={output.download}>
                  <Download />
                  下载{labels[output.name] || output.name}
                </a>
              </div>
            );
          })}
          {job.download && (
            <>
              <audio controls src={job.download} />
              <a href={job.download}>
                <Download />
                下载音频
              </a>
            </>
          )}
        </aside>
      )}
      <footer>只处理本人或已明确授权的声音。</footer>
    </main>
  );
}
createRoot(document.getElementById('root')).render(<App />);
