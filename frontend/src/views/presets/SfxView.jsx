export default function SfxView({ submit }) {
  return (
    <form onSubmit={(event) => submit(event, '/generate/sfx')}>
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
  );
}
