// Core data types for the visual essay

export type WorldType = 'citadel' | 'frontier';

export interface DataChip {
  id: string;
  key: string;
  value: string;
  timestamp: number;
}

// B-Tree Types
export interface BTreeNode {
  id: string;
  level: number; // 0 = leaf, 1+ = internal
  keys: string[];
  children?: string[]; // IDs of child nodes (for internal nodes)
  data?: DataChip[]; // Only for leaf nodes
  isLocked?: boolean;
  isOverflowing?: boolean;
  capacity?: number; // Max keys this node can hold (for fragmentation viz)
  pageSize?: number; // Size of this page in bytes (typically 4096)
  x?: number; // For animation positioning
  y?: number;
}

export interface BTreeState {
  nodes: Map<string, BTreeNode>;
  rootId: string;
  order: number; // Max keys per node
  writeIOCount: number;
  readIOCount: number;
  writeHistory: number[];
  readHistory: number[];
  walWrites: number; // Write-Ahead Log writes
  totalBytesWritten: number; // For write amplification calculation
  actualDataWritten: number; // Actual user data written
  totalDiskSpace: number; // Total disk space used (all pages)
  wastedSpace: number; // Fragmentation waste (empty slots in pages)
}

// LSM-Tree Types
export interface Memtable {
  data: DataChip[];
  capacity: number;
  isFull: boolean;
}

export interface SSTable {
  id: string;
  level: number; // 0 = L0, 1 = L1, etc.
  data: DataChip[];
  minKey: string;
  maxKey: string;
  createdAt: number;
  x?: number;
  y?: number;
  isCompacting?: boolean; // Currently being compacted
  bloomFilterChecks?: number; // Times bloom filter was checked
  sizeBytes: number; // Size in bytes (uncompressed)
  compressedBytes?: number; // Size after compression (L1+ only)
}

export interface LSMState {
  memtable: Memtable;
  sstables: SSTable[];
  writeIOCount: number;
  readIOCount: number;
  writeHistory: number[];
  readHistory: number[];
  compactionCount: number; // Number of compactions performed
  isCompacting: boolean; // Currently running compaction
  totalBytesWritten: number; // For write amplification
  actualDataWritten: number; // Actual user data written
  bloomFilterSaves: number; // I/Os saved by bloom filters
  totalDiskSpace: number; // Total disk space used (sum of all SSTables)
  compressionSavings: number; // Bytes saved through compression
}

// Shared State
export interface AppState {
  currentWorld: WorldType | null;
  currentFrame: number;
  btree: BTreeState;
  lsm: LSMState;
  showDashboard: boolean;
}

// Animation States
export type AnimationPhase =
  | 'idle'
  | 'seeking'
  | 'locking'
  | 'modifying'
  | 'writing'
  | 'wal-writing' // Writing to WAL
  | 'splitting'
  | 'flushing'
  | 'compacting' // Compaction in progress
  | 'hunting'
  | 'bloom-check' // Checking bloom filter
  | 'complete';

export interface AnimationState {
  phase: AnimationPhase;
  targetId?: string;
  data?: any;
}
