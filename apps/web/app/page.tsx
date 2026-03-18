'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? 'http://localhost:8000';

export default function UploadPage() {
  const [result, setResult] = useState<any>(null);
  async function onSubmit(formData: FormData) {
    const res = await fetch(`${API_BASE}/api/cards/upload`, { method: 'POST', body: formData });
    setResult(await res.json());
  }

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Upload Baseball Card</h1>
      <Card>
        <form action={onSubmit} className="space-y-3">
          <input type="file" name="front_image" accept="image/*" required className="block" />
          <input type="file" name="back_image" accept="image/*" required className="block" />
          <textarea name="notes" placeholder="notes" className="w-full rounded border p-2" />
          <Button type="submit">Analyze Card</Button>
        </form>
      </Card>
      {result && (
        <Card>
          <p>Status: {result.status}</p>
          <p>Candidates: {result.candidates?.length}</p>
        </Card>
      )}
    </div>
  );
}
