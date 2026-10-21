import { useState } from "react";

const MOCK = import.meta.env.DEV && import.meta.env.VITE_MOCK_AUTH === "true";

const MAX_ATTEMPTS = 5;
const STORAGE_KEY = "login_failed_attempts";
const LOCKED_MESSAGE = "Account Locked. Contact Administrator.";

function readAttempts() {
  try {
    return Number(localStorage.getItem(STORAGE_KEY)) || 0;
  } catch {
    return 0;
  }
}
function writeAttempts(n) {
  try {
    if (n > 0) localStorage.setItem(STORAGE_KEY, String(n));
    else localStorage.removeItem(STORAGE_KEY);
  } catch {
    
  }
}

export default function LoginPage({ apiUrl = "/api", onLogin, notice = "" }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [attempts, setAttempts] = useState(readAttempts);

  const locked = attempts >= MAX_ATTEMPTS;

  function lockOut() {
    writeAttempts(MAX_ATTEMPTS);
    setAttempts(MAX_ATTEMPTS);
    setPassword("");
  }

  function recordFailure() {
    const next = attempts + 1;
    writeAttempts(next);
    setAttempts(next);
    setPassword("");
    if (next < MAX_ATTEMPTS) {
      const left = MAX_ATTEMPTS - next;
      setError(
        `Username or password is incorrect. ${left} ${left === 1 ? "attempt" : "attempts"} left.`
      );
    }
  }

  async function submit(e) {
    e.preventDefault();
    if (locked) return;
    if (!username.trim() || !password) {
      setError("Enter your username and password.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      if (MOCK) {
        if (username.trim() === "demo" && password === "demo") {
          writeAttempts(0);
          onLogin({ token: "dev-token", name: "Demo user" });
        } else {
          recordFailure();
        }
        return;
      }

      const res = await fetch(`${apiUrl}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: username.trim(), password }),
      });

      if (res.status === 423 || res.status === 429) {
        lockOut();
        return;
      }
      if (res.status === 400 || res.status === 401 || res.status === 403) {
        recordFailure();
        return;
      }
      if (!res.ok) {
        setError("The sign-in service had a problem. Try again.");
        return;
      }

      const data = await res.json();
      writeAttempts(0);
      onLogin({ token: data.access_token, name: data.user?.name ?? username.trim() });
    } catch {
      
      setError("Couldn't reach the sign-in service. Check your connection and try again.");
      setPassword("");
    } finally {
      setLoading(false);
    }
  }

  if (locked) {
    return (
      <main className="lg">
        <style>{CSS}</style>
        <div className="lg-card">
          <h1>Sign in</h1>
          <div className="locked" role="alert">
            <strong>{LOCKED_MESSAGE}</strong>
          </div>
          {MOCK && (
            <button
              type="button"
              className="ghost"
              onClick={() => {
                writeAttempts(0);
                setAttempts(0);
                setError("");
              }}
            >
              Reset lockout (development only)
            </button>
          )}
        </div>
      </main>
    );
  }

  return (
    <main className="lg">
      <style>{CSS}</style>
      <form className="lg-card" onSubmit={submit} noValidate>
        <h1>Sign in</h1>
        <p className="sub">Diabetes risk assessment. For authorized clinical staff only.</p>

        {notice && <p className="notice" role="status">{notice}</p>}
        {MOCK && (
          <p className="notice">Development mode: sign in with username demo and password demo.</p>
        )}

        <label htmlFor="username">Username</label>
        <input
          id="username" autoComplete="username" autoFocus
          value={username} onChange={(e) => setUsername(e.target.value)}
          aria-invalid={!!error}
        />

        <label htmlFor="password">Password</label>
        <input
          id="password" type="password" autoComplete="current-password"
          value={password} onChange={(e) => setPassword(e.target.value)}
          aria-invalid={!!error}
        />

        {error && <p className="err" role="alert">{error}</p>}

        <button type="submit" disabled={loading}>
          {loading ? "Signing in…" : "Sign in"}
        </button>
      </form>
    </main>
  );
}

const CSS = `
.lg{--ink:#14232b;--mute:#5b6b73;--line:#d5dde1;--bg:#f4f7f8;--accent:#0d5c6e;--bad:#b3261e;
  font:16px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;color:var(--ink);background:var(--bg);
  min-height:100vh;display:grid;place-items:center;padding:24px}
.lg *{box-sizing:border-box}
.lg-card{width:100%;max-width:380px;background:#fff;border:1px solid var(--line);border-radius:8px;padding:28px}
.lg h1{font-size:1.5rem;margin:0 0 4px}
.sub{margin:0 0 20px;color:var(--mute);font-size:.95rem}
.lg label{display:block;font-size:.9rem;font-weight:550;margin:14px 0 4px}
.lg input{width:100%;height:44px;padding:0 12px;border:1px solid #9aa9b0;border-radius:6px;font:inherit}
.lg input:focus-visible,.lg button:focus-visible{outline:3px solid #7fc4d4;outline-offset:1px}
.lg [aria-invalid="true"]{border-color:var(--bad);background:#fff7f6}
.err{margin:12px 0 0;color:var(--bad);font-size:.9rem}
.notice{margin:0 0 4px;padding:10px 12px;background:#eaf3f5;border-radius:6px;font-size:.9rem}
.locked{margin:16px 0 0;padding:14px 16px;border-left:4px solid var(--bad);background:#fff7f6;color:var(--bad)}
.lg button{width:100%;height:46px;margin-top:20px;border:0;border-radius:6px;background:var(--accent);color:#fff;font:inherit;font-weight:600;cursor:pointer}
.lg button.ghost{background:transparent;border:1px solid #9aa9b0;color:var(--ink)}
.lg button:disabled{opacity:.6;cursor:progress}
`;
