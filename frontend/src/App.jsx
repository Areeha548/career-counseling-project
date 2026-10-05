const steps = [
  {
    number: '01',
    title: 'Take Assessment',
    description: 'Share your interests, strengths, and the kind of work that inspires you.',
  },
  {
    number: '02',
    title: 'Discover Your Career',
    description: 'Explore career paths that fit your unique strengths and ambitions.',
  },
  {
    number: '03',
    title: 'Follow Your Roadmap',
    description: 'Build in-demand skills with a clear, manageable learning plan.',
  },
  {
    number: '04',
    title: 'Become Career Ready',
    description: 'Track your progress and take confident steps toward your next role.',
  },
]

const features = [
  {
    icon: '◎',
    title: 'Career Assessment',
    description: 'Get to know your strengths, interests, and work preferences.',
  },
  {
    icon: '↗',
    title: 'Personalized Roadmaps',
    description: 'See the practical steps that can move you toward your goal.',
  },
  {
    icon: '✳',
    title: 'Daily Learning Tasks',
    description: 'Make steady progress with small, focused learning activities.',
  },
  {
    icon: '▥',
    title: 'Progress Tracking',
    description: 'Celebrate milestones and see how far you have come.',
  },
  {
    icon: '✦',
    title: 'AI Career Mentor',
    description: 'Get supportive guidance as you explore your next steps.',
  },
]

function BrandMark() {
  return <span className="brand-mark" aria-hidden="true">✦</span>
}

function ButtonLink({ children, href, secondary = false }) {
  return (
    <a className={`button${secondary ? ' button-secondary' : ''}`} href={href}>
      {children}
      {!secondary && <span aria-hidden="true">→</span>}
    </a>
  )
}

function SectionHeading({ eyebrow, title, description }) {
  return (
    <div className="section-heading">
      <p className="eyebrow">{eyebrow}</p>
      <h2>{title}</h2>
      <p className="section-description">{description}</p>
    </div>
  )
}

function RoadmapPreview() {
  return (
    <div className="preview-wrap" aria-label="Example career roadmap preview">
      <div className="preview-orbit orbit-one" />
      <div className="preview-orbit orbit-two" />
      <div className="roadmap-card">
        <div className="roadmap-card-top">
          <span className="card-label"><span className="status-dot" /> YOUR CAREER SNAPSHOT</span>
          <span className="more-dots" aria-hidden="true">···</span>
        </div>
        <div className="career-match">
          <div className="career-icon">✳</div>
          <div>
            <p className="muted-label">A path to explore</p>
            <h3>UX Designer</h3>
          </div>
          <span className="match-score">92%<small> match</small></span>
        </div>
        <div className="divider" />
        <div className="roadmap-heading"><span>YOUR ROADMAP</span><span>3 milestones</span></div>
        <div className="roadmap-list">
          <div className="roadmap-item complete"><span className="milestone-icon">✓</span><div><strong>Know your strengths</strong><small>Assessment complete</small></div></div>
          <div className="roadmap-item active"><span className="milestone-icon">2</span><div><strong>Learn design foundations</strong><small>Next step · 3 short lessons</small></div></div>
          <div className="roadmap-item"><span className="milestone-icon">3</span><div><strong>Build your first portfolio</strong><small>Coming up</small></div></div>
        </div>
        <div className="card-progress"><span><i /></span><small>1 of 3 milestones</small></div>
      </div>
      <div className="floating-note"><span>✦</span><div><strong>Made for your next step</strong><small>A plan that feels doable</small></div></div>
    </div>
  )
}

function App() {
  return (
    <>
      <header className="site-header">
        <nav className="navbar container" aria-label="Main navigation">
          <a className="brand" href="#home"><BrandMark /><span>AI Career <b>Mentor</b></span></a>
          <div className="nav-links">
            <a className="nav-active" href="#home">Home</a>
            <a href="#how-it-works">How It Works</a>
            <a href="#features">Features</a>
          </div>
          <div className="nav-actions">
            <a className="login-link" href="#get-started">Login</a>
            <ButtonLink href="#get-started">Get Started</ButtonLink>
          </div>
        </nav>
      </header>

      <main>
        <section className="hero" id="home">
          <div className="container hero-grid">
            <div className="hero-copy">
              <div className="hero-badge"><span>✦</span> YOUR NEXT CHAPTER STARTS HERE</div>
              <h1>Find your direction.<br /><span>Build your future.</span></h1>
              <p className="hero-description">Discover careers that fit who you are, then follow a personalized path to build the skills and confidence to get there.</p>
              <div className="hero-actions">
                <ButtonLink href="#get-started">Get Started</ButtonLink>
                <ButtonLink href="#how-it-works" secondary>Explore Careers <span className="play-icon">▶</span></ButtonLink>
              </div>
              <div className="hero-note"><span className="avatar-stack"><i>A</i><i>M</i><i>J</i></span><span>Small steps today. <b>Big possibilities tomorrow.</b></span></div>
            </div>
            <RoadmapPreview />
          </div>
          <div className="hero-bottom container"><span>CAREER CLARITY, ONE STEP AT A TIME</span><span className="hero-bottom-line" /><span>01 — 04</span></div>
        </section>

        <section className="how-section section" id="how-it-works">
          <div className="container">
            <SectionHeading eyebrow="A CLEARER WAY FORWARD" title="Your journey, made simple." description="A little clarity can change everything. Start wherever you are and take it one step at a time." />
            <div className="steps-grid">
              {steps.map((step) => (
                <article className="step-card" key={step.number}>
                  <span className="step-number">{step.number}</span>
                  <div className="step-marker"><span /></div>
                  <h3>{step.title}</h3>
                  <p>{step.description}</p>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className="features-section section" id="features">
          <div className="container">
            <SectionHeading eyebrow="TOOLS FOR YOUR NEXT CHAPTER" title="Everything you need to move forward." description="From the first spark of an idea to the skills that bring it to life, find your support in one place." />
            <div className="features-grid">
              {features.map((feature, index) => (
                <article className={`feature-card${index === 4 ? ' feature-card-highlight' : ''}`} key={feature.title}>
                  <span className="feature-icon" aria-hidden="true">{feature.icon}</span>
                  <h3>{feature.title}</h3>
                  <p>{feature.description}</p>
                  <span className="feature-arrow" aria-hidden="true">↗</span>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className="cta-section" id="get-started">
          <div className="container cta-inner">
            <div className="cta-spark cta-spark-one">✳</div>
            <div className="cta-copy">
              <p className="eyebrow">YOUR FUTURE ISN'T ONE-SIZE-FITS-ALL</p>
              <h2>Your next chapter<br />starts with <span>one step.</span></h2>
              <p>Get a clearer picture of where you could go—and a practical plan to help you get there.</p>
              <ButtonLink href="#home">Start Your Journey</ButtonLink>
            </div>
            <div className="cta-art" aria-hidden="true">
              <div className="cta-ring ring-one" /><div className="cta-ring ring-two" />
              <span className="cta-star star-one">✦</span><span className="cta-star star-two">✳</span><span className="cta-star star-three">✦</span>
              <div className="cta-path"><span /><span /><span /><span /></div>
              <div className="cta-art-label">A future shaped by you</div>
            </div>
          </div>
        </section>
      </main>

      <footer className="site-footer">
        <div className="container footer-main">
          <a className="brand footer-brand" href="#home"><BrandMark /><span>AI Career <b>Mentor</b></span></a>
          <p>Helping you find your direction and take your next step with confidence.</p>
          <div className="footer-links"><a href="#home">Home</a><a href="#how-it-works">How It Works</a><a href="#features">Features</a></div>
        </div>
        <div className="container footer-bottom"><span>© 2026 AI Career Mentor</span><span>Thoughtfully built for your next chapter.</span></div>
      </footer>
    </>
  )
}

export default App
