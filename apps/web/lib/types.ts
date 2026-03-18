export type CandidateMatch = { catalog_id: number; confidence: number; explanation: string };
export type InventoryCard = {
  id: number;
  status: string;
  front_image_url: string;
  back_image_url: string;
  extracted_clues: Record<string, unknown>;
  candidate_matches: CandidateMatch[];
  confirmed_catalog_id: number | null;
  valuation_snapshot: Record<string, unknown> | null;
  notes: string;
  created_at: string;
  raw_ocr_front: string;
  raw_ocr_back: string;
};
