'use client';

import { useServerInsertedHTML } from 'next/navigation';

export function ThemeScript() {
  useServerInsertedHTML(() => (
    <script
      dangerouslySetInnerHTML={{
        __html: `(function(){var t=localStorage.getItem('theme');if(t==='light'||t==='dark'){if(t==='dark')document.documentElement.classList.add('dark')}else{document.documentElement.classList.add('dark')}})()`,
      }}
    />
  ));

  return null;
}
