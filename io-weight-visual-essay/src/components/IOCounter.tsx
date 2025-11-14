import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';

interface IOCounterProps {
  writeCount: number;
  readCount: number;
}

const IOCounter = ({ writeCount, readCount }: IOCounterProps) => {
  const [prevWrite, setPrevWrite] = useState(writeCount);
  const [prevRead, setPrevRead] = useState(readCount);
  const [writePulsing, setWritePulsing] = useState(false);
  const [readPulsing, setReadPulsing] = useState(false);

  useEffect(() => {
    if (writeCount > prevWrite) {
      setWritePulsing(true);
      setTimeout(() => setWritePulsing(false), 300);
      setPrevWrite(writeCount);
    }
  }, [writeCount, prevWrite]);

  useEffect(() => {
    if (readCount > prevRead) {
      setReadPulsing(true);
      setTimeout(() => setReadPulsing(false), 300);
      setPrevRead(readCount);
    }
  }, [readCount, prevRead]);

  return (
    <motion.div
      className="io-counter"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="io-counter-item">
        <div className="io-counter-label">Write I/O</div>
        <motion.div
          className={`io-counter-value ${writePulsing ? 'pulsing' : ''}`}
          key={`write-${writeCount}`}
        >
          {writeCount}
        </motion.div>
      </div>
      <div className="io-counter-item">
        <div className="io-counter-label">Read I/O</div>
        <motion.div
          className={`io-counter-value ${readPulsing ? 'pulsing' : ''}`}
          key={`read-${readCount}`}
        >
          {readCount}
        </motion.div>
      </div>
    </motion.div>
  );
};

export default IOCounter;
