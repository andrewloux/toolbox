import { useState } from 'react';
import { AnimatePresence } from 'framer-motion';
import './App.css';
import type { AppState, WorldType, BTreeState, LSMState } from './types';
import TheChoice from './components/TheChoice';
import TheCitadel from './components/TheCitadel';
import TheFrontier from './components/TheFrontier';
import TheDashboard from './components/TheDashboard';
import WorldToggle from './components/WorldToggle';
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
});

function App() {
  const [state, setState] = useState<AppState>({
    currentWorld: null,
    currentFrame: 1,
    btree: initBTree(),
    lsm: initLSM(),
    showDashboard: false,
  });

  const handleWorldChoice = (world: WorldType) => {
    setState((prev) => ({
      ...prev,
      currentWorld: world,
      currentFrame: 2,
    }));
  };

  const toggleWorld = (world: WorldType) => {
    setState((prev) => ({
      ...prev,
      currentWorld: world,
    }));
  };

  const updateBTree = (updater: (prev: BTreeState) => BTreeState) => {
    setState((prev) => ({
      ...prev,
      btree: updater(prev.btree),
    }));
  };

  const updateLSM = (updater: (prev: LSMState) => LSMState) => {
    setState((prev) => ({
      ...prev,
      lsm: updater(prev.lsm),
    }));
  };

  const showDashboard = () => {
    setState((prev) => ({
      ...prev,
      showDashboard: true,
      currentFrame: 6,
    }));
  };

  const resetToChoice = () => {
    setState({
      currentWorld: null,
      currentFrame: 1,
      btree: initBTree(),
      lsm: initLSM(),
      showDashboard: false,
    });
  };

  return (
    <div className="app">
      <AnimatePresence mode="wait">
        {/* Frame 1: The Choice */}
        {state.currentFrame === 1 && (
          <TheChoice key="choice" onChoice={handleWorldChoice} />
        )}

        {/* Frame 2-5: The Worlds */}
        {state.currentWorld && !state.showDashboard && (
          <>
            <WorldToggle
              currentWorld={state.currentWorld}
              onToggle={toggleWorld}
            />
            <IOCounter
              writeCount={
                state.currentWorld === 'citadel'
                  ? state.btree.writeIOCount
                  : state.lsm.writeIOCount
              }
              readCount={
                state.currentWorld === 'citadel'
                  ? state.btree.readIOCount
                  : state.lsm.readIOCount
              }
            />
            {state.currentWorld === 'citadel' ? (
              <TheCitadel
                key="citadel"
                state={state.btree}
                updateState={updateBTree}
                onShowDashboard={showDashboard}
              />
            ) : (
              <TheFrontier
                key="frontier"
                state={state.lsm}
                updateState={updateLSM}
                onShowDashboard={showDashboard}
              />
            )}
          </>
        )}

        {/* Frame 6: The Dashboard */}
        {state.showDashboard && (
          <TheDashboard
            key="dashboard"
            btreeState={state.btree}
            lsmState={state.lsm}
            onReset={resetToChoice}
          />
        )}
      </AnimatePresence>
    </div>
  );
}

export default App;
