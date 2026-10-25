export default function SeparationView({ submit }) {
  return (
    <form onSubmit={(event) => submit(event, '/audio-separation')}>
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
  );
}
