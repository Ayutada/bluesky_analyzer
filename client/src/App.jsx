/* client/src/App.jsx */
import { useState } from 'react'
import './App.css' // Import styles

function App() {
  // --- State Definition ---
  // Principle: Data that changes on the UI needs to be defined as State
  const [handle, setHandle] = useState('scievents.bsky.social')
  const [lang, setLang] = useState('cn')
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState(null)
  const [error, setError] = useState('')

  // Multi-language dictionary (can be defined outside the component or in a separate file)
  const translations = {
    cn: {
      title: "BlueSky 人格分析器",
      subtitle: "输入您的 Handle，AI 将为您揭示 MBTI 与灵魂动物",
      btn: "开始分析",
      loading: "正在连接神经元...可能需要 10-20 秒",
      mbti: "MBTI 类型",
      animal: "灵魂动物",
      desc: "性格画像",
      alertInput: "请输入有效的 BlueSky Handle！",
    },
    jp: {
      title: "BlueSky 性格診断",
      subtitle: "Handleを入力して、AIがMBTIと動物占いを明らかにします",
      btn: "診断開始",
      loading: "ニューロン接続中... 10-20秒かかる場合があります",
      mbti: "MBTI タイプ",
      animal: "動物占い",
      desc: "性格プロフィール",
      alertInput: "有効なBlueSky Handleを入力してください！",
    },
    en: {
      title: "BlueSky Personality Analyzer",
      subtitle: "Enter your Handle, AI will reveal your MBTI & Spirit Animal",
      btn: "Analyze",
      loading: "Connecting neurons... may take 10-20 seconds",
      mbti: "MBTI Type",
      animal: "Spirit Animal",
      desc: "Portrait",
      alertInput: "Please enter a valid BlueSky Handle!",
    }
  }

  const t = translations[lang] // Current language package

  // --- Business Logic ---
  const handleAnalyze = async () => {
    if (!handle.trim()) {
      alert(t.alertInput)
      return
    }

    setLoading(true)
    setError('')
    setData(null) // Clear old results

    try {
      // Principle: Use fetch to make requests; path doesn't need http://localhost:5000 because proxy is configured
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ handle: handle, lang: lang })
      })

      const resData = await response.json()

      if (!response.ok) {
        throw new Error(resData.error || "请求失败")
      }

      // If successful, update data state; React will automatically render the result area
      setData(resData)
    } catch (err) {
      setError(err.message)
      alert("Error: " + err.message)
    } finally {
      setLoading(false)
    }
  }

  // --- View Rendering (JSX) ---
  return (
    <div className="container">
      <div className="glass-card">
        {/* Language Switch */}
        <div className="lang-switch">
          <button onClick={() => setLang('cn')} title="中文">🇨🇳</button>
          <button onClick={() => setLang('jp')} title="日本語">🇯🇵</button>
          <button onClick={() => setLang('en')} title="English">🇺🇸</button>
        </div>

        <h1 className="title">{t.title}</h1>
        <p className="subtitle">{t.subtitle}</p>

        {/* Input Area */}
        <div className="input-group">
          {/* Principle: Two-way binding; value shows state, onChange updates state */}
          <input
            type="text"
            placeholder="例如: scievents.bsky.social"
            value={handle}
            onChange={(e) => setHandle(e.target.value)}
          />
          <button onClick={handleAnalyze} disabled={loading}>
            {t.btn}
          </button>
        </div>

        {/* Loading State Rendering */}
        {loading && (
          <div className="loader" style={{ display: 'block' }}>
            <div className="spinner"></div>
            <p>{t.loading}</p>
          </div>
        )}

        {/* Result Rendering - Only display when data exists and is not loading */}
        {!loading && data && (
          <div id="result-section" style={{ display: 'block' }}>
            <div className="profile-header">
              <img
                src={data.profile.avatar || `https://ui-avatars.com/api/?name=${data.profile.handle}`}
                alt="Avatar"
                className="avatar"
              />
              <div className="profile-name">
                <h3>{data.profile.displayName || handle}</h3>
                <span>@{data.profile.handle}</span>
              </div>
            </div>

            <div className="result-cards">
              <div className="info-card">
                <div className="card-label">{t.mbti}</div>
                <div className="card-value">{data.analysis.mbti}</div>
              </div>
              <div className="info-card">
                <div className="card-label">{t.animal}</div>
                <div className="card-value">{data.analysis.animal}</div>
              </div>
            </div>

            <div className="analysis-text">
              <div className="card-label" style={{ textAlign: 'left', marginBottom: '1rem' }}>
                {t.desc}
              </div>
              <p>{data.analysis.description}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App