export default function SongVoiceSwapView({ submit }) {
  return (
    <form onSubmit={(event) => submit(event, '/features/song-voice-swap')}>
      <h2>歌曲换声</h2>
      <label>
        原歌曲（包含原唱和伴奏）
        <input type="file" name="song" accept="audio/*,.wav,.mp3,.flac,.m4a,.ogg" required />
      </label>
      <label>
        新人声参考音频（本人或已授权）
        <input type="file" name="reference" accept="audio/*,.wav,.mp3,.flac,.m4a,.ogg" required />
      </label>
      <small>
        先分离歌曲的人声，再用新人声作为音色参考转换原唱轨，最后与伴奏合成。转换保留原人声的停顿和时间位置；不是把参考音频的演唱直接贴到歌曲里。
      </small>
      <button className="go">分离并换声</button>
    </form>
  );
}
