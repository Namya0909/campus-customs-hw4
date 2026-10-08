import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "./NavBar.css";

const links = [
  { to: "/", label: "Home", end: true },
  { to: "/products", label: "Products" },
  { to: "/about", label: "About Us" },
];

export default function NavBar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  async function handleLogout() {
    await logout();
    navigate("/");
  }

  return (
    <header className="navbar">
      <div className="navbar-inner container">
        <NavLink to="/" className="brand" end>
          <span className="brand-mark">CC</span>
          <span className="brand-text">Campus Customs</span>
        </NavLink>

        <nav className="nav-links">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.end}
              className={({ isActive }) => "nav-link" + (isActive ? " active" : "")}
            >
              {link.label}
            </NavLink>
          ))}
        </nav>

        <div className="nav-auth">
          {user ? (
            <>
              <span className="nav-greeting">Hi, {user.first_name ?? user.name}</span>
              <button className="nav-link nav-logout" onClick={handleLogout}>
                Log out
              </button>
            </>
          ) : (
            <>
              <NavLink to="/login" className="nav-link">
                Log in
              </NavLink>
              <NavLink to="/create-account" className="nav-cta">
                Create account
              </NavLink>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
