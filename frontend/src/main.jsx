import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';
import { AudioWaveform, Mic2, Music2, Sparkles, Volume2 } from 'lucide-react';
import { useJob } from './shared/useJob';
import { useModels } from './shared/useModels';
import JobResult from './shared/JobResult';
import TtsView from './views/presets/TtsView';
import VoiceConversionView from './views/presets/VoiceConversionView';
import VoiceDesignView from './views/presets/VoiceDesignView';
import MusicView from './views/presets/MusicView';
import SfxView from './views/presets/SfxView';
import SeparationView from './views/presets/SeparationView';
import SongVoiceSwapView from './views/features/SongVoiceSwapView';
import './style.css';

const presetViews = [
  { id: 'tts', label: '文字转人声', icon: Mic2, Component: TtsView },
  { id: 'vc', label: '音色转换', icon: AudioWaveform, Component: VoiceConversionView },
  { id: 'voice_design', label: '提示词生成人声', icon: Sparkles, Component: VoiceDesignView },
  { id: 'music', label: '提示词生成音乐', icon: Music2, Component: MusicView },
  { id: 'sfx', label: '提示词生成音效', icon: Volume2, Component: SfxView },
  { id: 'separation', label: '音频分离', icon: AudioWaveform, Component: SeparationView },
];

function App() {
  const [section, setSection] = useState('presets');
  const [preset, setPreset] = useState('tts');
  const models = useModels();
  const { job, submit } = useJob();
  const currentPreset = presetViews.find((view) => view.id === preset) || presetViews[0];
  const View = section === 'features' ? SongVoiceSwapView : currentPreset.Component;

  return (
    <main>
      <header>
        <h1>AI Audio Studio</h1>
        <p>本地声音生成、编辑与处理</p>
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
      <nav aria-label="主导航">
        <button onClick={() => setSection('presets')} className={section === 'presets' ? 'on' : ''}>
          预设
        </button>
        <button
          onClick={() => setSection('features')}
          className={section === 'features' ? 'on' : ''}
        >
          功能
        </button>
      </nav>
      {section === 'presets' ? (
        <nav className="subnav" aria-label="预设页签">
          {presetViews.map(({ id, label, icon: Icon }) => (
            <button key={id} onClick={() => setPreset(id)} className={preset === id ? 'on' : ''}>
              <Icon />
              {label}
            </button>
          ))}
        </nav>
      ) : (
        <nav className="subnav" aria-label="功能页签">
          <button className="on">
            <AudioWaveform />
            歌曲换声
          </button>
        </nav>
      )}
      <View submit={submit} />
      <JobResult job={job} />
      <footer>只处理本人或已明确授权的声音。</footer>
    </main>
  );
}
createRoot(document.getElementById('root')).render(<App />);
