import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { LSMState, DataChip, SSTable } from '../types';
import './TheFrontier.css';

interface TheFrontierProps {
  state: LSMState;
  updateState: (updater: (prev: LSMState) => LSMState) => void;
  onShowDashboard: () => void;
}

const sampleKeys = ['apple', 'banana', 'cherry', 'date', 'elderberry', 'fig', 'grape', 'honey', 'iris', 'jackfruit'];

const TheFrontier = ({ state, updateState, onShowDashboard }: TheFrontierProps) => {
  const [statusMessage, setStatusMessage] = useState<string>('');
  const [targetSSTableId, setTargetSSTableId] = useState<string | null>(null);
  const [isAnimating, setIsAnimating] = useState(false);
  const [huntingSequence, setHuntingSequence] = useState<string[]>([]);

  const showStatus = (message: string, duration = 2000) => {
    setStatusMessage(message);
    setTimeout(() => setStatusMessage(''), duration);
  };

  // Perform write operation
  const handleWrite = async () => {
    if (isAnimating) return;
    setIsAnimating(true);

    const key = sampleKeys[Math.floor(Math.random() * sampleKeys.length)];
    const chip: DataChip = {
      id: `chip-${Date.now()}`,
      key,
      value: `Value for ${key}`,
      timestamp: Date.now(),
    };

    // PHASE 1: ABSORB into Memtable
    showStatus(`Absorbing "${key}" into Memtable...`, 800);

    await sleep(800);

    updateState(prev => {
      const newData = [...prev.memtable.data, chip];
      const isFull = newData.length >= prev.memtable.capacity;

      return {
        ...prev,
        memtable: {
          ...prev.memtable,
          data: newData,
          isFull,
        },
      };
    });

    await sleep(500);

    // Check if memtable is full
    if (state.memtable.data.length + 1 >= state.memtable.capacity) {
      // PHASE 2: FLUSH
      await handleFlush();
    } else {
      showStatus('Write complete! No disk I/O.', 1500);
      await sleep(1500);
    }

    setIsAnimating(false);
  };

  // Flush memtable to SSTable
  const handleFlush = async () => {
    showStatus('Memtable full! Flushing to disk...', 2000);

    await sleep(1500);

    updateState(prev => {
      const newSSTable: SSTable = {
        id: `sstable-${Date.now()}`,
        level: 0,
        data: [...prev.memtable.data].sort((a, b) => a.key.localeCompare(b.key)),
        minKey: prev.memtable.data.reduce((min, d) => (d.key < min ? d.key : min), prev.memtable.data[0].key),
        maxKey: prev.memtable.data.reduce((max, d) => (d.key > max ? d.key : max), prev.memtable.data[0].key),
        createdAt: Date.now(),
      };

      return {
        ...prev,
        memtable: {
          ...prev.memtable,
          data: [],
          isFull: false,
        },
        sstables: [newSSTable, ...prev.sstables],
        writeIOCount: prev.writeIOCount + 1,
        writeHistory: [...prev.writeHistory, prev.writeIOCount + 1],
      };
    });

    await sleep(1500);
    showStatus('Flush complete! SSTable written to L0.', 1500);
    await sleep(1000);
  };

  // Perform read operation
  const handleRead = async () => {
    if (isAnimating) return;
    setIsAnimating(true);

    const key = sampleKeys[Math.floor(Math.random() * sampleKeys.length)];
    showStatus(`The Hunt begins for "${key}"...`, 1500);

    await sleep(1000);

    let found = false;
    let ioCount = 0;
    const sequence: string[] = [];

    // Check memtable first
    showStatus('Checking Memtable...', 800);
    await sleep(800);
    if (state.memtable.data.some(d => d.key === key)) {
      found = true;
      showStatus('HIT in Memtable! (0 I/Os)', 2000);
    } else {
      showStatus('MISS in Memtable', 800);
      await sleep(800);

      // Hunt through SSTables
      for (const sstable of state.sstables) {
        setTargetSSTableId(sstable.id);
        sequence.push(sstable.id);
        setHuntingSequence([...sequence]);

        showStatus(`Checking SSTable L${sstable.level} (${sstable.minKey} - ${sstable.maxKey})...`, 1000);
        await sleep(1000);

        // Simulate disk I/O
        updateState(prev => ({
          ...prev,
          readIOCount: prev.readIOCount + 1,
        }));
        ioCount++;

        await sleep(600);

        // Check if key is in range
        if (key >= sstable.minKey && key <= sstable.maxKey) {
          // Scan the SSTable
          if (sstable.data.some(d => d.key === key)) {
            found = true;
            showStatus(`HIT in L${sstable.level}! (${ioCount} I/Os)`, 2000);
            break;
          }
        }

        showStatus(`MISS in L${sstable.level}`, 600);
        await sleep(600);
      }

      if (!found) {
        showStatus(`MISS. "${key}" not found (${ioCount} I/Os)`, 2000);
      }
    }

    updateState(prev => ({
      ...prev,
      readHistory: [...prev.readHistory, ioCount],
    }));

    await sleep(2000);
    setTargetSSTableId(null);
    setHuntingSequence([]);
    setIsAnimating(false);
  };

  return (
    <motion.div
      className="frame the-frontier"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <div className="frontier-header">
        <h2>The Frontier</h2>
        <p>Writes are instant. Reads hunt through the chaos. This is the price of freedom.</p>
      </div>

      {/* Controls */}
      <div className="controls">
        <button onClick={handleWrite} disabled={isAnimating}>
          Write Document
        </button>
        <button onClick={handleRead} disabled={isAnimating}>
          Find Document
        </button>
        <button onClick={onShowDashboard} disabled={isAnimating}>
          View Results
        </button>
      </div>

      {/* LSM Visualization */}
      <div className="lsm-container">
        {/* Memtable */}
        <div className="memtable-section">
          <h3>Memtable (RAM)</h3>
          <motion.div
            className={`memtable ${state.memtable.isFull ? 'full' : ''}`}
            animate={{
              scale: state.memtable.isFull ? 1.05 : 1,
            }}
            transition={{ type: 'spring', stiffness: 300 }}
          >
            <div className="memtable-label">
              {state.memtable.data.length} / {state.memtable.capacity}
            </div>
            <div className="memtable-data">
              <AnimatePresence>
                {state.memtable.data.map((chip, idx) => (
                  <motion.div
                    key={chip.id}
                    className="data-chip"
                    initial={{ scale: 0, rotate: -180 }}
                    animate={{ scale: 1, rotate: 0 }}
                    exit={{ scale: 0, y: 100, opacity: 0 }}
                    transition={{
                      type: 'spring',
                      stiffness: 400,
                      damping: 20,
                      delay: idx * 0.05,
                    }}
                  >
                    {chip.key}
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          </motion.div>
        </div>

        {/* SSTables */}
        <div className="sstables-section">
          <h3>SSTables (Disk)</h3>
          <div className="sstables-grid">
            <AnimatePresence>
              {state.sstables.map((sstable, idx) => (
                <motion.div
                  key={sstable.id}
                  className={`sstable ${targetSSTableId === sstable.id ? 'hunting' : ''} ${huntingSequence.includes(sstable.id) ? 'checked' : ''}`}
                  initial={{ x: 0, y: -100, opacity: 0, scale: 0.8 }}
                  animate={{ x: 0, y: 0, opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.5 }}
                  transition={{
                    type: 'spring',
                    stiffness: 300,
                    damping: 25,
                    delay: idx * 0.1,
                  }}
                >
                  <div className="sstable-label">L{sstable.level}</div>
                  <div className="sstable-range">
                    {sstable.minKey} → {sstable.maxKey}
                  </div>
                  <div className="sstable-count">{sstable.data.length} keys</div>
                </motion.div>
              ))}
            </AnimatePresence>

            {state.sstables.length === 0 && (
              <div className="empty-state">No SSTables yet. Write some data!</div>
            )}
          </div>
        </div>
      </div>

      {/* Status Message */}
      <AnimatePresence>
        {statusMessage && (
          <motion.div
            className="status-message"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            {statusMessage}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export default TheFrontier;
