import { useEffect, useState } from 'react'
import { setUnauthorizedHandler } from './api/client'
import LoginPage from './LoginPage'
import Workspace from './Workspace'

type Session = { token: string; name: string }

// The token is kept in memory only: refreshing or closing the tab means signing in again.
function App() {
  const [session, setSession] = useState<Session | null>(null)
  const [notice, setNotice] = useState('')

  useEffect(() => {
    setUnauthorizedHandler(() => {
      setSession(null)
      setNotice('Your session ended. Sign in again.')
    })
  }, [])

  if (!session) {
    return (
      <LoginPage
        notice={notice}
        onLogin={(s: Session) => {
          setNotice('')
          setSession(s)
        }}
      />
    )
  }

  return (
    <>
      <header className="topbar">
        <span>GlycoVision · {session.name}</span>
        <button type="button" onClick={() => setSession(null)}>
          Sign out
        </button>
      </header>
      <Workspace token={session.token} />
    </>
  )
}

export default App