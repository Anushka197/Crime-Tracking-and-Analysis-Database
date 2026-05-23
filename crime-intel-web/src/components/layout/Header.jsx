import BharatFlag from '../ui/BharatFlag';
import NationalEmblem from '../ui/NationalEmblem';
import './Header.css';

const navLinks = ['ABOUT REGISTRY', 'CONTACT US', 'OFFICIAL NOTICE'];

export default function Header() {
  return (
    <header className="header">
      {/* Left — emblem + site title */}
      <div className="header__brand">
        <NationalEmblem size={40} />
        <div>
          <h1 className="header__title">CRIME RECORDS</h1>
          <p className="header__subtitle">Government of Bharat</p>
        </div>
      </div>

      {/* Right — nav + flag */}
      <nav className="header__nav">
        {navLinks.map((link, i) => (
          <span key={i} className="header__nav-item">
            <a href="#" className="header__nav-link" onClick={(e) => e.preventDefault()}>
              {link}
            </a>
          </span>
        ))}
        <div className="header__flag-wrapper">
          <BharatFlag />
        </div>
      </nav>
    </header>
  );
}
