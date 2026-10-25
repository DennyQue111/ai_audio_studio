import { useState } from 'react';

const API = '/api';

export function useJob() {
  const [job, setJob] = useState();

  async function poll(id) {
    const response = await fetch(`${API}/jobs/${id}`);
    const current = await response.json();
    setJob(current);
    if (current.status === 'queued' || current.status === 'running') {
      window.setTimeout(() => poll(id), 1200);
    }
  }

  async function submit(event, endpoint) {
    event.preventDefault();
    setJob({ message: '上传中' });
    try {
      const response = await fetch(`${API}${endpoint}`, {
        method: 'POST',
        body: new FormData(event.currentTarget),
      });
      const result = await response.json();
      if (!response.ok) {
        setJob({ status: 'failed', error: result.detail });
        return;
      }
      poll(result.job_id);
    } catch (error) {
      setJob({ status: 'failed', error: error.message || '请求失败，请检查后端服务' });
    }
  }

  return { job, submit };
}
