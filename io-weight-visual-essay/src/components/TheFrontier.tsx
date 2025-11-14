import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { LSMState, DataChip, SSTable } from '../types';
import AmplificationCounter from './AmplificationCounter';
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

    const dataSize = 100; // Simulated size in bytes

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
        actualDataWritten: prev.actualDataWritten + dataSize,
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
      const flushSize = prev.memtable.data.length * 100;
      const newSSTable: SSTable = {
        id: `sstable-${Date.now()}`,
        level: 0,
        data: [...prev.memtable.data].sort((a, b) => a.key.localeCompare(b.key)),
        minKey: prev.memtable.data.reduce((min, d) => (d.key < min ? d.key : min), prev.memtable.data[0].key),
        maxKey: prev.memtable.data.reduce((max, d) => (d.key > max ? d.key : max), prev.memtable.data[0].key),
        createdAt: Date.now(),
        sizeBytes: flushSize,
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
        totalBytesWritten: prev.totalBytesWritten + flushSize,
      };
    });

    await sleep(1500);
    showStatus('Flush complete! SSTable written to L0.', 1500);
    await sleep(1000);

    // Check if compaction is needed (>= 4 L0 SSTables)
    const l0Count = state.sstables.filter(t => t.level === 0).length + 1; // +1 for the one we just added
    if (l0Count >= 4) {
      await sleep(500);
      await handleCompaction();
    }
  };

  // THE COMPACTION SCENE - The brutal reality
  const handleCompaction = async () => {
    showStatus('⚠️ COMPACTION TRIGGERED!', 2000);
    await sleep(1500);

    updateState(prev => ({ ...prev, isCompacting: true }));

    showStatus('Merging L0 SSTables...', 2000);
    await sleep(1000);

    // Get all L0 tables
    const l0Tables = state.sstables.filter(t => t.level === 0);
    if (l0Tables.length < 2) {
      updateState(prev => ({ ...prev, isCompacting: false }));
      return;
    }

    // Mark them as compacting
    updateState(prev => ({
      ...prev,
      sstables: prev.sstables.map(t =>
        t.level === 0 ? { ...t, isCompacting: true } : t
      ),
    }));

    await sleep(1500);

    // Merge sort animation (simulate reading all L0 tables)
    showStatus('Reading and merging SSTables...', 2000);
    for (let i = 0; i < l0Tables.length; i++) {
      await sleep(600);
      updateState(prev => ({
        ...prev,
        readIOCount: prev.readIOCount + 1,
      }));
    }

    await sleep(1000);

    // Merge all L0 data
    const allData: DataChip[] = [];
    l0Tables.forEach(t => allData.push(...t.data));
    const mergedData = allData.sort((a, b) => a.key.localeCompare(b.key));

    // Write to L1 (this is write amplification!)
    showStatus('Writing merged SSTable to L1...', 2000);
    await sleep(1500);

    const mergedSize = mergedData.length * 100;
    const compressedSize = Math.floor(mergedSize * 0.7); // 30% compression

    const newL1Table: SSTable = {
      id: `sstable-l1-${Date.now()}`,
      level: 1,
      data: mergedData,
      minKey: mergedData[0].key,
      maxKey: mergedData[mergedData.length - 1].key,
      createdAt: Date.now(),
      sizeBytes: mergedSize,
      compressedBytes: compressedSize,
    };

    updateState(prev => ({
      ...prev,
      sstables: [
        ...prev.sstables.filter(t => t.level !== 0), // Remove all L0
        newL1Table,
      ],
      writeIOCount: prev.writeIOCount + 1,
      compactionCount: prev.compactionCount + 1,
      isCompacting: false,
      // WRITE AMPLIFICATION: We wrote the same data again!
      totalBytesWritten: prev.totalBytesWritten + mergedSize,
    }));

    await sleep(1000);
    showStatus('Compaction complete. Data rewritten to L1.', 2500);
    await sleep(1500);
    showStatus('This is where you paid for those cheap writes.', 2500);
    await sleep(2000);
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

        // BLOOM FILTER CHECK (NEW!)
        showStatus(`Bloom filter check: ${sstable.id}...`, 500);
        await sleep(500);

        const keyExists = sstable.data.some(d => d.key === key);
        const bloomResult = !keyExists && Math.random() < 0.8 ? 'NOT_PRESENT' : 'MAYBE';

        if (bloomResult === 'NOT_PRESENT') {
          showStatus(`✓ Bloom: NOT in ${sstable.id}. Skipping I/O!`, 800);
          updateState(prev => ({
            ...prev,
            bloomFilterSaves: prev.bloomFilterSaves + 1,
          }));
          await sleep(800);
          continue; // SKIP the disk I/O!
        }

        showStatus(`Bloom: MAYBE in L${sstable.level}. Reading disk...`, 1000);
        await sleep(1000);

        // Simulate disk I/O
        updateState(prev => ({
          ...prev,
          readIOCount: prev.readIOCount + 1,
        }));
        ioCount++;

        await sleep(600);

        // Check if key is in range and scan
        if (key >= sstable.minKey && key <= sstable.maxKey) {
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
        <button onClick={handleWrite} disabled={isAnimating || state.isCompacting}>
          Write Document
        </button>
        <button onClick={handleRead} disabled={isAnimating || state.isCompacting}>
          Find Document
        </button>
        <button
          onClick={handleCompaction}
          disabled={isAnimating || state.isCompacting || state.sstables.filter(t => t.level === 0).length < 2}
          className="compaction-btn"
        >
          Trigger Compaction
        </button>
        <button onClick={onShowDashboard} disabled={isAnimating}>
          View Results
        </button>
      </div>

      {/* Amplification Counter */}
      {state.totalBytesWritten > 0 && (
        <AmplificationCounter
          totalBytesWritten={state.totalBytesWritten}
          actualDataWritten={state.actualDataWritten}
          type="write"
        />
      )}

      {/* Bloom Filter Stats */}
      {state.bloomFilterSaves > 0 && (
        <div className="bloom-stats">
          <div className="bloom-label">Bloom Filter Saves</div>
          <div className="bloom-value">{state.bloomFilterSaves} I/Os</div>
        </div>
      )}

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
                  className={`sstable ${targetSSTableId === sstable.id ? 'hunting' : ''} ${huntingSequence.includes(sstable.id) ? 'checked' : ''} ${sstable.isCompacting ? 'compacting' : ''}`}
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
