import { Download } from 'lucide-react';

const labels = {
  vocals: '人声',
  instrumental: '伴奏（合并）',
  bass: '贝斯',
  drums: '鼓组',
  other: '其他伴奏',
  converted_vocals: '换声后人声',
  final_song: '合成歌曲',
};

export default function JobResult({ job }) {
  if (!job) return null;

  return (
    <aside>
      <b>{job.message}</b>
      {job.error && <pre>{job.error}</pre>}
      {job.outputs?.map((output) => {
        const label = labels[output.name] || output.name;
        return (
          <div className="stem" key={output.name}>
            <b>{label}</b>
            <audio controls src={output.download} />
            <a href={output.download}>
              <Download />
              下载{label}
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
  );
}
