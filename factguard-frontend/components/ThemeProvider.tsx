'use client';

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from 'react';

type Theme = 'light' | 'dark';

interface ThemeContextValue {
  theme: Theme;
  toggleTheme: () => void;
}

const ThemeContext =
  createContext<ThemeContextValue>({
    theme: 'dark',
    toggleTheme: () => {},
  });

export function useTheme() {
  return useContext(ThemeContext);
}

function getInitialTheme(): Theme {
  try {
    const stored =
      localStorage.getItem(
        'theme'
      ) as Theme | null;
    if (
      stored === 'light' ||
      stored === 'dark'
    )
      return stored;
  } catch {
    /* localStorage unavailable */
  }
  return 'dark';
}

export function ThemeProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [theme, setTheme] =
    useState<Theme>(getInitialTheme);

  useEffect(() => {
    document.documentElement.classList.toggle(
      'dark',
      theme === 'dark'
    );
    try {
      localStorage.setItem(
        'theme',
        theme
      );
    } catch {
      /* storage unavailable */
    }
  }, [theme]);

  const toggleTheme =
    useCallback(() => {
      setTheme((prev) =>
        prev === 'light'
          ? 'dark'
          : 'light'
      );
    }, []);

  return (
    <ThemeContext.Provider
      value={{ theme, toggleTheme }}
    >
      {children}
    </ThemeContext.Provider>
  );
}
