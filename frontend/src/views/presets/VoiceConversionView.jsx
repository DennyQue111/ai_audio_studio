export default function VoiceConversionView({ submit }) {
  return (
    <form onSubmit={(event) => submit(event, '/voice-conversion')}>
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
  );
}
