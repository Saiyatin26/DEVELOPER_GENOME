import { useMemo, useState } from 'react';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  ResponsiveContainer,
  LineChart,
  Line,
  Area,
  AreaChart,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import snapshot from '../../backend/data/analytics_snapshot.json';

const COLORS = ['#7c3aed', '#38bdf8', '#22c55e', '#f59e0b', '#ef4444', '#a855f7'];

function App() {
  const [darkMode, setDarkMode] = useState(true);
  const [currentView, setCurrentView] = useState('dashboard');
  const [selectedRepo, setSelectedRepo] = useState(snapshot.repositories[0]);
  const initialDay = snapshot.daily_activity[snapshot.daily_activity.length - 1]?.date ?? '';
  const [selectedDay, setSelectedDay] = useState(initialDay);

  const selectedDayData = useMemo(
    () => snapshot.daily_activity.find((item) => item.date === selectedDay)
      ?? snapshot.daily_activity[snapshot.daily_activity.length - 1]
      ?? { date: '', commits: 0, pull_requests: 0, issues_closed: 0, pushes: 0 },
    [selectedDay]
  );

  const repoHealthAverage = useMemo(
    () => (snapshot.repositories.reduce((sum, repo) => sum + repo.health, 0) / (snapshot.repositories.length || 1)).toFixed(1),
    []
  );

  const technicalData = useMemo(
    () => Object.entries(snapshot.technical_dna).map(([name, value]) => ({ subject: name, value })),
    []
  );

  const behaviorData = useMemo(
    () => Object.entries(snapshot.behavioral_dna).map(([name, value]) => ({ subject: name, value })),
    []
  );

  const exportSnapshot = () => {
    const blob = new Blob([JSON.stringify(snapshot, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'developer-genome-snapshot.json';
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className={darkMode ? 'theme-dark' : 'theme-light'}>
      <div className="page-shell">
        <header className="topbar">
          <div>
            <div className="eyebrow">Developer Genome</div>
            <h1>{snapshot.developer.name}</h1>
          </div>
          <div className="topbar-actions">
            <nav className="nav-pills">
              <button className={currentView === 'landing' ? 'nav-btn active' : 'nav-btn'} onClick={() => setCurrentView('landing')}>Landing</button>
              <button className={currentView === 'dashboard' ? 'nav-btn active' : 'nav-btn'} onClick={() => setCurrentView('dashboard')}>Dashboard</button>
              <button className={currentView === 'repo' ? 'nav-btn active' : 'nav-btn'} onClick={() => setCurrentView('repo')}>Repository</button>
            </nav>
            <button className="ghost-btn" onClick={exportSnapshot}>Export Snapshot</button>
            <button className="theme-toggle" onClick={() => setDarkMode((prev) => !prev)}>
              {darkMode ? 'Light mode' : 'Dark mode'}
            </button>
          </div>
        </header>

        {currentView === 'landing' && (
          <main className="landing-layout">
            <section className="hero card">
              <div>
                <p className="muted">{snapshot.developer.handle} • {snapshot.developer.location}</p>
                <h2>{snapshot.developer.headline}</h2>
                <p className="lead">
                  A continuously evolving developer profile built from GitHub signals, engineering behavior, project momentum, and historical growth.
                </p>
                <div className="hero-actions">
                  <button className="primary-btn" onClick={() => setCurrentView('dashboard')}>View analytics</button>
                  <button className="ghost-btn" onClick={() => setCurrentView('repo')}>Open repo deep dive</button>
                </div>
              </div>
              <div className="score-ring">
                <div className="ring-center">{snapshot.summary.overall_score}</div>
              </div>
            </section>

            <section className="feature-grid">
              {[
                { title: 'Technical DNA', text: 'Tracks backend, frontend, data, algorithms, and DevOps patterns over time.' },
                { title: 'Behavioral DNA', text: 'Measures consistency, exploration, focus, and persistence in everyday development work.' },
                { title: 'Project intelligence', text: 'Flags high-impact repositories, momentum changes, and growth milestones automatically.' },
              ].map((feature) => (
                <article key={feature.title} className="card feature-card">
                  <h3>{feature.title}</h3>
                  <p>{feature.text}</p>
                </article>
              ))}
            </section>
          </main>
        )}

        {currentView === 'dashboard' && (
          <main className="dashboard">
            <section className="hero card">
              <div>
                <p className="muted">{snapshot.developer.handle} • {snapshot.developer.location}</p>
                <h2>{snapshot.developer.headline}</h2>
                <div className="hero-metrics">
                  <div>
                    <span className="label">Overall score</span>
                    <strong>{snapshot.summary.overall_score}</strong>
                  </div>
                  <div>
                    <span className="label">Current streak</span>
                    <strong>{snapshot.summary.current_streak} days</strong>
                  </div>
                  <div>
                    <span className="label">Repositories</span>
                    <strong>{snapshot.summary.active_repositories}</strong>
                  </div>
                </div>
              </div>
              <div className="score-ring">
                <div className="ring-center">{snapshot.summary.overall_score}</div>
              </div>
            </section>

            <section className="stats-grid">
              {[
                { label: 'Total commits', value: snapshot.summary.total_commits },
                { label: 'Pull requests', value: snapshot.summary.pull_requests },
                { label: 'Issues closed', value: snapshot.summary.issues_closed },
                { label: 'Active repos', value: snapshot.summary.active_repositories },
              ].map((stat) => (
                <article key={stat.label} className="card stat-card">
                  <span className="muted">{stat.label}</span>
                  <strong>{stat.value}</strong>
                </article>
              ))}
            </section>

            <section className="card chart-card">
              <div className="section-head">
                <h3>Repository health overview</h3>
              </div>
              <div className="hero-metrics" style={{ marginTop: '18px' }}>
                <div>
                  <span className="label">Average health</span>
                  <strong>{repoHealthAverage}</strong>
                </div>
                <div>
                  <span className="label">Public repos</span>
                  <strong>{snapshot.repositories.filter((repo) => !repo.private).length}</strong>
                </div>
                <div>
                  <span className="label">Private repos</span>
                  <strong>{snapshot.repositories.filter((repo) => repo.private).length}</strong>
                </div>
                <div>
                  <span className="label">Tracked repos</span>
                  <strong>{snapshot.repositories.length}</strong>
                </div>
              </div>
            </section>

            <section className="card chart-card">
              <div className="section-head">
                <h3>Daily analytics</h3>
              </div>
              <div className="hero-metrics" style={{ marginTop: '18px' }}>
                <label className="repo-detail-box" style={{ minWidth: '220px' }}>
                  <span className="label">Selected day</span>
                  <input
                    type="date"
                    value={selectedDay}
                    min={snapshot.daily_activity[0]?.date ?? ''}
                    max={snapshot.daily_activity[snapshot.daily_activity.length - 1]?.date ?? ''}
                    onChange={(e) => setSelectedDay(e.target.value)}
                    style={{ width: '100%', padding: '10px 12px', borderRadius: '12px', background: 'rgba(15,23,42,0.35)', color: 'inherit', border: '1px solid rgba(148,163,184,0.2)' }}
                  />
                </label>
                <div>
                  <span className="label">Commits</span>
                  <strong>{selectedDayData.commits}</strong>
                </div>
                <div>
                  <span className="label">PRs</span>
                  <strong>{selectedDayData.pull_requests}</strong>
                </div>
                <div>
                  <span className="label">Issues closed</span>
                  <strong>{selectedDayData.issues_closed}</strong>
                </div>
                <div>
                  <span className="label">Pushes</span>
                  <strong>{selectedDayData.pushes}</strong>
                </div>
              </div>
            </section>

            <section className="card chart-card">
              <div className="section-head">
                <h3>What I did today</h3>
              </div>
              <div className="repo-list" style={{ marginTop: '18px' }}>
                {snapshot.today_activity.length === 0 ? (
                  <div className="muted">No GitHub activity recorded for today yet.</div>
                ) : (
                  snapshot.today_activity.map((entry) => (
                    <div key={entry.repo} className="repo-line">
                      <span>{entry.repo}</span>
                      <span>{entry.commits} commits • {entry.pushes} pushes</span>
                    </div>
                  ))
                )}
              </div>
            </section>

            <section className="card chart-card">
              <div className="section-head">
                <h3>Recent push summary</h3>
              </div>
              <div className="repo-list" style={{ marginTop: '18px' }}>
                {snapshot.repo_push_summary?.length === 0 ? (
                  <div className="muted">No push events found in the public GitHub history.</div>
                ) : (
                  snapshot.repo_push_summary?.map((entry) => (
                    <div key={entry.repo} className="repo-line">
                      <span>{entry.repo}</span>
                      <span>{entry.commits} commits in {entry.pushes} push(es)</span>
                    </div>
                  ))
                )}
              </div>
            </section>

            <section className="grid-two">
              <article className="card chart-card">
                <div className="section-head">
                  <h3>Technical DNA</h3>
                </div>
                <div className="chart-wrap radar-wrap">
                  <ResponsiveContainer width="100%" height={320}>
                    <RadarChart data={technicalData} outerRadius="75%">
                      <PolarGrid stroke="rgba(148,163,184,0.4)" />
                      <PolarAngleAxis dataKey="subject" tick={{ fill: 'currentColor', fontSize: 12 }} />
                      <Radar dataKey="value" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.45} />
                      <Tooltip />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>
              </article>

              <article className="card chart-card">
                <div className="section-head">
                  <h3>Behavioral DNA</h3>
                </div>
                <div className="chart-wrap radar-wrap">
                  <ResponsiveContainer width="100%" height={320}>
                    <RadarChart data={behaviorData} outerRadius="75%">
                      <PolarGrid stroke="rgba(148,163,184,0.4)" />
                      <PolarAngleAxis dataKey="subject" tick={{ fill: 'currentColor', fontSize: 12 }} />
                      <Radar dataKey="value" stroke="#22c55e" fill="#22c55e" fillOpacity={0.35} />
                      <Tooltip />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>
              </article>
            </section>

            <section className="grid-two">
              <article className="card chart-card">
                <div className="section-head">
                  <h3>Score evolution</h3>
                </div>
                <div className="chart-wrap">
                  <ResponsiveContainer width="100%" height={260}>
                    <AreaChart data={snapshot.history}>
                      <defs>
                        <linearGradient id="scoreFill" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#7c3aed" stopOpacity={0.5} />
                          <stop offset="100%" stopColor="#7c3aed" stopOpacity={0.05} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.2)" />
                      <XAxis dataKey="period" />
                      <YAxis domain={[50, 100]} />
                      <Tooltip />
                      <Area type="monotone" dataKey="score" stroke="#7c3aed" fill="url(#scoreFill)" />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </article>

              <article className="card chart-card">
                <div className="section-head">
                  <h3>Technology mix</h3>
                </div>
                <div className="chart-wrap donut-wrap">
                  <ResponsiveContainer width="100%" height={260}>
                    <PieChart>
                      <Pie data={snapshot.technology_mix} dataKey="value" nameKey="name" innerRadius={50} outerRadius={80} paddingAngle={3}>
                        {snapshot.technology_mix.map((entry, index) => (
                          <Cell key={entry.name} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </article>
            </section>

            <section className="grid-two">
              <article className="card chart-card">
                <div className="section-head">
                  <h3>Contribution momentum</h3>
                </div>
                <div className="chart-wrap">
                  <ResponsiveContainer width="100%" height={260}>
                    <LineChart data={snapshot.history}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.2)" />
                      <XAxis dataKey="period" />
                      <YAxis />
                      <Tooltip />
                      <Line type="monotone" dataKey="commits" stroke="#38bdf8" strokeWidth={3} dot={{ r: 4 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </article>

              <article className="card chart-card">
                <div className="section-head">
                  <h3>Repository health</h3>
                </div>
                <div className="chart-wrap">
                  <ResponsiveContainer width="100%" height={260}>
                    <BarChart data={snapshot.repositories.slice(0, 6)}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.2)" />
                      <XAxis dataKey="name" tick={{ fontSize: 10 }} interval={0} angle={-15} textAnchor="end" />
                      <YAxis domain={[0, 100]} />
                      <Tooltip />
                      <Bar dataKey="health" fill="#22c55e" radius={[6, 6, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </article>
            </section>

            <section className="card repository-panel">
              <div className="section-head">
                <h3>Repository signals</h3>
              </div>
              <div className="repo-grid">
                {snapshot.repositories.map((repo) => (
                  <button key={repo.name} className="repo-card repo-button" onClick={() => { setSelectedRepo(repo); setCurrentView('repo'); }}>
                    <div className="repo-topline">
                      <h4>{repo.name}</h4>
                      <span className="pill">{repo.health}</span>
                    </div>
                    <div className="tag-row" style={{ marginBottom: '10px' }}>
                      <span className="tag">{repo.private ? 'Private' : 'Public'}</span>
                      <span className="tag">{repo.commit_count ?? repo.commits} commits</span>
                    </div>
                    <p>{repo.description}</p>
                    <div className="repo-meta">
                      <span>{repo.language}</span>
                      <span>{repo.stars}★</span>
                      <span>{repo.days_since_last_activity}d ago</span>
                    </div>
                    <div className="tag-row">
                      {repo.technologies.map((tech) => (
                        <span key={tech} className="tag">{tech}</span>
                      ))}
                    </div>
                  </button>
                ))}
              </div>
            </section>

            <section className="milestones">
              {snapshot.milestones.map((milestone) => (
                <article key={milestone.title} className="card milestone-card">
                  <div className="dot" />
                  <div>
                    <h4>{milestone.title}</h4>
                    <small>{milestone.date}</small>
                    <p>{milestone.detail}</p>
                  </div>
                </article>
              ))}
            </section>
          </main>
        )}

        {currentView === 'repo' && (
          <main className="repo-page">
            <section className="card repo-detail-panel">
              <div className="section-head">
                <h3>Repository deep dive</h3>
                <button className="ghost-btn" onClick={() => setCurrentView('dashboard')}>Back to dashboard</button>
              </div>

              <div className="repo-detail-top">
                <div>
                  <p className="muted">Project focus</p>
                  <h2>{selectedRepo.name}</h2>
                  <p className="lead-sm">{selectedRepo.description}</p>
                </div>
                <div className="score-pill">Health {selectedRepo.health}</div>
              </div>

              <div className="repo-detail-grid">
                <div className="repo-detail-box">
                  <span className="label">Visibility</span>
                  <strong>{selectedRepo.private ? 'Private' : 'Public'}</strong>
                </div>
                <div className="repo-detail-box">
                  <span className="label">Primary language</span>
                  <strong>{selectedRepo.language}</strong>
                </div>
                <div className="repo-detail-box">
                  <span className="label">Total commits</span>
                  <strong>{selectedRepo.commit_count ?? selectedRepo.commits}</strong>
                </div>
                <div className="repo-detail-box">
                  <span className="label">Stars</span>
                  <strong>{selectedRepo.stars}</strong>
                </div>
                <div className="repo-detail-box">
                  <span className="label">Last commit</span>
                  <strong>{selectedRepo.last_commit}</strong>
                </div>
                <div className="repo-detail-box">
                  <span className="label">Active window</span>
                  <strong>{selectedRepo.days_since_last_activity} days</strong>
                </div>
              </div>

              <div className="tag-row large-gap">
                {selectedRepo.technologies.map((tech) => (
                  <span key={tech} className="tag">{tech}</span>
                ))}
              </div>
            </section>

            <section className="card repo-list-panel">
              <div className="section-head">
                <h3>Explore other repositories</h3>
              </div>
              <div className="repo-list">
                {snapshot.repositories.map((repo) => (
                  <button key={repo.name} className={repo.name === selectedRepo.name ? 'repo-line active' : 'repo-line'} onClick={() => setSelectedRepo(repo)}>
                    <span>{repo.name}</span>
                    <span>{repo.health}</span>
                  </button>
                ))}
              </div>
            </section>
          </main>
        )}
      </div>
    </div>
  );
}

export default App;
