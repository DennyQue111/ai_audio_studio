import { useEffect, useState } from 'react';

export function useModels() {
  const [models, setModels] = useState();

  useEffect(() => {
    fetch('/api/models')
      .then((response) => response.json())
      .then(setModels)
      .catch(() => setModels({}));
  }, []);

  return models;
}
