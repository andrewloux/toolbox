import { useState } from 'react';
import { AnimatePresence } from 'framer-motion';
import './App.css';
import type { BTreeState, LSMState } from './types';
import TheCascade from './components/TheCascade';
import TheRevelation from './components/TheRevelation';
import TheCitadel from './components/TheCitadel';
import TheDashboard from './components/TheDashboard';
import IOCounter from './components/IOCounter';

// Initialize B-Tree with a simple root
const initBTree = (): BTreeState => ({
  nodes: new Map([
    [
      'root',
      {
        id: 'root',
        level: 0,
        keys: ['grape', 'honey'],
        data: [
          { id: '1', key: 'grape', value: 'A purple fruit', timestamp: Date.now() },
          { id: '2', key: 'honey', value: 'Sweet nectar', timestamp: Date.now() },
        ],
      },
    ],
  ]),
  rootId: 'root',
  order: 4, // Max 4 keys per node
  writeIOCount: 0,
  readIOCount: 0,
  writeHistory: [],
  readHistory: [],
  walWrites: 0,
  totalBytesWritten: 0,
  actualDataWritten: 0,
});

// Initialize LSM-Tree with empty memtable
const initLSM = (): LSMState => ({
  memtable: {
    data: [],
    capacity: 3,
    isFull: false,
  },
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
});

function App() {
  // Frame management: 0=Cascade, 1=Revelation, 2=Citadel, 3=Dashboard
  const [currentFrame, setCurrentFrame] = useState(0);

  // State for both structures
  const [btreeState, setBtreeState] = useState<BTreeState>(initBTree());
  const [lsmState, setLsmState] = useState<LSMState>(initLSM());

  // Handlers for frame transitions
  const handleCascadeComplete = (finalLSMState: LSMState) => {
    setLsmState(finalLSMState); // Capture the LSM state from The Cascade
    setCurrentFrame(1); // Move to Revelation
  };

  const handleRevelationComplete = () => {
    setCurrentFrame(2); // Move to Citadel
  };

  const handleCitadelComplete = () => {
    setCurrentFrame(3); // Move to Dashboard
  };

  const updateBTree = (updater: (prev: BTreeState) => BTreeState) => {
    setBtreeState(updater);
  };

  const resetToBeginning = () => {
    setCurrentFrame(0);
    setBtreeState(initBTree());
    setLsmState(initLSM());
  };

  return (
    <div className="app">
      <AnimatePresence mode="wait">
        {/* Frame 0: The Cascade (Forced LSM Experience) */}
        {currentFrame === 0 && (
          <TheCascade
            key="cascade"
            onComplete={handleCascadeComplete}
          />
        )}

        {/* Frame 1: The Revelation (Title Card) */}
        {currentFrame === 1 && (
          <TheRevelation
            key="revelation"
            onComplete={handleRevelationComplete}
          />
        )}

        {/* Frame 2: The Citadel (B-Tree Deep Dive) */}
        {currentFrame === 2 && (
          <>
            <IOCounter
              writeCount={btreeState.writeIOCount}
              readCount={btreeState.readIOCount}
            />
            <TheCitadel
              key="citadel"
              state={btreeState}
              updateState={updateBTree}
              onShowDashboard={handleCitadelComplete}
            />
          </>
        )}

        {/* Frame 3: The Synthesis (Dashboard) */}
        {currentFrame === 3 && (
          <TheDashboard
            key="dashboard"
            btreeState={btreeState}
            lsmState={lsmState}
            onReset={resetToBeginning}
          />
        )}
      </AnimatePresence>
    </div>
  );
}

export default App;
