"use client";

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MarkdownContentProps {
  content: string;
  className?: string;
}

export function MarkdownContent({ content, className = '' }: MarkdownContentProps) {
  return (
    <div className={className}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          // Paragraphs
          p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
          
          // Bold text
          strong: ({ children }) => <strong className="font-bold">{children}</strong>,
          
          // Italic text
          em: ({ children }) => <em className="italic">{children}</em>,
          
          // Lists
          ul: ({ children }) => <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>,
          ol: ({ children }) => <ol className="list-decimal list-inside mb-2 space-y-1">{children}</ol>,
          li: ({ children }) => <li className="ml-2">{children}</li>,
          
          // Headings
          h1: ({ children }) => <h1 className="text-lg font-bold mb-2 mt-3 first:mt-0">{children}</h1>,
          h2: ({ children }) => <h2 className="text-base font-bold mb-2 mt-3 first:mt-0">{children}</h2>,
          h3: ({ children }) => <h3 className="text-sm font-bold mb-1 mt-2 first:mt-0">{children}</h3>,
          
          // Code
          code: ({ children, node }) => {
            const isInline = !node?.position;
            return isInline ? (
              <code className="bg-black/10 px-1 py-0.5 rounded text-xs font-mono">{children}</code>
            ) : (
              <code className="block bg-black/10 p-2 rounded text-xs font-mono overflow-x-auto my-2">{children}</code>
            );
          },
          
          // Blockquote
          blockquote: ({ children }) => (
            <blockquote className="border-l-2 border-white/30 pl-3 italic my-2">{children}</blockquote>
          ),
          
          // Links
          a: ({ href, children }) => (
            <a href={href} className="underline hover:opacity-80" target="_blank" rel="noopener noreferrer">
              {children}
            </a>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
