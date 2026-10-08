import { Link } from "react-router-dom";
import "./Home.css";

export default function Home() {
  return (
    <div className="home">
      <section className="hero">
        <div className="hero-photo-credit">Photo: Carol M. Highsmith / Library of Congress — public domain</div>
        <div className="container hero-inner">
          <p className="eyebrow">New Haven, CT</p>
          <h1>Gear that actually fits how you live at Yale.</h1>
          <p className="hero-sub">
            Campus Customs builds a small, carefully made catalogue for students, families, and alumni —
            everyday layers, game-day pieces, and the occasional gift that doesn't feel like merch.
          </p>
          <div className="hero-actions">
            <Link to="/products" className="btn-primary">
              Browse the catalogue
            </Link>
            <Link to="/about" className="btn-secondary">
              Our story
            </Link>
          </div>
        </div>
      </section>

      <section className="features container">
        <div className="feature-card">
          <h3>Picked, not just printed</h3>
          <p>Every item is chosen for the kind of thing you'd actually wear again next week, not just once.</p>
        </div>
        <div className="feature-card">
          <h3>Sized honestly</h3>
          <p>Real stock counts per size, so what you see on the page is what's actually on the shelf.</p>
        </div>
        <div className="feature-card">
          <h3>Ask before you buy</h3>
          <p>Not sure about fit or color? The assistant in the corner knows the catalogue inside and out.</p>
        </div>
      </section>

      <section className="campus-gallery container">
        <div className="campus-photo">
          <img src="/images/yale/harkness-tower.jpg" alt="Harkness Tower, Yale University" loading="lazy" />
          <span className="campus-photo-caption">Harkness Tower</span>
        </div>
        <div className="campus-photo">
          <img src="/images/yale/sterling-library.jpg" alt="Sterling Memorial Library, Yale University" loading="lazy" />
          <span className="campus-photo-caption">Sterling Memorial Library</span>
        </div>
      </section>
    </div>
  );
}
