import { createRoot } from 'react-dom/client';
import { useEffect, useState } from 'react';

function PulsingBadge({ initialCount }: { initialCount: number }) {
  const [pulse, setPulse] = useState(true);

  useEffect(() => {
    const id = setInterval(() => setPulse((p) => !p), 1200);
    return () => clearInterval(id);
  }, []);

  return (
    <span className={`badge notification-badge${pulse ? ' notification-badge-pulse' : ''}`}>
      {initialCount}
    </span>
  );
}

function mountNotificationBadge() {
  const el = document.getElementById('notification-badge');
  if (!el) return;
  const count = Number(el.dataset.count ?? '0');
  if (!count) return;
  const root = createRoot(el);
  root.render(<PulsingBadge initialCount={count} />);
}

document.addEventListener('DOMContentLoaded', () => {
  mountNotificationBadge();
});
