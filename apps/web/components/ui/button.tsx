import { ButtonHTMLAttributes } from 'react';

export function Button(props: ButtonHTMLAttributes<HTMLButtonElement>) {
  return <button {...props} className={`rounded bg-slate-900 px-3 py-2 text-white ${props.className ?? ''}`} />;
}
