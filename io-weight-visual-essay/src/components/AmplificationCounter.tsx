import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';

interface AmplificationCounterProps {
  totalBytesWritten: number;
  actualDataWritten: number;
  type: 'write' | 'read';
  label?: string;
}

const AmplificationCounter = ({
  totalBytesWritten,
  actualDataWritten,
  type,
  label,
}: AmplificationCounterProps) => {
  const [prevTotal, setPrevTotal] = useState(totalBytesWritten);
  const [pulsing, setPulsing] = useState(false);

  useEffect(() => {
    if (totalBytesWritten > prevTotal) {
      setPulsing(true);
      setTimeout(() => setPulsing(false), 300);
      setPrevTotal(totalBytesWritten);
    }
  }, [totalBytesWritten, prevTotal]);

  const amplificationFactor =
    actualDataWritten > 0
      ? (totalBytesWritten / actualDataWritten).toFixed(1)
      : '0.0';

  return (
    <motion.div
      className="amplification-counter"
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="amplification-label">
        {label || `${type === 'write' ? 'Write' : 'Read'} Amplification`}
      </div>
      <motion.div
        className={`amplification-value ${pulsing ? 'pulsing' : ''} ${parseFloat(amplificationFactor) > 5 ? 'critical' : ''}`}
        key={`amp-${totalBytesWritten}`}
      >
        {amplificationFactor}×
      </motion.div>
      <div className="amplification-detail">
        {totalBytesWritten} bytes written for {actualDataWritten} data
      </div>
    </motion.div>
  );
};

export default AmplificationCounter;
