import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { LSMState, DataChip, SSTable } from '../types';
import './TheCascade.css';

interface TheCascadeProps {
  onComplete: (finalLSMState: LSMState) => void;
}

const sampleKeys = ['apple', 'banana', 'cherry', 'date', 'elderberry', 'fig', 'grape', 'honey', 'iris', 'jackfruit'];

type ScenePhase =
  | 'intro'
  | 'write1'
  | 'write2'
  | 'write3'
  | 'flush1'
  | 'write4'
  | 'write5'
  | 'write6'
  | 'flush2'
  | 'write7'
  | 'write8'
  | 'flush3'
  | 'write9'
  | 'write10'
  | 'flush4'
  | 'compaction-trigger'
  | 'compaction-reading'
  | 'compaction-merging'
  | 'compaction-writing'
  | 'revelation'
  | 'complete';

const TheCascade = ({ onComplete }: TheCascadeProps) => {
  const [phase, setPhase] = useState<ScenePhase>('intro');
  const [narration, setNarration] = useState<string>('');
  const [state, setState] = useState<LSMState>({
    memtable: { data: [], capacity: 3, isFull: false },
    sstables: [],
    writeIOCount: 0,
    readIOCount: 0,
    writeHistory: [],
    readHistory: [],
    compactionCount: 0,
    isCompacting: false,
    totalBytesWritten: 0,
    actualDataWritten: 0,
    bloomFilterSaves: 0,
    totalDiskSpace: 0,
    compressionSavings: 0,
  });
  const [canContinue, setCanContinue] = useState(false);
  const [writeAmp, setWriteAmp] = useState(0);

  const showNarration = (text: string, duration = 2500) => {
    setNarration(text);
    setTimeout(() => setNarration(''), duration);
  };

  const advance = async () => {
    setCanContinue(false);

    switch (phase) {
      case 'intro':
        await runIntro();
        break;
      case 'write1':
        await performWrite();
        setPhase('write2');
        break;
      case 'write2':
        await performWrite();
        setPhase('write3');
        break;
      case 'write3':
        await performWrite();
        setPhase('flush1');
        break;
      case 'flush1':
        await performFlush();
        setPhase('write4');
        break;
      case 'write4':
        await performWrite();
        setPhase('write5');
        break;
      case 'write5':
        await performWrite();
        setPhase('write6');
        break;
      case 'write6':
        await performWrite();
        setPhase('flush2');
        break;
      case 'flush2':
        await performFlush();
        setPhase('write7');
        break;
      case 'write7':
        await performWrite();
        setPhase('write8');
        break;
      case 'write8':
        await performWrite();
        setPhase('flush3');
        break;
      case 'flush3':
        await performFlush();
        setPhase('write9');
        break;
      case 'write9':
        await performWrite();
        setPhase('write10');
        break;
      case 'write10':
        await performWrite();
        setPhase('flush4');
        break;
      case 'flush4':
        await performFlush();
        setPhase('compaction-trigger');
        break;
      case 'compaction-trigger':
        await triggerCompaction();
        setPhase('compaction-reading');
        break;
      case 'compaction-reading':
        await readAllL0();
        setPhase('compaction-merging');
        break;
      case 'compaction-merging':
        await mergeData();
        setPhase('compaction-writing');
        break;
      case 'compaction-writing':
        await writeL1();
        setPhase('revelation');
        break;
      case 'revelation':
        await showRevelation();
        setPhase('complete');
        break;
      case 'complete':
        onComplete(state);
        break;
    }
  };

  const runIntro = async () => {
    showNarration('Write fast. Pay later.', 3000);
    await sleep(3500);
    showNarration('This is The Cascade.', 2500);
    await sleep(3000);
    setPhase('write1');
    setCanContinue(true);
  };

  const performWrite = async () => {
    const key = sampleKeys[Math.floor(Math.random() * sampleKeys.length)];
    const chip: DataChip = {
      id: `chip-${Date.now()}-${Math.random()}`,
      key,
      value: `Value for ${key}`,
      timestamp: Date.now(),
    };

    showNarration(`Writing "${key}"...`, 1000);
    await sleep(800);

    const dataSize = 100;

    setState(prev => {
      const newData = [...prev.memtable.data, chip];
      const isFull = newData.length >= prev.memtable.capacity;

      const newState = {
        ...prev,
        memtable: { ...prev.memtable, data: newData, isFull },
        actualDataWritten: prev.actualDataWritten + dataSize,
      };

      // Update write amp
      if (newState.actualDataWritten > 0) {
        setWriteAmp(newState.totalBytesWritten / newState.actualDataWritten);
      }

      return newState;
    });

    await sleep(500);
    showNarration('Instant. Zero disk I/O.', 1500);
    await sleep(1800);
    setCanContinue(true);
  };

  const performFlush = async () => {
    showNarration('Memtable full! Flushing to disk...', 2000);
    await sleep(2000);

    setState(prev => {
      const flushSize = prev.memtable.data.length * 100;
      const newSSTable: SSTable = {
        id: `sstable-${Date.now()}`,
        level: 0,
        data: [...prev.memtable.data].sort((a, b) => a.key.localeCompare(b.key)),
        minKey: prev.memtable.data.reduce((min, d) => (d.key < min ? d.key : min), prev.memtable.data[0].key),
        maxKey: prev.memtable.data.reduce((max, d) => (d.key > max ? d.key : max), prev.memtable.data[0].key),
        createdAt: Date.now(),
        sizeBytes: flushSize, // L0 = uncompressed
      };

      const newState = {
        ...prev,
        memtable: { data: [], capacity: 3, isFull: false },
        sstables: [newSSTable, ...prev.sstables],
        writeIOCount: prev.writeIOCount + 1,
        totalBytesWritten: prev.totalBytesWritten + flushSize,
        totalDiskSpace: prev.totalDiskSpace + flushSize, // Add SSTable size to disk usage
      };

      // Update write amp
      if (newState.actualDataWritten > 0) {
        setWriteAmp(newState.totalBytesWritten / newState.actualDataWritten);
      }

      return newState;
    });

    await sleep(1500);
    showNarration('SSTable written to L0. 100% uncompressed.', 1500);
    await sleep(1800);
    setCanContinue(true);
  };

  const triggerCompaction = async () => {
    showNarration('⚠️ 4 SSTables at L0...', 2000);
    await sleep(2500);
    showNarration('COMPACTION TRIGGERED', 2500);
    await sleep(2500);

    setState(prev => ({ ...prev, isCompacting: true }));

    showNarration('This is where you pay.', 2500);
    await sleep(3000);
    setCanContinue(true);
  };

  const readAllL0 = async () => {
    showNarration('Reading all L0 SSTables...', 2000);

    const l0Count = state.sstables.filter(t => t.level === 0).length;

    for (let i = 0; i < l0Count; i++) {
      await sleep(600);
      setState(prev => ({
        ...prev,
        readIOCount: prev.readIOCount + 1,
      }));
      showNarration(`Reading SSTable ${i + 1}/${l0Count}...`, 600);
    }

    await sleep(1000);
    showNarration('All data loaded into memory.', 1500);
    await sleep(2000);
    setCanContinue(true);
  };

  const mergeData = async () => {
    showNarration('Merge-sorting all data...', 2000);
    await sleep(2000);

    setState(prev => {
      const l0Tables = prev.sstables.filter(t => t.level === 0);
      const allData: DataChip[] = [];
      l0Tables.forEach(t => allData.push(...t.data));

      return {
        ...prev,
        sstables: prev.sstables.map(t =>
          t.level === 0 ? { ...t, isCompacting: true } : t
        ),
      };
    });

    await sleep(1500);
    showNarration('Merge complete.', 1500);
    await sleep(2000);
    setCanContinue(true);
  };

  const writeL1 = async () => {
    showNarration('Writing merged data to L1...', 2500);
    await sleep(2000);

    setState(prev => {
      const l0Tables = prev.sstables.filter(t => t.level === 0);
      const allData: DataChip[] = [];
      l0Tables.forEach(t => allData.push(...t.data));
      const mergedData = allData.sort((a, b) => a.key.localeCompare(b.key));
      const mergedSize = mergedData.length * 100;

      // COMPRESSION: Simulate 30% compression ratio for L1
      const compressedSize = Math.floor(mergedSize * 0.7);
      const compressionSaved = mergedSize - compressedSize;

      // Calculate L0 disk space to be freed
      const l0DiskSpace = l0Tables.reduce((sum, t) => sum + t.sizeBytes, 0);

      const newL1Table: SSTable = {
        id: `sstable-l1-${Date.now()}`,
        level: 1,
        data: mergedData,
        minKey: mergedData[0].key,
        maxKey: mergedData[mergedData.length - 1].key,
        createdAt: Date.now(),
        sizeBytes: mergedSize, // Uncompressed size
        compressedBytes: compressedSize, // Compressed on-disk size
      };

      const newState = {
        ...prev,
        sstables: [
          ...prev.sstables.filter(t => t.level !== 0),
          newL1Table,
        ],
        writeIOCount: prev.writeIOCount + 1,
        compactionCount: prev.compactionCount + 1,
        isCompacting: false,
        totalBytesWritten: prev.totalBytesWritten + mergedSize,
        // Disk space: Remove L0 tables, add compressed L1
        totalDiskSpace: prev.totalDiskSpace - l0DiskSpace + compressedSize,
        compressionSavings: prev.compressionSavings + compressionSaved,
      };

      // Update write amp
      if (newState.actualDataWritten > 0) {
        setWriteAmp(newState.totalBytesWritten / newState.actualDataWritten);
      }

      return newState;
    });

    await sleep(2500);
    showNarration('You wrote the same data again.', 3000);
    await sleep(3500);
    showNarration('But... L1 is compressed! 30% smaller on disk.', 3000);
    await sleep(3500);
    showNarration(`Write Amplification: ${writeAmp.toFixed(1)}×`, 3000);
    await sleep(3500);
    setCanContinue(true);
  };

  const showRevelation = async () => {
    showNarration('This is the cost of "fast writes."', 3500);
    await sleep(4000);
    showNarration('The disk never forgets.', 3000);
    await sleep(3500);
    showNarration('There must be a better way...', 3500);
    await sleep(4000);
    setCanContinue(true);
  };

  useEffect(() => {
    if (phase === 'intro') {
      advance();
    }
  }, []);

  return (
    <motion.div
      className="frame the-cascade"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      {/* Title */}
      <motion.div
        className="cascade-header"
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.5, duration: 1 }}
      >
        <h2 className="cascade-title">THE CASCADE</h2>
        <p className="cascade-subtitle">Write fast. Pay later.</p>
      </motion.div>

      {/* Write Amplification Counter */}
      {state.totalBytesWritten > 0 && (
        <motion.div
          className="cascade-amp-counter"
          initial={{ scale: 0, rotate: -180 }}
          animate={{ scale: 1, rotate: 0 }}
          transition={{ type: 'spring', stiffness: 200 }}
        >
          <div className="amp-label">Write Amplification</div>
          <motion.div
            className="amp-value"
            animate={{
              scale: writeAmp > 2 ? [1, 1.1, 1] : 1,
              color: writeAmp > 3 ? '#FF4444' : '#00FFC2',
            }}
            transition={{ duration: 0.3 }}
          >
            {writeAmp.toFixed(1)}×
          </motion.div>
          <div className="amp-detail">
            {state.totalBytesWritten} / {state.actualDataWritten} bytes
          </div>
        </motion.div>
      )}

      {/* Storage Efficiency Counter */}
      {state.compressionSavings > 0 && (
        <motion.div
          className="cascade-storage-counter"
          initial={{ scale: 0, x: -50 }}
          animate={{ scale: 1, x: 0 }}
          transition={{ type: 'spring', stiffness: 200 }}
        >
          <div className="storage-label">Compression Savings</div>
          <motion.div className="storage-value">
            {state.compressionSavings} bytes
          </motion.div>
          <div className="storage-detail">
            Disk: {state.totalDiskSpace} bytes (30% smaller)
          </div>
        </motion.div>
      )}

      {/* I/O Counters */}
      <div className="cascade-io-counters">
        <div className="io-counter-box">
          <div className="io-label">Writes</div>
          <motion.div
            className="io-value"
            key={state.writeIOCount}
            initial={{ scale: 1.5, color: '#FF4444' }}
            animate={{ scale: 1, color: '#00FFC2' }}
          >
            {state.writeIOCount}
          </motion.div>
        </div>
        <div className="io-counter-box">
          <div className="io-label">Reads</div>
          <motion.div
            className="io-value"
            key={state.readIOCount}
            initial={{ scale: 1.5, color: '#FF4444' }}
            animate={{ scale: 1, color: '#FF006E' }}
          >
            {state.readIOCount}
          </motion.div>
        </div>
      </div>

      {/* LSM Visualization */}
      <div className="cascade-lsm-container">
        {/* Memtable */}
        <div className="cascade-memtable-section">
          <h3>Memtable (RAM)</h3>
          <motion.div
            className={`cascade-memtable ${state.memtable.isFull ? 'full' : ''}`}
            animate={{ scale: state.memtable.isFull ? 1.05 : 1 }}
          >
            <div className="memtable-count">
              {state.memtable.data.length} / {state.memtable.capacity}
            </div>
            <div className="memtable-chips">
              <AnimatePresence>
                {state.memtable.data.map((chip, idx) => (
                  <motion.div
                    key={chip.id}
                    className="cascade-chip"
                    initial={{ scale: 0, y: -50 }}
                    animate={{ scale: 1, y: 0 }}
                    exit={{ scale: 0, y: 100 }}
                    transition={{ type: 'spring', delay: idx * 0.1 }}
                  >
                    {chip.key}
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          </motion.div>
        </div>

        {/* SSTables */}
        <div className="cascade-sstables-section">
          <h3>SSTables (Disk)</h3>
          <div className="cascade-sstables-grid">
            <AnimatePresence>
              {state.sstables.map((sstable, idx) => (
                <motion.div
                  key={sstable.id}
                  className={`cascade-sstable ${sstable.isCompacting ? 'compacting' : ''} ${sstable.level === 1 ? 'level1' : 'level0'}`}
                  initial={{ scale: 0, y: -100 }}
                  animate={{ scale: 1, y: 0 }}
                  exit={{ scale: 0, opacity: 0 }}
                  transition={{ type: 'spring', delay: idx * 0.15 }}
                >
                  <div className="sstable-level">L{sstable.level}</div>
                  <div className="sstable-keys">{sstable.data.length} keys</div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </div>
      </div>

      {/* Narration */}
      <AnimatePresence>
        {narration && (
          <motion.div
            className="cascade-narration"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            {narration}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Continue Button */}
      <AnimatePresence>
        {canContinue && (
          <motion.button
            className="cascade-continue-btn"
            onClick={advance}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            {phase === 'complete' ? 'Continue to the Answer' : 'Continue'}
          </motion.button>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export default TheCascade;
