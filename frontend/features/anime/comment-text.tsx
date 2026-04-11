const URL_PATTERN = /(https?:\/\/[^\s<>"]+)/g;
const TRAILING_PUNCTUATION = /[),.!?;:]+$/;

function getSafeUrl(candidate: string): string | null {
  try {
    const url = new URL(candidate);
    return url.protocol === 'http:' || url.protocol === 'https:' ? url.toString() : null;
  } catch {
    return null;
  }
}

function splitUrlSuffix(value: string): { url: string; suffix: string } {
  const suffixMatch = value.match(TRAILING_PUNCTUATION);
  if (!suffixMatch) {
    return { url: value, suffix: '' };
  }
  const suffix = suffixMatch[0];
  return { url: value.slice(0, -suffix.length), suffix };
}

export function CommentText({ text }: { text: string }) {
  if (!text) return <span className="text-muted-foreground">—</span>;

  const lines = text.split('\n');
  return (
    <span className="whitespace-pre-wrap break-words text-sm text-muted-foreground">
      {lines.map((line, lineIndex) => {
        const parts = line.split(URL_PATTERN);
        return (
          <span key={`${lineIndex}-${line}`}>
            {parts.map((part, index) => {
              const isUrl = /^https?:\/\//.test(part);
              if (!isUrl) {
                return <span key={`${part}-${index}`}>{part}</span>;
              }

              const { url, suffix } = splitUrlSuffix(part);
              const safeUrl = getSafeUrl(url);
              if (!safeUrl) {
                return <span key={`${part}-${index}`}>{part}</span>;
              }

              return (
                <span key={`${part}-${index}`}>
                  <a href={safeUrl} target="_blank" rel="noopener noreferrer nofollow ugc" className="underline underline-offset-2">
                    {url}
                  </a>
                  {suffix}
                </span>
              );
            })}
            {lineIndex < lines.length - 1 ? <br /> : null}
          </span>
        );
      })}
    </span>
  );
}
