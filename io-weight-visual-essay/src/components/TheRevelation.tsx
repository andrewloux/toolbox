import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import './TheRevelation.css';

interface TheRevelationProps {
  onComplete: () => void;
}

const TheRevelation = ({ onComplete }: TheRevelationProps) => {
  const [phase, setPhase] = useState<'fade-in' | 'question' | 'answer' | 'fade-out'>('fade-in');

  useEffect(() => {
    const sequence = async () => {
      // Fade in
      await sleep(1500);
      setPhase('question');

      // Show question
      await sleep(3500);
      setPhase('answer');

      // Show answer
      await sleep(4000);
      setPhase('fade-out');

      // Fade out and complete
      await sleep(1500);
      onComplete();
    };

    sequence();
  }, [onComplete]);

  return (
    <motion.div
      className="frame the-revelation"
      initial={{ opacity: 0 }}
      animate={{ opacity: phase === 'fade-out' ? 0 : 1 }}
      transition={{ duration: 1.5 }}
    >
      <div className="revelation-content">
        {/* Question */}
        {(phase === 'question' || phase === 'answer') && (
          <motion.div
            className="revelation-question"
            initial={{ opacity: 0, y: 50 }}
            animate={{
              opacity: phase === 'answer' ? 0.3 : 1,
              y: phase === 'answer' ? -30 : 0
            }}
            transition={{ duration: 1 }}
          >
            What if we were honest with the disk?
          </motion.div>
        )}

        {/* Answer */}
        {phase === 'answer' && (
          <motion.div
            className="revelation-answer"
            initial={{ opacity: 0, scale: 0.8, y: 50 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            transition={{
              type: 'spring',
              stiffness: 200,
              damping: 20,
              delay: 0.5
            }}
          >
            <div className="revelation-title">HONEST GEOMETRY</div>
            <div className="revelation-subtitle">The B-Tree</div>
          </motion.div>
        )}

        {/* Geometric accent */}
        <motion.div
          className="revelation-geometry"
          initial={{ opacity: 0, scale: 0 }}
          animate={{
            opacity: phase === 'answer' ? 0.2 : 0,
            scale: phase === 'answer' ? 1 : 0,
            rotate: phase === 'answer' ? 360 : 0
          }}
          transition={{ duration: 2 }}
        >
          <svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
            {/* B-Tree inspired geometric shape */}
            <g stroke="currentColor" strokeWidth="2" fill="none">
              {/* Root */}
              <circle cx="100" cy="40" r="10" />
              {/* Level 1 */}
              <line x1="100" y1="50" x2="70" y2="90" />
              <line x1="100" y1="50" x2="130" y2="90" />
              <circle cx="70" cy="100" r="10" />
              <circle cx="130" cy="100" r="10" />
              {/* Level 2 */}
              <line x1="70" y1="110" x2="50" y2="150" />
              <line x1="70" y1="110" x2="90" y2="150" />
              <line x1="130" y1="110" x2="110" y2="150" />
              <line x1="130" y1="110" x2="150" y2="150" />
              <circle cx="50" cy="160" r="8" />
              <circle cx="90" cy="160" r="8" />
              <circle cx="110" cy="160" r="8" />
              <circle cx="150" cy="160" r="8" />
            </g>
          </svg>
        </motion.div>
      </div>
    </motion.div>
  );
};

const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export default TheRevelation;
