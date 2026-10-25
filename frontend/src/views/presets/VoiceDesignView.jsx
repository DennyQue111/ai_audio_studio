export default function VoiceDesignView({ submit }) {
  return (
    <form onSubmit={(event) => submit(event, '/generate/voice-design')}>
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
  );
}
