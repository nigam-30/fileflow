export type MatchMode = 'all' | 'any';

export type ConditionOperator =
  | 'equals'
  | 'not_equals'
  | 'contains'
  | 'not_contains'
  | 'starts_with'
  | 'ends_with'
  | 'greater_than'
  | 'less_than'
  | 'matches_regex'
  | 'before'
  | 'after'
  | 'in_last_days';

export type ActionType =
  | 'move'
  | 'copy'
  | 'rename'
  | 'delete'
  | 'recycle'
  | 'run_command'
  | 'notify'
  | 'zip';

export type CollisionPolicy = 'overwrite' | 'skip' | 'rename_with_counter';

export interface Condition {
  field: string;
  operator: ConditionOperator;
  value: any;
}

export interface Action {
  type: ActionType;
  destination?: string;
  template?: string;
  collision_policy: CollisionPolicy;
  command?: string;
  notification_title?: string;
  notification_message?: string;
}

export interface Rule {
  id: string;
  name: string;
  description?: string;
  enabled: boolean;
  monitored_folders: string[];
  match_mode: MatchMode;
  conditions: Condition[];
  actions: Action[];
  stop_processing_on_match: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface MonitoredFolder {
  path: string;
  recursive: boolean;
  enabled?: boolean;
}

export interface AuditLogEntry {
  id: number;
  timestamp: string;
  rule_id?: string;
  rule_name?: string;
  source_path: string;
  destination_path?: string;
  action_type?: string;
  status: 'success' | 'skipped' | 'failed' | 'info';
  details?: string;
}
