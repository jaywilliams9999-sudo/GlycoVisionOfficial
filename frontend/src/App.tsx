import Workspace from './Workspace'

// No sign-in yet: the backend has no /auth/login. Swap in LoginPage once it does.
function App() {
  return <Workspace token="" />
}

export default App