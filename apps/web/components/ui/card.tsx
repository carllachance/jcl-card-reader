import { PropsWithChildren } from 'react';

export function Card({ children }: PropsWithChildren) {
  return <div className="rounded border bg-white p-4 shadow-sm">{children}</div>;
}
