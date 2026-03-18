import { getCard } from '@/lib/api';
import { Card } from '@/components/ui/card';

export default async function CardDetailPage({ params }: { params: { id: string } }) {
  const card = await getCard(params.id);
  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Card #{card.id}</h1>
      <Card>
        <p>Status: {card.status}</p>
        <p>Confirmed catalog ID: {card.confirmed_catalog_id ?? 'Pending'}</p>
        <pre className="overflow-auto text-xs">{JSON.stringify(card.extracted_clues, null, 2)}</pre>
      </Card>
      <Card>
        <h2 className="font-medium">Valuation</h2>
        <pre className="overflow-auto text-xs">{JSON.stringify(card.valuation_snapshot, null, 2)}</pre>
      </Card>
    </div>
  );
}
