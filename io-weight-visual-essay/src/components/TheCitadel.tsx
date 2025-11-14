import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { BTreeState, BTreeNode, DataChip, AnimationPhase } from '../types';
import AmplificationCounter from './AmplificationCounter';
import './TheCitadel.css';

interface TheCitadelProps {
  state: BTreeState;
  updateState: (updater: (prev: BTreeState) => BTreeState) => void;
  onShowDashboard: () => void;
}

const sampleKeys = ['apple', 'banana', 'cherry', 'date', 'elderberry', 'fig', 'grape', 'honey', 'iris', 'jackfruit'];

const TheCitadel = ({ state, updateState, onShowDashboard }: TheCitadelProps) => {
  const [animationPhase, setAnimationPhase] = useState<AnimationPhase>('idle');
  const [targetNodeId, setTargetNodeId] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string>('');
  const [isAnimating, setIsAnimating] = useState(false);
  const [showIntro, setShowIntro] = useState(true);

  const showStatus = (message: string, duration = 2000) => {
    setStatusMessage(message);
    setTimeout(() => setStatusMessage(''), duration);
  };

  // Find leaf node for a key
  const findLeafNode = (key: string): string => {
    let currentId = state.rootId;
    let currentNode = state.nodes.get(currentId);

    while (currentNode && currentNode.level > 0) {
      // Internal node - find the right child
      const childIndex = currentNode.keys.findIndex(k => key < k);
      const index = childIndex === -1 ? currentNode.keys.length : childIndex;
      currentId = currentNode.children![index];
      currentNode = state.nodes.get(currentId);
    }

    return currentId;
  };

  // Perform write operation
  const handleWrite = async () => {
    if (isAnimating) return;
    setIsAnimating(true);

    // Generate random key
    const key = sampleKeys[Math.floor(Math.random() * sampleKeys.length)];
    const chip: DataChip = {
      id: `chip-${Date.now()}`,
      key,
      value: `Value for ${key}`,
      timestamp: Date.now(),
    };

    const dataSize = 100; // Simulated size in bytes

    // PHASE 0: WAL WRITE (NEW!)
    setAnimationPhase('wal-writing');
    showStatus('Writing to Write-Ahead Log...', 1000);

    await sleep(800);
    updateState(prev => ({
      ...prev,
      walWrites: prev.walWrites + 1,
      writeIOCount: prev.writeIOCount + 1,
      totalBytesWritten: prev.totalBytesWritten + dataSize,
      actualDataWritten: prev.actualDataWritten + dataSize,
    }));

    await sleep(500);
    showStatus('WAL write complete. Now modifying tree...', 800);
    await sleep(800);

    // PHASE 1: SEEK
    setAnimationPhase('seeking');
    showStatus('Seeking target page...', 1000);

    await sleep(500);
    const targetId = findLeafNode(key);
    setTargetNodeId(targetId);

    // Count I/O for seeking through levels
    const root = state.nodes.get(state.rootId)!;
    const seekIOCount = root.level + 1;

    for (let i = 0; i < seekIOCount; i++) {
      await sleep(400);
      updateState(prev => ({
        ...prev,
        writeIOCount: prev.writeIOCount + 1,
      }));
    }

    // PHASE 2: LOCK
    await sleep(500);
    setAnimationPhase('locking');
    showStatus('Page Locked. Modifying In-Place...', 1500);

    updateState(prev => {
      const newNodes = new Map(prev.nodes);
      const node = { ...newNodes.get(targetId)! };
      node.isLocked = true;
      newNodes.set(targetId, node);
      return { ...prev, nodes: newNodes };
    });

    await sleep(1500);

    // PHASE 3: MODIFY
    setAnimationPhase('modifying');
    showStatus('Inserting and reordering keys...', 1500);

    await sleep(1500);

    // Insert the key
    const targetNode = state.nodes.get(targetId)!;
    const newKeys = [...targetNode.keys, key].sort();
    const newData = [...(targetNode.data || []), chip].sort((a, b) => a.key.localeCompare(b.key));

    // Check if overflow
    const isOverflow = newKeys.length > state.order;

    updateState(prev => {
      const newNodes = new Map(prev.nodes);
      const node = { ...newNodes.get(targetId)! };
      node.keys = newKeys;
      node.data = newData;
      node.isOverflowing = isOverflow;
      newNodes.set(targetId, node);
      return { ...prev, nodes: newNodes };
    });

    await sleep(1000);

    // PHASE 4: WRITE BACK (or SPLIT)
    if (isOverflow) {
      // Trigger split animation
      await handleSplit(targetId);
    } else {
      // Normal write-back
      setAnimationPhase('writing');
      showStatus('Writing page back to disk...', 1000);

      await sleep(800);

      const pageSize = 4096; // 4KB page
      updateState(prev => ({
        ...prev,
        writeIOCount: prev.writeIOCount + 1,
        totalBytesWritten: prev.totalBytesWritten + pageSize, // Write entire page!
      }));

      await sleep(500);

      // Unlock
      updateState(prev => {
        const newNodes = new Map(prev.nodes);
        const node = { ...newNodes.get(targetId)! };
        node.isLocked = false;
        newNodes.set(targetId, node);
        return {
          ...prev,
          nodes: newNodes,
          writeHistory: [...prev.writeHistory, prev.writeIOCount],
        };
      });
    }

    // Reset
    setAnimationPhase('complete');
    showStatus('Write complete!', 1500);
    await sleep(1500);
    setAnimationPhase('idle');
    setTargetNodeId(null);
    setIsAnimating(false);
  };

  // Handle B-Tree split
  const handleSplit = async (nodeId: string) => {
    setAnimationPhase('splitting');
    showStatus('OVERFLOW! Splitting page...', 2000);

    await sleep(1500);

    updateState(prev => {
      const newNodes = new Map(prev.nodes);
      const node = { ...newNodes.get(nodeId)! };

      // Split the node
      const mid = Math.floor(node.keys.length / 2);
      const leftKeys = node.keys.slice(0, mid);
      const rightKeys = node.keys.slice(mid + 1);
      const medianKey = node.keys[mid];

      const leftData = node.data!.slice(0, mid);
      const rightData = node.data!.slice(mid + 1);

      // Create new nodes
      const leftNode: BTreeNode = {
        id: `${nodeId}-left`,
        level: 0,
        keys: leftKeys,
        data: leftData,
      };

      const rightNode: BTreeNode = {
        id: `${nodeId}-right`,
        level: 0,
        keys: rightKeys,
        data: rightData,
      };

      newNodes.set(leftNode.id, leftNode);
      newNodes.set(rightNode.id, rightNode);

      // If this is root, create new root
      if (nodeId === prev.rootId) {
        const newRoot: BTreeNode = {
          id: `root-${Date.now()}`,
          level: 1,
          keys: [medianKey],
          children: [leftNode.id, rightNode.id],
        };
        newNodes.set(newRoot.id, newRoot);
        newNodes.delete(nodeId);

        const pageSize = 4096;
        return {
          ...prev,
          nodes: newNodes,
          rootId: newRoot.id,
          writeIOCount: prev.writeIOCount + 3, // Writing 3 pages
          totalBytesWritten: prev.totalBytesWritten + (pageSize * 3), // 3 pages!
          writeHistory: [...prev.writeHistory, prev.writeIOCount + 3],
        };
      }

      // Remove old node
      newNodes.delete(nodeId);

      const pageSize = 4096;
      return {
        ...prev,
        nodes: newNodes,
        writeIOCount: prev.writeIOCount + 2, // Writing 2 pages
        totalBytesWritten: prev.totalBytesWritten + (pageSize * 2), // 2 pages!
        writeHistory: [...prev.writeHistory, prev.writeIOCount + 2],
      };
    });

    await sleep(2000);
    showStatus('Split complete! The tree grows deeper...', 2000);
  };

  // Perform read operation
  const handleRead = async () => {
    if (isAnimating) return;
    setIsAnimating(true);

    const key = sampleKeys[Math.floor(Math.random() * sampleKeys.length)];

    setAnimationPhase('seeking');
    showStatus(`Searching for "${key}"...`, 1000);

    // Traverse tree
    let currentId = state.rootId;
    let found = false;
    let ioCount = 0;

    while (currentId) {
      await sleep(600);
      setTargetNodeId(currentId);

      updateState(prev => ({
        ...prev,
        readIOCount: prev.readIOCount + 1,
      }));
      ioCount++;

      const node = state.nodes.get(currentId);
      if (!node) break;

      // Check if key is in this node
      if (node.level === 0) {
        // Leaf node
        if (node.keys.includes(key)) {
          found = true;
          break;
        } else {
          break;
        }
      } else {
        // Internal node - navigate to child
        const childIndex = node.keys.findIndex(k => key < k);
        const index = childIndex === -1 ? node.keys.length : childIndex;
        currentId = node.children![index];
      }
    }

    await sleep(800);

    if (found) {
      showStatus(`HIT! Found "${key}" in ${ioCount} I/Os`, 2000);
    } else {
      showStatus(`MISS. "${key}" not found (${ioCount} I/Os)`, 2000);
    }

    updateState(prev => ({
      ...prev,
      readHistory: [...prev.readHistory, ioCount],
    }));

    await sleep(2000);
    setAnimationPhase('idle');
    setTargetNodeId(null);
    setIsAnimating(false);
  };

  return (
    <motion.div
      className="frame the-citadel"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      {/* Intro Overlay */}
      <AnimatePresence>
        {showIntro && (
          <motion.div
            className="citadel-intro-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowIntro(false)}
          >
            <motion.div
              className="intro-content"
              initial={{ y: 50, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.3 }}
            >
              <h3>HONEST GEOMETRY</h3>
              <p className="intro-principle">
                The B-Tree makes no promises it can't keep.
              </p>
              <div className="intro-guarantees">
                <div className="guarantee-item">
                  <span className="guarantee-icon">✓</span>
                  <span>Every write knows its exact cost</span>
                </div>
                <div className="guarantee-item">
                  <span className="guarantee-icon">✓</span>
                  <span>Every read takes O(log n) steps. Always.</span>
                </div>
                <div className="guarantee-item">
                  <span className="guarantee-icon">✓</span>
                  <span>Durability is explicit (WAL)</span>
                </div>
                <div className="guarantee-item">
                  <span className="guarantee-icon">✓</span>
                  <span>Perfect order, maintained in-place</span>
                </div>
              </div>
              <div className="intro-cta">Click anywhere to explore</div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="citadel-header">
        <h2>Honest Geometry</h2>
        <p>No deferred costs. No hidden amplification. Every operation's price is known upfront.</p>
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

      {/* Amplification Counter */}
      {state.totalBytesWritten > 0 && (
        <AmplificationCounter
          totalBytesWritten={state.totalBytesWritten}
          actualDataWritten={state.actualDataWritten}
          type="write"
        />
      )}

      {/* WAL Stats */}
      {state.walWrites > 0 && (
        <div className="wal-stats">
          <div className="wal-label">WAL Writes</div>
          <div className="wal-value">{state.walWrites}</div>
          <div className="wal-detail">Durability requires writing twice</div>
        </div>
      )}

      {/* B-Tree Visualization */}
      <div className="btree-container">
        <BTreeVisualization
          nodes={state.nodes}
          rootId={state.rootId}
          targetNodeId={targetNodeId}
          animationPhase={animationPhase}
        />
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

// Helper component for B-Tree visualization
interface BTreeVisualizationProps {
  nodes: Map<string, BTreeNode>;
  rootId: string;
  targetNodeId: string | null;
  animationPhase: AnimationPhase;
}

const BTreeVisualization = ({ nodes, rootId, targetNodeId }: BTreeVisualizationProps) => {
  const renderNode = (nodeId: string, depth: number = 0) => {
    const node = nodes.get(nodeId);
    if (!node) return <></>;

    const isTarget = nodeId === targetNodeId;
    const className = `btree-node ${isTarget ? 'target' : ''} ${node.isLocked ? 'locked' : ''} ${node.isOverflowing ? 'overflowing' : ''}`;

    return (
      <div key={nodeId} className="btree-level">
        <motion.div
          className={className}
          layout
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{
            scale: isTarget ? 1.1 : 1,
            opacity: 1,
          }}
          transition={{ type: 'spring', stiffness: 300, damping: 25 }}
        >
          <div className="node-label">
            {node.level === 0 ? 'Leaf' : `Level ${node.level}`}
          </div>
          <div className="node-keys">
            {node.keys.map((key, idx) => (
              <motion.div
                key={`${nodeId}-${key}-${idx}`}
                className="key-chip"
                layout
                initial={{ x: -10, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: idx * 0.05 }}
              >
                {key}
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Render children */}
        {node.children && node.children.length > 0 && (
          <div className="btree-children">
            {node.children.map(childId => renderNode(childId, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  return <div className="btree-visualization">{renderNode(rootId)}</div>;
};

// Utility
const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export default TheCitadel;
