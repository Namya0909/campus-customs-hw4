import "./About.css";

export default function About() {
  return (
    <div className="about container">
      <h1>About Campus Customs</h1>

      <div className="about-intro">
        <p className="lede">
          We started Campus Customs because most campus merch falls into two camps: stiff, oversized
          "spirit wear" that lives in a drawer, or generic blanks with a logo slapped on top. We wanted a
          middle ground — a small catalogue of pieces people actually reach for.
        </p>
        <div className="about-photo">
          <img src="/images/yale/harkness-tower.jpg" alt="Harkness Tower seen through the trees, Yale University" loading="lazy" />
        </div>
      </div>

      <div className="about-grid">
        <div>
          <h2>What we do</h2>
          <p>
            Every item we carry is photographed, measured, and sized against real stock before it ever
            shows up on the Products page. If a size says it's available, it's available — no
            "temporarily out of stock" surprises at checkout.
          </p>
        </div>
        <div>
          <h2>Who it's for</h2>
          <p>
            Students putting together a game-day outfit, families visiting for Parents' Weekend, alumni
            who want something sharper than their freshman-year hoodie — we try to carry something for
            each of them without the catalogue turning into an overwhelming scroll.
          </p>
        </div>
      </div>

      <div className="about-callout">
        <h2>Need help choosing?</h2>
        <p>
          Our assistant in the bottom-right corner can answer questions about color, fit, and what's
          currently in stock — open it any time while you browse.
        </p>
      </div>
    </div>
  );
}
