import { motion } from 'framer-motion';
import type { WorldType } from '../types';

interface WorldToggleProps {
  currentWorld: WorldType;
  onToggle: (world: WorldType) => void;
}

const WorldToggle = ({ currentWorld, onToggle }: WorldToggleProps) => {
  return (
    <motion.div
      className="world-toggle"
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5 }}
    >
      <button
        className={`world-toggle-btn ${currentWorld === 'citadel' ? 'active' : ''}`}
        onClick={() => onToggle('citadel')}
      >
        The Citadel
      </button>
      <button
        className={`world-toggle-btn ${currentWorld === 'frontier' ? 'active' : ''}`}
        onClick={() => onToggle('frontier')}
      >
        The Frontier
      </button>
    </motion.div>
  );
};

export default WorldToggle;
