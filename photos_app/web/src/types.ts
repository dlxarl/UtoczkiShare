export interface Photo {
  id: number;
  original_name: string;
  file: string;
  created_at: string;
  preview?: string;
  isOwned: boolean;
}