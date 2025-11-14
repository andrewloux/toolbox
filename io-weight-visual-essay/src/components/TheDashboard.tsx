import { motion } from 'framer-motion';
import type { BTreeState, LSMState } from '../types';
import './TheDashboard.css';

interface TheDashboardProps {
  btreeState: BTreeState;
  lsmState: LSMState;
  onReset: () => void;
}

const TheDashboard = ({ btreeState, lsmState, onReset }: TheDashboardProps) => {
  // Calculate averages
  const avgBTreeWrite =
    btreeState.writeHistory.length > 0
      ? (btreeState.writeHistory.reduce((a, b) => a + b, 0) / btreeState.writeHistory.length).toFixed(1)
      : '0';

  const avgLSMWrite =
    lsmState.writeHistory.length > 0
      ? (lsmState.writeHistory.reduce((a, b) => a + b, 0) / lsmState.writeHistory.length).toFixed(1)
      : '0';

  const avgBTreeRead =
    btreeState.readHistory.length > 0
      ? (btreeState.readHistory.reduce((a, b) => a + b, 0) / btreeState.readHistory.length).toFixed(1)
      : 'N/A';

  const avgLSMRead =
    lsmState.readHistory.length > 0
      ? (lsmState.readHistory.reduce((a, b) => a + b, 0) / lsmState.readHistory.length).toFixed(1)
      : 'N/A';

  // Calculate write amplification
  const btreeWriteAmp =
    btreeState.actualDataWritten > 0
      ? (btreeState.totalBytesWritten / btreeState.actualDataWritten).toFixed(1)
      : 'N/A';

  const lsmWriteAmp =
    lsmState.actualDataWritten > 0
      ? (lsmState.totalBytesWritten / lsmState.actualDataWritten).toFixed(1)
      : 'N/A';

  // Calculate storage efficiency
  const btreeFragmentation =
    btreeState.totalDiskSpace > 0
      ? ((btreeState.wastedSpace / btreeState.totalDiskSpace) * 100).toFixed(0)
      : '0';

  const lsmCompressionRatio =
    lsmState.totalDiskSpace > 0 && lsmState.compressionSavings > 0
      ? (((lsmState.compressionSavings / (lsmState.totalDiskSpace + lsmState.compressionSavings)) * 100).toFixed(0))
      : '0';

  return (
    <motion.div
      className="frame the-dashboard"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <motion.div
        className="dashboard-content"
        initial={{ y: 50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.3, duration: 0.8 }}
      >
        <h1 className="dashboard-title">
          The Synthesis
        </h1>

        <blockquote className="dashboard-quote">
          There is no best. There is only the weight of I/O.
          <br />
          Choose your trade-off.
        </blockquote>

        {/* Results Table */}
        <div className="results-table">
          <div className="table-header">
            <div className="table-cell header-cell">Your Workload Results</div>
            <div className="table-cell header-cell citadel-header">
              The Citadel
              <span className="tech-label">RDBMS • B-Tree</span>
            </div>
            <div className="table-cell header-cell frontier-header">
              The Frontier
              <span className="tech-label">NoSQL • LSM-Tree</span>
            </div>
          </div>

          <div className="table-row">
            <div className="table-cell metric-label">Avg. Write I/Os</div>
            <div className="table-cell citadel-cell">
              <motion.div
                className="metric-value"
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.6, type: 'spring', stiffness: 300 }}
              >
                {btreeState.writeIOCount > 0 ? avgBTreeWrite : 'N/A'}
              </motion.div>
              <div className="metric-description">
                {parseFloat(avgBTreeWrite) > 3 ? 'Expensive but maintains order' : 'Precise writes'}
              </div>
            </div>
            <div className="table-cell frontier-cell">
              <motion.div
                className="metric-value"
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.7, type: 'spring', stiffness: 300 }}
              >
                {lsmState.writeIOCount > 0 ? avgLSMWrite : 'N/A'}
              </motion.div>
              <div className="metric-description">
                {parseFloat(avgLSMWrite) < 2 ? 'Lightning fast appends' : 'Batched writes'}
              </div>
            </div>
          </div>

          <div className="table-row">
            <div className="table-cell metric-label">Avg. Read I/Os</div>
            <div className="table-cell citadel-cell">
              <motion.div
                className="metric-value"
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.8, type: 'spring', stiffness: 300 }}
              >
                {avgBTreeRead}
              </motion.div>
              <div className="metric-description">Predictable • Logarithmic</div>
            </div>
            <div className="table-cell frontier-cell">
              <motion.div
                className="metric-value"
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.9, type: 'spring', stiffness: 300 }}
              >
                {avgLSMRead}
              </motion.div>
              <div className="metric-description">
                {parseFloat(avgLSMRead) > 5 ? 'The chaos of the hunt' : 'Variable performance'}
              </div>
            </div>
          </div>

          {/* Write Amplification Row */}
          <div className="table-row highlight-row">
            <div className="table-cell metric-label">
              Write Amplification
              <span className="metric-hint">Bytes written / User data</span>
            </div>
            <div className="table-cell citadel-cell">
              <motion.div
                className={`metric-value ${parseFloat(btreeWriteAmp) > 10 ? 'critical' : ''}`}
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 1.0, type: 'spring', stiffness: 300 }}
              >
                {btreeWriteAmp}×
              </motion.div>
              <div className="metric-description">
                {parseFloat(btreeWriteAmp) > 20 ? 'WAL + Full Page Writes' : 'The cost of order'}
              </div>
            </div>
            <div className="table-cell frontier-cell">
              <motion.div
                className={`metric-value ${parseFloat(lsmWriteAmp) > 10 ? 'critical' : ''}`}
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 1.1, type: 'spring', stiffness: 300 }}
              >
                {lsmWriteAmp}×
              </motion.div>
              <div className="metric-description">
                {parseFloat(lsmWriteAmp) > 5 ? 'Compaction penalty' : 'Deferred cost'}
              </div>
            </div>
          </div>

          {/* Storage Efficiency Row */}
          <div className="table-row highlight-row">
            <div className="table-cell metric-label">
              Storage Efficiency
              <span className="metric-hint">Fragmentation vs Compression</span>
            </div>
            <div className="table-cell citadel-cell">
              <motion.div
                className={`metric-value ${parseFloat(btreeFragmentation) > 40 ? 'critical' : ''}`}
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 1.2, type: 'spring', stiffness: 300 }}
              >
                {btreeFragmentation}% wasted
              </motion.div>
              <div className="metric-description">
                {parseFloat(btreeFragmentation) > 40 ? 'Half-empty pages' : 'Fragmentation penalty'}
              </div>
            </div>
            <div className="table-cell frontier-cell">
              <motion.div
                className="metric-value positive"
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 1.3, type: 'spring', stiffness: 300 }}
              >
                {lsmCompressionRatio}% saved
              </motion.div>
              <div className="metric-description">
                {parseFloat(lsmCompressionRatio) > 20 ? 'Aggressive compression' : 'Compact storage'}
              </div>
            </div>
          </div>

          {/* Special Stats Row */}
          <div className="table-row">
            <div className="table-cell metric-label">Special Stats</div>
            <div className="table-cell citadel-cell">
              <div className="metric-value small">{btreeState.walWrites}</div>
              <div className="metric-description">WAL Writes (durability)</div>
            </div>
            <div className="table-cell frontier-cell">
              <div className="stat-split">
                <div>
                  <div className="metric-value small">{lsmState.compactionCount}</div>
                  <div className="metric-description">Compactions</div>
                </div>
                <div>
                  <div className="metric-value small">{lsmState.bloomFilterSaves}</div>
                  <div className="metric-description">Bloom Saves</div>
                </div>
              </div>
            </div>
          </div>

          <div className="table-row">
            <div className="table-cell metric-label">Total Writes</div>
            <div className="table-cell citadel-cell">
              <div className="metric-value small">{btreeState.writeHistory.length}</div>
            </div>
            <div className="table-cell frontier-cell">
              <div className="metric-value small">{lsmState.writeHistory.length}</div>
            </div>
          </div>

          <div className="table-row">
            <div className="table-cell metric-label">Total Reads</div>
            <div className="table-cell citadel-cell">
              <div className="metric-value small">{btreeState.readHistory.length}</div>
            </div>
            <div className="table-cell frontier-cell">
              <div className="metric-value small">{lsmState.readHistory.length}</div>
            </div>
          </div>
        </div>

        {/* Key Insights */}
        <motion.div
          className="insights"
          initial={{ y: 30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 1.2, duration: 0.8 }}
        >
          <h3>Key Insights</h3>
          <div className="insights-grid">
            <div className="insight-card citadel">
              <h4>The Citadel (B-Tree)</h4>
              <ul>
                <li>Writes are <strong>expensive</strong> but maintain perfect order</li>
                <li>Reads are <strong>fast</strong> and <strong>predictable</strong> (O(log n))</li>
                <li><strong>Fragmentation</strong>: 30-50% wasted space after splits</li>
                <li>Ideal for: Read-heavy workloads, transactional systems</li>
                <li>Trade-off: Write amplification & fragmentation for read speed</li>
              </ul>
            </div>
            <div className="insight-card frontier">
              <h4>The Frontier (LSM-Tree)</h4>
              <ul>
                <li>Writes are <strong>instant</strong> (append-only to memtable)</li>
                <li>Reads are <strong>slow</strong> and <strong>unpredictable</strong></li>
                <li><strong>Compression</strong>: 30%+ space savings on disk</li>
                <li>Ideal for: Write-heavy workloads, time-series data, logs</li>
                <li>Trade-off: Read amplification for write speed & storage</li>
              </ul>
            </div>
          </div>
        </motion.div>

        {/* Actions */}
        <motion.div
          className="dashboard-actions"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 1.5, duration: 0.8 }}
        >
          <button onClick={onReset} className="reset-btn">
            Start Over
          </button>
        </motion.div>

        {/* Final Thought */}
        <motion.div
          className="final-thought"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 2, duration: 1 }}
        >
          <p>
            Every database is a bet on the future shape of your queries.
            <br />
            <strong>Choose wisely.</strong>
          </p>
        </motion.div>
      </motion.div>
    </motion.div>
  );
};

export default TheDashboard;
