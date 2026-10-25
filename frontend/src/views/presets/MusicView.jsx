export default function MusicView({ submit }) {
  return (
    <form onSubmit={(event) => submit(event, '/generate/music')}>
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
  );
}
