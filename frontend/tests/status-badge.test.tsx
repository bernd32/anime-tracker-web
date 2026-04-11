import { render, screen } from '@testing-library/react';

import { StatusBadge } from '@/features/anime/status-badge';

describe('StatusBadge', () => {
  it('renders completed state', () => {
    render(<StatusBadge status="completed" />);
    expect(screen.getByText('Completed')).toBeInTheDocument();
  });
});
