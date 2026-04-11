import { render, screen } from '@testing-library/react';

import { CommentText } from '@/features/anime/comment-text';

describe('CommentText', () => {
  it('renders plain text and links safely', () => {
    render(<CommentText text={'watch this https://example.com\nnext line'} />);
    expect(document.body).toHaveTextContent('watch this https://example.com');
    expect(screen.getByRole('link', { name: 'https://example.com' })).toHaveAttribute('href', 'https://example.com/');
    expect(screen.getByText('next line')).toBeInTheDocument();
  });

  it('does not include trailing punctuation in links', () => {
    render(<CommentText text="Docs: https://example.com/docs, thanks." />);
    const link = screen.getByRole('link', { name: 'https://example.com/docs' });
    expect(link).toHaveAttribute('href', 'https://example.com/docs');
    expect(document.body).toHaveTextContent('Docs: https://example.com/docs, thanks.');
  });

  it('renders user input as text instead of HTML', () => {
    render(<CommentText text={'<script>alert(1)</script> https://example.com'} />);
    expect(document.body).toHaveTextContent('<script>alert(1)</script> https://example.com');
    expect(document.querySelector('script')).toBeNull();
  });
});
