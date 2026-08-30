import { useEffect, useMemo, useState } from 'react';
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  PolarAngleAxis,
  PolarGrid,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

const COLORS = ['#7c3aed', '#38bdf8', '#22c55e', '#f59e0b', '#ef4444', '#a855f7'];

const emptySnapshot = {
  schema_version: 1,
  timezone: 'Asia/Kolkata',
  generated_at: null,
  last_successful_analysis: null,
  analyzed_date: null,
  profile: { name: 'Developer', handle: '@developer', location: 'Remote', headline: 'Awaiting live GitHub analytics.' },
  current_genome: { Backend: 0, Frontend: 0, Data: 0, Algorithms: 0, DevOps: 0 },
  behavioral_genome: { Consistency: 0, Exploration: 0, Focus: 0, Persistence: 0 },
  daily_activity: [],
  repositories: [],
  technology_history: [],
  milestones: [],
  insights: [],
  data_quality: { commit_collection: 'pending', notes: 'Dashboard data is not available yet.' },
};

function App() {
  const [darkMode, setDarkMode] = useState(true);
  const [view, setView] = useState('overview');
  const [snapshot, setSnapshot] = useState(emptySnapshot);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedRepo, setSelectedRepo] = useState(null);
  const [selectedDay, setSelectedDay] = useState('');

  useEffect(() => {
    let active = true;
    async function load() {
      try {
        const response = await fetch('/dashboard/data.json', { cache: 'no-store' });
        if (!response.ok) {
          throw new Error('Dashboard data is not available yet.');
        }
        const data = await response.json();
        if (!active) return;
        setSnapshot(data);
        setSelectedRepo(data.repositories?.[0] ?? null);
        setSelectedDay(data.daily_activity?.[data.daily_activity.length - 1]?.date ?? '');
      } catch (err) {
        if (!active) return;
        setError(err.message || 'Unable to load the latest analytics data.');
        setSnapshot(emptySnapshot);
      } finally {
        if (active) setLoading(false);
      }
    }
    load();
    return () => { active = false; };
  }, []);

  const techData = useMemo(
    () => Object.entries(snapshot.current_genome ?? {}).map(([subject, value]) => ({ subject, value })),
    [snapshot]
  );

  const behaviorData = useMemo(
    () => Object.entries(snapshot.behavioral_genome ?? {}).map(([subject, value]) => ({ subject, value })),
    [snapshot]
  );

  const selectedDayData = useMemo(() => {
    if (!snapshot.daily_activity?.length) {
      return { date: selectedDay || 'No data', developer_commits: 0, repositories_touched: 0, pull_requests: 0, issues: 0, observed_push_events: null };
    }
    return snapshot.daily_activity.find((item) => item.date === selectedDay)
      ?? snapshot.daily_activity[snapshot.daily_activity.length - 1];
  }, [selectedDay, snapshot]);

  const repoHealthAverage = useMemo(() => {
    if (!snapshot.repositories?.length) return '0.0';
    const total = snapshot.repositories.reduce((sum, repo) => sum + Number(repo.health_score ?? repo.health ?? 0), 0);
    return (total / snapshot.repositories.length).toFixed(1);
  }, [snapshot]);

  const exportSnapshot = () => {
    const blob = new Blob([JSON.stringify(snapshot, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'developer-genome-dashboard.json';
    link.click();
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return <div className={darkMode ? 'theme-dark' : 'theme-light'}><div className="page-shell"><div className="card loading-card">Loading the latest GitHub activity data…</div></div></div>;
  }

  const hasData = Boolean(snapshot.repositories?.length || snapshot.daily_activity?.length || snapshot.current_genome);

  return (
    <div className={darkMode ? 'theme-dark' : 'theme-light'}>
      <div className="page-shell">
        <header className="topbar">
          <div>
            <div className="eyebrow">Developer Genome</div>
            <h1>{snapshot.profile?.name ?? 'Developer Genome'}</h1>
          </div>
          <div className="topbar-actions">
            <nav className="nav-pills">
              {['overview', 'daily', 'evolution', 'repositories', 'technologies', 'milestones', 'methodology'].map((key) => (
                <button key={key} className={view === key ? 'nav-btn active' : 'nav-btn'} onClick={() => setView(key)}>
                  {key.charAt(0).toUpperCase() + key.slice(1)}
                </button>
              ))}
            </nav>
            <button className="ghost-btn" onClick={exportSnapshot}>Export JSON</button>
            <button className="theme-toggle" onClick={() => setDarkMode((prev) => !prev)}>{darkMode ? 'Light mode' : 'Dark mode'}</button>
          </div>
        </header>

        {error && !hasData ? (
          <main className="card error-card">
            <h2>Data status</h2>
            <p>{error}</p>
            <p className="muted">The app is intentionally not using fake or stale fallback values. Run the daily GitHub Actions job or supply live data to populate the dashboard.</p>
          </main>
        ) : (
          <>
            {view === 'overview' && (
              <main className="dashboard">
                <section className="hero card">
                  <div>
                    <p className="muted">{snapshot.profile?.handle} • {snapshot.profile?.location}</p>
                    <h2>{snapshot.profile?.headline}</h2>
                    <div className="hero-metrics">
                      <div>
                        <span className="label">Last analyzed</span>
                        <strong>{snapshot.analyzed_date ?? 'Not available'}</strong>
                      </div>
                      <div>
                        <span className="label">7-day commits</span>
                        <strong>{snapshot.daily_activity.slice(-7).reduce((sum, day) => sum + Number(day.developer_commits ?? 0), 0)}</strong>
                      </div>
                      <div>
                        <span className="label">Repositories</span>
                        <strong>{snapshot.repositories.length}</strong>
                      </div>
                    </div>
                  </div>
                  <div className="score-ring">
                    <div className="ring-center">{Math.round(Object.values(snapshot.current_genome ?? {}).reduce((sum, value) => sum + Number(value || 0), 0) / 5 || 0)}</div>
                  </div>
                </section>

                <section className="stats-grid">
                  {[
                    { label: 'Developer commits', value: snapshot.daily_activity.slice(-30).reduce((sum, day) => sum + Number(day.developer_commits ?? 0), 0) },
                    { label: 'PRs', value: snapshot.daily_activity.reduce((sum, day) => sum + Number(day.pull_requests ?? 0), 0) },
                    { label: 'Issues', value: snapshot.daily_activity.reduce((sum, day) => sum + Number(day.issues ?? 0), 0) },
                    { label: 'Active repos', value: snapshot.repositories.length },
                  ].map((stat) => (
                    <article key={stat.label} className="card stat-card">
                      <span className="muted">{stat.label}</span>
                      <strong>{stat.value}</strong>
                    </article>
                  ))}
                </section>

                <section className="grid-two">
                  <article className="card chart-card">
                    <div className="section-head"><h3>Technical DNA</h3></div>
                    <div className="chart-wrap radar-wrap">
                      <ResponsiveContainer width="100%" height={300}>
                        <RadarChart data={techData} outerRadius="70%">
                          <PolarGrid stroke="rgba(148,163,184,0.4)" />
                          <PolarAngleAxis dataKey="subject" tick={{ fill: 'currentColor', fontSize: 11 }} />
                          <Radar dataKey="value" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.4} />
                          <Tooltip />
                        </RadarChart>
                      </ResponsiveContainer>
                    </div>
                  </article>

                  <article className="card chart-card">
                    <div className="section-head"><h3>Behavioral DNA</h3></div>
                    <div className="chart-wrap radar-wrap">
                      <ResponsiveContainer width="100%" height={300}>
                        <RadarChart data={behaviorData} outerRadius="70%">
                          <PolarGrid stroke="rgba(148,163,184,0.4)" />
                          <PolarAngleAxis dataKey="subject" tick={{ fill: 'currentColor', fontSize: 11 }} />
                          <Radar dataKey="value" stroke="#22c55e" fill="#22c55e" fillOpacity={0.4} />
                          <Tooltip />
                        </RadarChart>
                      </ResponsiveContainer>
                    </div>
                  </article>
                </section>

                <section className="grid-two">
                  <article className="card chart-card">
                    <div className="section-head"><h3>Activity trend</h3></div>
                    <div className="chart-wrap">
                      <ResponsiveContainer width="100%" height={260}>
                        <AreaChart data={snapshot.daily_activity}>
                          <defs>
                            <linearGradient id="activityFill" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="0%" stopColor="#7c3aed" stopOpacity={0.5} />
                              <stop offset="100%" stopColor="#7c3aed" stopOpacity={0.05} />
                            </linearGradient>
                          </defs>
                          <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.2)" />
                          <XAxis dataKey="date" tick={{ fontSize: 10 }} minTickGap={20} />
                          <YAxis allowDecimals={false} />
                          <Tooltip />
                          <Area type="monotone" dataKey="developer_commits" stroke="#7c3aed" fill="url(#activityFill)" />
                        </AreaChart>
                      </ResponsiveContainer>
                    </div>
                  </article>

                  <article className="card chart-card">
                    <div className="section-head"><h3>Language share</h3></div>
                    <div className="chart-wrap donut-wrap">
                      <ResponsiveContainer width="100%" height={260}>
                        <PieChart>
                          <Pie data={snapshot.technology_history?.[0]?.languages ?? []} dataKey="share" nameKey="name" innerRadius={50} outerRadius={80}>
                            {(snapshot.technology_history?.[0]?.languages ?? []).map((entry, index) => (
                              <Cell key={entry.name} fill={COLORS[index % COLORS.length]} />
                            ))}
                          </Pie>
                          <Tooltip />
                        </PieChart>
                      </ResponsiveContainer>
                    </div>
                  </article>
                </section>

                <section className="card repository-panel">
                  <div className="section-head"><h3>Recent repositories</h3></div>
                  <div className="repo-grid">
                    {snapshot.repositories.map((repo) => (
                      <button key={repo.name} className="repo-card repo-button" onClick={() => { setSelectedRepo(repo); setView('repositories'); }}>
                        <div className="repo-topline"><h4>{repo.name}</h4><span className="pill">{repo.health_score ?? repo.health ?? 0}</span></div>
                        <p>{repo.description || 'Repository activity'}</p>
                        <div className="repo-meta"><span>{repo.language || 'Unknown'}</span><span>{repo.stars ?? 0}★</span><span>{repo.commits ?? 0} commits</span></div>
                      </button>
                    ))}
                  </div>
                </section>
              </main>
            )}

            {view === 'daily' && (
              <main className="dashboard">
                <section className="card chart-card">
                  <div className="section-head"><h3>Daily Activity Explorer</h3></div>
                  <div className="day-controls">
                    <label>
                      <span className="label">Select date</span>
                      <input type="date" value={selectedDay} onChange={(e) => setSelectedDay(e.target.value)} />
                    </label>
                  </div>
                  <div className="hero-metrics">
                    <div><span className="label">Date</span><strong>{selectedDayData.date}</strong></div>
                    <div><span className="label">Developer commits</span><strong>{selectedDayData.developer_commits ?? selectedDayData.commits ?? 0}</strong></div>
                    <div><span className="label">Repositories touched</span><strong>{selectedDayData.repositories_touched ?? 0}</strong></div>
                    <div><span className="label">PRs</span><strong>{selectedDayData.pull_requests ?? 0}</strong></div>
                    <div><span className="label">Issues</span><strong>{selectedDayData.issues ?? 0}</strong></div>
                    <div><span className="label">Push evidence</span><strong>{selectedDayData.observed_push_events ?? 'Partial / unavailable'}</strong></div>
                  </div>
                  {Number(selectedDayData.developer_commits ?? selectedDayData.commits ?? 0) === 0 ? (
                    <div className="empty-state">NO COMMITS ON THIS DATE</div>
                  ) : (
                    <div className="repo-list">
                      {(snapshot.repositories || []).map((repo) => (
                        <div key={repo.name} className="repo-line">
                          <span>{repo.name}</span>
                          <span>{repo.commits ?? 0} commits</span>
                        </div>
                      ))}
                    </div>
                  )}
                </section>
              </main>
            )}

            {view === 'repositories' && (
              <main className="repo-page">
                <section className="card repo-detail-panel">
                  <div className="section-head"><h3>Repository details</h3><button className="ghost-btn" onClick={() => setView('overview')}>Back</button></div>
                  <div className="repo-detail-top">
                    <div>
                      <p className="muted">Repository</p>
                      <h2>{(selectedRepo ?? snapshot.repositories[0])?.name ?? 'No repository'}</h2>
                      <p className="lead-sm">{(selectedRepo ?? snapshot.repositories[0])?.description || 'Repository detail is unavailable until the next successful analysis.'}</p>
                    </div>
                    <div className="score-pill">Health {(selectedRepo ?? snapshot.repositories[0])?.health_score ?? (selectedRepo ?? snapshot.repositories[0])?.health ?? 0}</div>
                  </div>
                  <div className="repo-detail-grid">
                    <div className="repo-detail-box"><span className="label">Language</span><strong>{(selectedRepo ?? snapshot.repositories[0])?.language || 'Unknown'}</strong></div>
                    <div className="repo-detail-box"><span className="label">Commits</span><strong>{(selectedRepo ?? snapshot.repositories[0])?.commits ?? 0}</strong></div>
                    <div className="repo-detail-box"><span className="label">Stars</span><strong>{(selectedRepo ?? snapshot.repositories[0])?.stars ?? 0}</strong></div>
                    <div className="repo-detail-box"><span className="label">PRs</span><strong>{(selectedRepo ?? snapshot.repositories[0])?.pull_requests ?? 0}</strong></div>
                  </div>
                </section>
                <section className="card repo-list-panel">
                  <div className="section-head"><h3>All repositories</h3></div>
                  <div className="repo-list">
                    {(snapshot.repositories || []).map((repo) => (
                      <button key={repo.name} className={((selectedRepo ?? snapshot.repositories[0])?.name === repo.name) ? 'repo-line active' : 'repo-line'} onClick={() => setSelectedRepo(repo)}>
                        <span>{repo.name}</span>
                        <span>{repo.health_score ?? repo.health ?? 0}</span>
                      </button>
                    ))}
                  </div>
                </section>
              </main>
            )}

            {view === 'technologies' && (
              <main className="dashboard">
                <section className="card chart-card">
                  <div className="section-head"><h3>Technology evidence</h3></div>
                  <div className="repo-list">
                    {(snapshot.technology_history?.[0]?.languages ?? []).length ? (
                      (snapshot.technology_history?.[0]?.languages ?? []).map((tech) => (
                        <div key={tech.name} className="repo-line"><span>{tech.name}</span><span>{tech.share}%</span></div>
                      ))
                    ) : (
                      <div className="empty-state">Technology evidence will appear after a live GitHub analysis run.</div>
                    )}
                  </div>
                </section>
              </main>
            )}

            {view === 'milestones' && (
              <main className="dashboard">
                <section className="milestones">
                  {(snapshot.milestones || []).length ? (
                    snapshot.milestones.map((item) => (
                      <article key={item.title} className="card milestone-card">
                        <div className="dot" />
                        <div>
                          <h4>{item.title}</h4>
                          <small>{item.date}</small>
                          <p>{item.detail}</p>
                        </div>
                      </article>
                    ))
                  ) : (
                    <article className="card milestone-card"><div className="dot" /><div><h4>No milestones yet</h4><p>Milestones are generated only from real thresholds crossed in the historical analytics.</p></div></article>
                  )}
                </section>
              </main>
            )}

            {view === 'methodology' && (
              <main className="dashboard">
                <section className="card chart-card">
                  <h3>Methodology</h3>
                  <p className="lead-sm">This dashboard consumes generated public-safe data produced by the GitHub Actions pipeline. The workflow runs daily at 08:00 IST, targets the previous calendar date, and analyzes actual developer activity from the GitHub API.</p>
                  <ul className="method-list">
                    <li>Timezone: Asia/Kolkata; the reporting window is the full previous day from 00:00:00 to 23:59:59.999999 IST.</li>
                    <li>Commit collection uses since/until filters and author filtering; it does not count automation activity.</li>
                    <li>Push events remain separate from commit counts because one push can include multiple commits.</li>
                    <li>Genome scores are based on actual repository metadata, language statistics, topics, and historical activity rather than arbitrary constants.</li>
                    <li>Data quality is shown explicitly when a value is partial or unavailable.</li>
                  </ul>
                </section>
              </main>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default App;
