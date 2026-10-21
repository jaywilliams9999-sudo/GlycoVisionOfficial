import { useEffect, useState } from 'react'
import { getModels } from './api/client'
import type { ModelInfo } from './api/types'

// Temporary connection check: lists the models the backend has loaded.
function App() {
  const [models, setModels] = useState<ModelInfo[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getModels()
      .then(setModels)
      .catch((e: Error) => setError(e.message))
  }, [])

  if (error) return <p>Backend not reachable: {error}</p>

  return (
    <main>
      <h1>GlycoVision</h1>
      <ul>
        {models.map((m) => (
          <li key={m.model_version}>
            {m.model_version}: {m.features.length} features, ROC-AUC {m.metrics.roc_auc}
          </li>
        ))}
      </ul>
    </main>
  )
}

export default App