export default function TtsView({ submit }) {
  return (
    <form onSubmit={(event) => submit(event, '/tts')}>
      <h2>使用参考声音朗读</h2>
      <textarea name="text" required rows="8" placeholder="输入文字" />
      <input name="emotion_text" placeholder="情绪描述，可选" />
      <label>
        本人或已授权的参考音频
        <input type="file" name="voice" accept="audio/*" required />
      </label>
      <button className="go">开始生成</button>
    </form>
  );
}
