export interface Plot {
  id: number;
  farmer_id: number;
  farmer_name: string;
  area_acre: number;
  baseline_crop: string;
  planned_crop: string;
  week: number;
  expected_yield: number;
  health: number;
  polygon: [number, number][];
  profit?: number;
  baseline_profit?: number;
  profit_gain?: number;
  kyun_hi?: string;
  kyun_en?: string;
  changed?: boolean;
}

export interface PlanResult {
  assignment: Record<number, {
    crop: string;
    week: number;
    price: number;
    profit: number;
    baseline_profit: number;
    profit_gain: number;
    kyun_hi: string;
    kyun_en: string;
    changed: boolean;
  }>;
  farmers_worse_off: number;
  village_profit_before: number;
  village_profit_after: number;
  profit_diff: number;
  max_crop_share_before: number;
  max_crop_share_after: number;
  crop_distribution_before: Record<string, number>;
  crop_distribution_after: Record<string, number>;
  plots: Plot[];
  iterations: number;
}

export interface LogbookEntry {
  id: number;
  type: string;
  farmer_id: number;
  farmer_name: string;
  crop: string;
  crop_hi: string;
  qty_kg: number;
  rate: number;
  total: number;
  buyer: string;
  timestamp: string;
  raw_text: string;
}

export interface TractorSlot {
  request_id: number;
  farmer_id: number;
  farmer_name: string;
  original_date: string;
  scheduled_date: string;
  delayed_days: number;
  tractor_id: string;
  hours: number;
  status: string;
}

export interface TractorScheduleResult {
  schedule: Record<string, TractorSlot[]>;
  daily_hours: Record<string, number>;
  daily_capacity_hours: number;
  tractors_count: number;
  total_requests: number;
  peak_demand_unplanned: number;
  peak_demand_planned: number;
  demand_flattening_pct: number;
  assigned_requests: TractorSlot[];
}

export interface BijliWindowResult {
  best_window: string;
  start_hour: number;
  end_hour: number;
  average_prob: number;
  average_prob_pct: number;
  hourly_probabilities: { hour: number; time_label: string; prob: number; pct: number }[];
  recommendation_hi: string;
  recommendation_en: string;
  confidence: string;
}

export interface IrrigationSlot {
  plot_id: number;
  farmer_name: string;
  crop: string;
  crop_hi: string;
  area_acre: number;
  days_since: number;
  crop_interval: number;
  urgency_score: number;
  decision: 'irrigate' | 'wait' | 'skip';
  action_hi: string;
  slot_time: string;
  reason_hi: string;
  reason_en: string;
  feeder_id: number;
}

export interface RadarAlert {
  id: string;
  type: string;
  subtype: string;
  title_hi: string;
  title_en: string;
  description_hi: string;
  description_en: string;
  severity: string;
  reports_count: number;
  center_lat: number;
  center_lon: number;
  radius_km: number;
  remedies: { name: string; cost_acre: number; type: string; dosage: string }[];
}

export interface HeatmapPoint {
  lat: number;
  lon: number;
  x_pct: number;
  y_pct: number;
  intensity: number;
}

export interface ShockStep {
  step: number;
  pillar: string;
  pillar_hi: string;
  status: string;
  title_hi: string;
  title_en: string;
  desc_hi: string;
  desc_en: string;
}

export interface ShockResult {
  type: string;
  plot_ids: number[];
  magnitude: number;
  effects: string[];
  steps: ShockStep[];
  kyun: { plot_id: number; farmer_name: string; kyun_hi: string; kyun_en: string }[];
  updated_plots: Plot[];
  plan_summary: {
    village_profit_after: number;
    farmers_worse_off: number;
    max_crop_share: number;
  };
}
