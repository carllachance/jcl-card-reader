import { InventoryCard } from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? 'http://localhost:8000';

export async function getInventory(query?: string, status?: string): Promise<InventoryCard[]> {
  const params = new URLSearchParams();
  if (query) params.set('query', query);
  if (status) params.set('status', status);
  const r = await fetch(`${API_BASE}/api/cards?${params.toString()}`, { cache: 'no-store' });
  return r.json();
}

export async function getCard(id: string): Promise<InventoryCard> {
  const r = await fetch(`${API_BASE}/api/cards/${id}`, { cache: 'no-store' });
  return r.json();
}
