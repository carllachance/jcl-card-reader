import Link from 'next/link';
import { getInventory } from '@/lib/api';
import { Card } from '@/components/ui/card';

export default async function InventoryPage({ searchParams }: { searchParams: { query?: string; status?: string } }) {
  const cards = await getInventory(searchParams.query, searchParams.status);
  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Inventory</h1>
      {cards.map((c) => (
        <Card key={c.id}>
          <Link href={`/cards/${c.id}`} className="font-medium underline">Card #{c.id}</Link>
          <p>Status: {c.status}</p>
          <p>Player: {String(c.extracted_clues?.player_name ?? 'Unknown')}</p>
        </Card>
      ))}
    </div>
  );
}
