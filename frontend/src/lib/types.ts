// Mirrors the public (answer-free) shapes served by backend/app/services/challenge_store.py.

export const MODES = ["veryeasy", "easy", "medium", "hard", "veryhard", "insane", "lab"] as const;
export type Mode = (typeof MODES)[number];
export type Lang = "en" | "el";

export function isMode(v: string): v is Mode {
  return (MODES as readonly string[]).includes(v);
}

export interface Card {
  title: string;
  what: string;
  formula: string;
  example: string;
  why: string;
}

export interface ChoiceGap {
  mode: "choice";
  options: string[];
  concept: string;
}

export interface TextGap {
  mode: "text";
  concept: string;
  width: number;
}

export type Gap = ChoiceGap | TextGap;

interface QuestionBase {
  id: string;
  section: string;
  q: string;
  card: Card;
  hint_levels: number[];
}

export interface DuoQuestion extends QuestionBase {
  type: "duo";
  prefix: string;
}

export interface BtnsQuestion extends QuestionBase {
  type: "btns";
  options: string[];
}

export interface GapsQuestion extends QuestionBase {
  type: "gaps";
  lang: "python" | "c";
  code: string;
  gaps: Gap[];
}

export interface TermQuestion extends QuestionBase {
  type: "term";
}

export type Question = DuoQuestion | BtnsQuestion | GapsQuestion | TermQuestion;

export interface ModeContent {
  mode: Mode;
  total: number;
  questions: Question[];
  // Lab only: the virtual project the terminal can ls / cat
  files?: Record<string, string>;
  cwd?: string;
  prompt_user?: string;
}

export interface Progress {
  mode: Mode;
  answered: Record<string, boolean>;
  correct_count: number;
  total_score: number;
  completed: boolean;
  completed_at: string | null;
}

export interface LeaderRow {
  rank: number;
  username: string;
  total_score: number;
  total_correct: number;
  total_attempts?: number;
  best_streak?: number;
}

export interface SubmitResult {
  correct: boolean;
  per_gap: boolean[];
  explain: string;
  output: string;
  score_delta: number;
  total_score: number;
  message: string;
  leaderboard: LeaderRow[];
  completed: boolean;
  already_correct: boolean;
}

export interface HintResult {
  gap: number;
  level: number;
  max_level: number;
  hint: string;
  hints_used: number;
  points_if_correct: number;
}

export interface ModeScore {
  best_score: number;
  correct: number;
  attempts: number;
  best_streak: number;
  updated_at: string | null;
}

export interface Me {
  id: number;
  username: string;
  email: string;
  created_at: string;
  last_login: string | null;
  is_admin: boolean;
  stats: { total_score: number; total_correct: number; total_attempts: number; modes_played: number };
  mode_scores: Record<string, ModeScore>;
}
