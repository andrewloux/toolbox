import { motion } from 'framer-motion';
import type { WorldType } from '../types';
import './TheChoice.css';

interface TheChoiceProps {
  onChoice: (world: WorldType) => void;
}

const TheChoice = ({ onChoice }: TheChoiceProps) => {
  return (
    <motion.div
      className="frame the-choice"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 1 }}
    >
      {/* Title */}
      <motion.h1
        className="choice-title"
        initial={{ y: 50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.3, duration: 0.8 }}
      >
        The Weight
        <br />
        <span className="accent-primary">of I/O</span>
      </motion.h1>

      {/* Subtitle */}
      <motion.blockquote
        className="choice-subtitle"
        initial={{ y: 30, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.6, duration: 0.8 }}
      >
        A database is not just code. It's a philosophy about the physics of storage.
        <br />
        Choose a world to build your document index.
      </motion.blockquote>

      {/* World choices */}
      <motion.div
        className="worlds-container"
        initial={{ y: 50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.9, duration: 0.8 }}
      >
        {/* The Citadel */}
        <motion.div
          className="world-card citadel"
          onClick={() => onChoice('citadel')}
          whileHover={{ scale: 1.05, y: -10 }}
          whileTap={{ scale: 0.98 }}
          transition={{ type: 'spring', stiffness: 300, damping: 20 }}
        >
          <div className="world-icon citadel-icon">
            {/* SVG Icon: Solid, structured citadel */}
            <svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
              <rect x="40" y="80" width="120" height="100" fill="currentColor" />
              <rect x="60" y="50" width="80" height="30" fill="currentColor" />
              <rect x="80" y="20" width="40" height="30" fill="currentColor" />
              <rect x="50" y="100" width="30" height="80" fill="var(--bg-dark)" />
              <rect x="120" y="100" width="30" height="80" fill="var(--bg-dark)" />
              <line x1="40" y1="120" x2="160" y2="120" stroke="var(--bg-dark)" strokeWidth="2" />
              <line x1="40" y1="140" x2="160" y2="140" stroke="var(--bg-dark)" strokeWidth="2" />
              <line x1="40" y1="160" x2="160" y2="160" stroke="var(--bg-dark)" strokeWidth="2" />
            </svg>
          </div>
          <h2 className="world-name">The Citadel</h2>
          <p className="world-description">
            Perfect order. Reads are instant. Writes pay the price of precision.
          </p>
          <div className="world-tech">RDBMS • B-Tree</div>
        </motion.div>

        {/* The Frontier */}
        <motion.div
          className="world-card frontier"
          onClick={() => onChoice('frontier')}
          whileHover={{ scale: 1.05, y: -10 }}
          whileTap={{ scale: 0.98 }}
          transition={{ type: 'spring', stiffness: 300, damping: 20 }}
        >
          <div className="world-icon frontier-icon">
            {/* SVG Icon: Chaotic asteroids and particles */}
            <svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
              <circle cx="100" cy="50" r="15" fill="currentColor" />
              <circle cx="60" cy="100" r="20" fill="currentColor" />
              <circle cx="140" cy="110" r="12" fill="currentColor" />
              <circle cx="90" cy="140" r="18" fill="currentColor" />
              <circle cx="150" cy="70" r="10" fill="currentColor" />
              <circle cx="40" cy="60" r="8" fill="currentColor" />
              <circle cx="120" cy="160" r="14" fill="currentColor" />
              <circle cx="70" cy="170" r="6" fill="currentColor" />
              {/* Energy lines */}
              <line x1="100" y1="50" x2="60" y2="100" stroke="currentColor" strokeWidth="1" opacity="0.5" />
              <line x1="60" y1="100" x2="90" y2="140" stroke="currentColor" strokeWidth="1" opacity="0.5" />
              <line x1="140" y1="110" x2="120" y2="160" stroke="currentColor" strokeWidth="1" opacity="0.5" />
            </svg>
          </div>
          <h2 className="world-name">The Frontier</h2>
          <p className="world-description">
            Chaotic freedom. Writes are instant. Reads hunt through the debris.
          </p>
          <div className="world-tech">NoSQL • LSM-Tree</div>
        </motion.div>
      </motion.div>
    </motion.div>
  );
};

export default TheChoice;
