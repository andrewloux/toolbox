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
}

export interface LSMState {
  memtable: Memtable;
  sstables: SSTable[];
  writeIOCount: number;
  readIOCount: number;
  writeHistory: number[];
  readHistory: number[];
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
  | 'splitting'
  | 'flushing'
  | 'hunting'
  | 'complete';

export interface AnimationState {
  phase: AnimationPhase;
  targetId?: string;
  data?: any;
}
